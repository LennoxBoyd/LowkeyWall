from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from .models import Reply
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_protect
import qrcode
from io import BytesIO
from django.http import HttpResponse
from django.urls import reverse

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404

from django.db.models import Count


import json
import requests
import base64

from .models import Confession, Upvote, Quote, Comment, SupportPlan
from .forms import ConfessionForm, MpesaPaymentForm, ContactForm, CommentForm
from .forms import ReplyForm, CommentForm
from django.shortcuts import render, redirect
from .forms import ConfessionForm

# -------------------- API --------------------

from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response


class ConfessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Confession
        fields = '__all__'


@api_view(['GET'])
def get_confessions(request):
    confessions = Confession.objects.all().order_by('-created_at')[:20]
    serializer = ConfessionSerializer(confessions, many=True)
    return Response(serializer.data)


# -------------------- Pages --------------------

from django.contrib.auth import get_user_model
User = get_user_model()


def index(request):
    confessions = Confession.objects.order_by('-created_at')[:6]
    featured_confessions = Confession.objects.filter(is_featured=True).order_by('-created_at')[:3]

    total_confessions = Confession.objects.count()
    total_upvotes = Upvote.objects.count()
    active_users = Upvote.objects.values('session_key').distinct().count()
    quote = Quote.objects.order_by('?').first()

    # ✅ Annotate properly for most upvoted confession
    most_upvoted_confession = (
        Confession.objects
        .annotate(upvote_count=Count('upvotes'))
        .order_by('-upvote_count')
        .first()
    )

    return render(request, 'index.html', {
        'confessions': confessions,
        'featured_confessions': featured_confessions,
        'total_confessions': total_confessions,
        'total_upvotes': total_upvotes,
        'active_users': active_users,
        'quote': quote,
        'most_upvoted_confession': most_upvoted_confession,
    })





def post_confession(request):
    if request.method == 'POST':
        form = ConfessionForm(request.POST)
        if form.is_valid():
            confession = form.save(commit=False)  # don’t save yet

            # ✅ Ensure the session exists
            if not request.session.session_key:
                request.session.create()

            # ✅ Save session_owner
            confession.session_owner = request.session.session_key

            confession.save()

            return redirect('index')  # or wherever you want to go
    else:
        form = ConfessionForm()

    return render(request, 'post_confession.html', {'form': form})



@csrf_exempt
def upvote_confession(request, confession_id):
    if request.method == "POST":
        confession = get_object_or_404(Confession, id=confession_id)

        if not request.session.session_key:
            request.session.create()

        session_key = request.session.session_key

        upvote, created = Upvote.objects.get_or_create(
            confession=confession,
            session_key=session_key
        )

        if not created:
            # If upvote existed → remove it
            upvote.delete()
            # ✅ Update the count field
            confession.upvote_count = confession.upvotes.count()
            confession.save()
            return JsonResponse({
                'status': 'removed',
                'new_count': confession.upvote_count
            })
        else:
            # If new upvote → update count
            confession.upvote_count = confession.upvotes.count()
            confession.save()
            return JsonResponse({
                'status': 'added',
                'new_count': confession.upvote_count
            })

    return HttpResponseBadRequest("Invalid request method.")

