from django.urls import path
from . import views
from .views import (
    post_confession,
    # delete_confession,
    browse_confessions,
    toggle_upvote,
    aboutus_view,
    contact_page,
    confession_detail,
    privacy_policy_view,
    terms_view,
    guidelines_view,
)
from django.contrib import admin


urlpatterns = [
    # Anonymous homepage
    path('', views.index, name='index'),

    # Confession-related
    path('post/', post_confession, name='post_confession'),
    # path('delete_confession/<int:pk>/', delete_confession, name='delete_confession'),
    path('browse/', browse_confessions, name='browse_confessions'),
    path('upvote/<int:confession_id>/', toggle_upvote, name='toggle_upvote'),
    path('upvote/<int:pk>/', views.upvote_confession, name='upvote_confession'),
    path('upvote/<int:confession_id>/', views.upvote_confession, name='upvote_confession'),


    path('upvote/', views.upvote_confession, name='upvote_confession'),
    path('confession/<int:pk>/', confession_detail, name='confession_detail'),

    # Static Pages
    path('about/', aboutus_view, name='aboutus'),
    path('contact/', contact_page, name='contact'),
    path('privacy_policy/', privacy_policy_view, name='privacy_policy'),
    path('guidelines/', guidelines_view, name='guidelines'),
    path('terms/', views.terms_view, name='terms'),

    # MPESA
    path('mpesa/pay/', views.mpesa_pay, name='mpesa_pay'),
    path('mpesa/callback/', views.mpesa_callback, name='mpesa_callback'),
    path('help/', views.help_center, name='help_center'),

    
    
    
    path('learn-more-ads/', views.learn_more_ads_view, name='learn_more_ads'),

    
]

