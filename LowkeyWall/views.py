from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
import json  # ✅ Make sure this is at the top of views.py

from django.http import JsonResponse, HttpResponseBadRequest
from .models import Confession


from .models import Confession, Upvote, Quote, Comment, SupportPlan
from .forms import ConfessionForm, MpesaPaymentForm, ContactForm, CommentForm

import requests
import base64

# ---------------------- Home ----------------------
# views.py
from django.shortcuts import render, redirect
from .models import Confession
from .forms import ConfessionForm  # you'll create this
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Confession, Upvote
from django.shortcuts import render
from LowkeyWall.models import Confession
from django.db.models import Sum


from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Confession, Upvote
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count
from .models import Confession, Upvote
from django.db.models import Count
from django.shortcuts import render
from .models import Confession, Upvote, Quote

from django.contrib.auth import get_user_model
User = get_user_model()

def index(request):
    confessions = Confession.objects.order_by('-created_at')[:6]
    total_confessions = Confession.objects.count()
    total_upvotes = Upvote.objects.count()
    active_users = User.objects.count()
    quote = Quote.objects.order_by('?').first()

    return render(request, 'index.html', {
        'confessions': confessions,
        'total_confessions': total_confessions,
        'total_upvotes': total_upvotes,
        'active_users': active_users,
        'quote': quote,
    })


    # ✅ Get a random quote BEFORE returning
    quote = Quote.objects.order_by('?').first()

    return render(request, 'index.html', {
        'confessions': confessions,
        'total_confessions': total_confessions,
        'total_upvotes': total_upvotes,
        'active_users': active_users,
        'quote': quote,
    })



def post_confession(request):
    if request.method == 'POST':
        form = ConfessionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')  # redirects to homepage
    else:
        form = ConfessionForm()
    return render(request, 'post_confession.html', {'form': form})

def browse_confessions(request):
    confessions = Confession.objects.all()

    # Filter by topic
    topic = request.GET.get('topic')
    if topic:
        confessions = confessions.filter(topic=topic)

    # Sort
    sort = request.GET.get('sort')
    if sort == 'latest':
        confessions = confessions.order_by('-created_at')
    elif sort == 'popular':
        confessions = confessions.annotate(num_upvotes=models.Count('upvotes')).order_by('-num_upvotes')

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



def confession_detail(request, pk):
    confession = get_object_or_404(Confession, pk=pk)
    comments = Comment.objects.filter(confession=confession).order_by('-created_at')

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.confession = confession
            comment.save()
            return redirect('confession_detail', pk=pk)
    else:
        form = CommentForm()

    return render(request, 'confession_detail.html', {
        'confession': confession,
        'comments': comments,
        'comment_form': form,  # ✅ fix here
    })

# ---------------------- Upvote ----------------------





@csrf_exempt
def upvote_confession(request, confession_id):
    if request.method == "GET":  # or POST if you prefer!
        confession = get_object_or_404(Confession, id=confession_id)

        # Ensure session
        if not request.session.session_key:
            request.session.create()

        session_key = request.session.session_key

        upvote, created = Upvote.objects.get_or_create(
            confession=confession,
            session_key=session_key
        )

        if not created:
            # Remove upvote
            upvote.delete()
            count = confession.upvotes.count()
            return JsonResponse({'status': 'removed', 'count': count})
        else:
            # New upvote
            count = confession.upvotes.count()
            return JsonResponse({'status': 'added', 'count': count})

    return JsonResponse({'error': 'Invalid method'}, status=400)

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
    access_token = response.json().get('access_token')
    return access_token

# ✅ Merge payment_view + mpesa_pay into 1 view
@csrf_exempt
def mpesa_pay(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        amount = request.POST.get('amount')

        if not phone or not amount:
            messages.error(request, "Phone and amount required.")
            return redirect('mpesa_pay')

        if not phone.startswith('254') or len(phone) < 12:
            messages.error(request, "Phone number must be like 2547XXXXXXXX")
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

        print("Payload:", payload)

        res = requests.post(
            "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
            headers=headers,
            json=payload
        )

        if res.status_code == 200:
            mpesa_response = res.json()
            print("M-PESA OK:", mpesa_response)
            messages.success(request, "STK push sent. Check your phone.")
        else:
            error_info = res.json()
            print("M-PESA ERROR:", error_info)
            messages.error(request, f"Payment failed: {error_info.get('errorMessage', 'Unknown error')}")

        return redirect('mpesa_pay')

    return render(request, 'payment.html')



@csrf_exempt
def mpesa_callback(request):
    data = json.loads(request.body)
    print("MPESA CALLBACK JSON:", json.dumps(data, indent=2))
    return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})


# ---------------------- Static Pages ----------------------

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




@csrf_exempt
def upvote_confession(request, confession_id):
    if request.method == "GET":  # Or POST if you want
        confession = get_object_or_404(Confession, id=confession_id)

        # Ensure session key exists
        if not request.session.session_key:
            request.session.create()

        session_key = request.session.session_key

        upvote, created = Upvote.objects.get_or_create(
            confession=confession,
            session_key=session_key
        )

        if not created:
            upvote.delete()
            count = confession.upvotes.count()
            return JsonResponse({'status': 'removed', 'count': count})
        else:
            count = confession.upvotes.count()
            return JsonResponse({'status': 'added', 'count': count})

    return JsonResponse({'error': 'Invalid method'}, status=400)



def learn_more_ads_view(request):
    return render(request, 'learn_more_ads.html')

def help_center(request):
    return render(request, 'help_center.html')
