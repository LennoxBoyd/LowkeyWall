from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Confession, ContactMessage
from .models import Confession, Comment
from .models import Confession


# ✅ Full topic list used across forms and models
TOPIC_CHOICES = [
    ('Love', 'Love'),
    ('Career', 'Career'),
    ('Life', 'Life'),
    ('Family', 'Family'),
    ('School', 'School'),
    ('Other', 'Other'),
    ('Mental Health', 'Mental Health'),
    ('Friendship', 'Friendship'),
    ('Finance', 'Finance'),
    ('Addiction', 'Addiction'),
    ('Loneliness', 'Loneliness'),
    ('Relationships', 'Relationships'),
    ('Spirituality', 'Spirituality'),
    ('Success', 'Success'),
    ('Failure', 'Failure'),
    ('Secrets', 'Secrets'),
    ('Other', 'Other'),
]

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'placeholder': 'Write a response...',
                'rows': 2,
                'class': 'w-full p-3 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none'
            })
        }




class MpesaPaymentForm(forms.Form):
    phone_number = forms.CharField(label="Phone Number", max_length=15, widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-2 border border-gray-300 rounded focus:ring-primary focus:border-primary',
        'placeholder': '07XX XXX XXX'
    }))
    amount = forms.DecimalField(label="Amount (KES)", min_value=1, widget=forms.NumberInput(attrs={
        'class': 'w-full px-4 py-2 border border-gray-300 rounded focus:ring-primary focus:border-primary',
        'placeholder': '500'
    }))


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full p-2 border rounded', 'placeholder': 'Your Name'}),
            'email': forms.EmailInput(attrs={'class': 'w-full p-2 border rounded', 'placeholder': 'Your Email'}),
            'message': forms.Textarea(attrs={'class': 'w-full p-2 border rounded', 'placeholder': 'Your Message'}),
        }



# forms.py




class ConfessionForm(forms.ModelForm):
    class Meta:
        model = Confession
        fields = ['topic', 'message', 'feeling', 'anonymous', 'ai_response_requested']
        widgets = {
            'message': forms.Textarea(attrs={
                'placeholder': 'Write your confession here...',
                'class': 'w-full h-48 bg-white/5 border border-white/10 rounded-lg p-4 focus:outline-none focus:border-primary resize-none text-white'
            }),
            'feeling': forms.RadioSelect(),
        }

    def __init__(self, *args, **kwargs):
        super(ConfessionForm, self).__init__(*args, **kwargs)

        # ✅ Remove "---------" by disabling empty_label on ChoiceField
        self.fields['topic'].empty_label = None

        # Optional: styling for topic select field
        self.fields['topic'].widget.attrs.update({
            'class': 'w-full px-4 py-2 bg-gray-800 border border-white/10 rounded focus:outline-none focus:border-primary text-white'
        })

    






