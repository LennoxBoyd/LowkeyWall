from django.urls import path
from . import views
from .views import (
    post_confession,
    browse_confessions,
    aboutus_view,
    contact_page,
    confession_detail,
    privacy_policy_view,
    terms_view,
    guidelines_view,
)

urlpatterns = [
    path('', views.index, name='index'),
    path('post/', post_confession, name='post_confession'),
    path('browse/', browse_confessions, name='browse_confessions'),
    path('upvote/<int:confession_id>/', views.upvote_confession, name='upvote_confession'),
    path('confession/<int:confession_id>/', confession_detail, name='confession_detail'),
    path('about/', aboutus_view, name='aboutus'),
    path('contact/', contact_page, name='contact'),
    path('privacy_policy/', privacy_policy_view, name='privacy_policy'),
    path('guidelines/', guidelines_view, name='guidelines'),
    path('terms/', terms_view, name='terms'),

    # MPESA
    path('mpesa/pay/', views.mpesa_pay, name='mpesa_pay'),
    path('mpesa/callback/', views.mpesa_callback, name='mpesa_callback'),

    # Help Center
    path('help/', views.help_center, name='help_center'),

    # Ads info page
    path('learn-more-ads/', views.learn_more_ads_view, name='learn_more_ads'),

    # API endpoint
    
    path('api/confessions/', views.get_confessions, name='api_confessions'),

    path('my_confessions/', views.my_confessions, name='my_confessions'),
   # For replies to top-level comments
   path('reply/comment/<int:confession_id>/<int:comment_id>/', views.post_reply_to_comment, name='post_reply_to_comment'),
   path('reply/reply/<int:confession_id>/<int:reply_id>/', views.post_reply_to_reply, name='post_reply_to_reply'),
   path('confession/<int:confession_id>/qr/', views.generate_qr, name='generate_qr'),
 



]