def browse_confessions(request):
    confessions = Confession.objects.all()

    # Filter
    topic = request.GET.get('topic')
    if topic:
        confessions = confessions.filter(topic=topic)

    # Sort
    sort = request.GET.get('sort')
    if sort == 'latest':
        confessions = confessions.order_by('-created_at')
    elif sort == 'popular':
        confessions = confessions.annotate(upvote_count=Count('upvotes')).order_by('-upvote_count')

    # Search
    search = request.GET.get('search')
    if search:
        confessions = confessions.filter(Q(message__icontains=search) | Q(topic__icontains=search))

    paginator = Paginator(confessions, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    form = ConfessionForm()
    return render(request, 'browse_confessions.html', {
        'confessions': page_obj,
        'form': form,
    })



from django.shortcuts import render, get_object_or_404, redirect
from .models import Confession, Comment, Reply
from .forms import CommentForm

def confession_detail(request, id):
    confession = get_object_or_404(Confession, id=id)
    comments = Comment.objects.filter(confession=confession).order_by('created_at')
    replies = Reply.objects.filter(confession=confession).order_by('created_at')

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.confession = confession
            if confession.session_owner == request.session.session_key:
                comment.is_author = True
            comment.save()
            return redirect('confession_detail', id=confession.id)
    else:
        form = CommentForm()

    return render(request, 'confession_detail.html', {
        'confession': confession,
        'comments': comments,
        'replies': replies,
        'comment_form': form,
    })

@csrf_protect
def post_reply_to_comment(request, confession_id, comment_id):
    confession = get_object_or_404(Confession, id=confession_id)
    comment = get_object_or_404(Comment, id=comment_id)

    if request.method == 'POST':
        form = ReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.confession = confession
            reply.parent_comment = comment
            reply.is_author = (confession.session_owner == request.session.session_key)  # ✅ CRUCIAL!
            reply.save()
            html = render_to_string('reply_item.html', {'reply': reply}, request=request)
            return JsonResponse({'success': True, 'html': html})
    return JsonResponse({'success': False, 'error': 'Invalid request'})


@csrf_protect
def post_reply_to_reply(request, confession_id, reply_id):
    confession = get_object_or_404(Confession, id=confession_id)
    parent_reply = get_object_or_404(Reply, id=reply_id)

    if request.method == 'POST':
        form = ReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.confession = confession
            reply.parent = parent_reply
            reply.is_author = (
                confession.session_owner == request.session.session_key
                if confession.session_owner and request.session.session_key
                else False
            )
            reply.save()
            print('✅ Saved reply:', reply.id, reply.message)  # ✅ LOG SUCCESS
            html = render_to_string('reply_item.html', {'reply': reply}, request=request)
            return JsonResponse({'success': True, 'html': html})
        else:
            print('❌ FORM ERRORS:', form.errors)  # ✅ LOG FAILURE

    return JsonResponse({'success': False, 'error': 'Invalid request'})


def toggle_upvote(request, confession_id):
    confession = get_object_or_404(Confession, id=confession_id)

    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key  # ✅ FIXED

    upvote, created = Upvote.objects.get_or_create(
        session_key=session_key,
        confession=confession
    )

    if not created:
        upvote.delete()
        confession.upvote_count = max(0, confession.upvote_count - 1)
        confession.save()
        return JsonResponse({'status': 'removed', 'count': confession.upvote_count})

    confession.upvote_count += 1
    confession.save()
    return JsonResponse({'status': 'added', 'count': confession.upvote_count})


# ---------------------- M-PESA Payment ----------------------

def get_access_token():
    consumer_key = settings.MPESA_CONSUMER_KEY
    consumer_secret = settings.MPESA_CONSUMER_SECRET
    auth_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    response = requests.get(auth_url, auth=(consumer_key, consumer_secret))
    return response.json().get('access_token')


@csrf_exempt
def mpesa_pay(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        amount = request.POST.get('amount')

        if not phone or not amount:
            messages.error(request, "Phone and amount required.")
            return redirect('mpesa_pay')

        if not phone.startswith('254') or len(phone) < 12:
            messages.error(request, "Phone must be like 2547XXXXXXXX")
            return redirect('mpesa_pay')

        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        password = base64.b64encode(
            (settings.MPESA_SHORTCODE + settings.MPESA_PASSKEY + timestamp).encode()
        ).decode()

        headers = {
            "Authorization": f"Bearer {get_access_token()}",
            "Content-Type": "application/json"
        }

        payload = {
            "BusinessShortCode": settings.MPESA_SHORTCODE,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone,
            "PartyB": settings.MPESA_SHORTCODE,
            "PhoneNumber": phone,
            "CallBackURL": settings.MPESA_CALLBACK_URL,
            "AccountReference": "LowkeyWall",
            "TransactionDesc": "Premium Support"
        }

        res = requests.post(
            "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
            headers=headers,
            json=payload
        )

        if res.status_code == 200:
            messages.success(request, "STK push sent. Check your phone.")
        else:
            error_info = res.json()
            messages.error(request, f"Payment failed: {error_info.get('errorMessage', 'Unknown error')}")

        return redirect('mpesa_pay')

    return render(request, 'payment.html')


@csrf_exempt
def mpesa_callback(request):
    data = json.loads(request.body)
    print("MPESA CALLBACK JSON:", json.dumps(data, indent=2))
    return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})


# -------------------- Static --------------------

def aboutus_view(request):
    return render(request, 'aboutus.html')


def privacy_policy_view(request):
    return render(request, 'privacy_policy.html')


def terms_view(request):
    return render(request, 'terms.html')


def guidelines_view(request):
    return render(request, 'guidelines.html')


def contact_page(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'contact.html', {'form': ContactForm(), 'success': True})
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})

def learn_more_ads_view(request):
    return render(request, 'learn_more_ads.html')


def help_center(request):
    return render(request, 'help_center.html')   



def my_confessions(request):
    # Make sure the user has a session key
    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key

    # ✅ Filter confessions where session_owner matches this session
    confessions = Confession.objects.filter(session_owner=session_key).order_by('-created_at')

    return render(request, 'my_confessions.html', {'confessions': confessions})

def generate_qr(request, confession_id):
    url = request.build_absolute_uri(reverse('confession_detail', args=[confession_id]))
    img = qrcode.make(url)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return HttpResponse(buffer.getvalue(), content_type="image/png")
   
    
