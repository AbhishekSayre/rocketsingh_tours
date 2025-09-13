from django.contrib import admin
from django.urls import path,include
from . import views

admin.site.site_header = "Rocket Singh Admin"
admin.site.site_title = "Rocket Singh Portal"
admin.site.index_title = "Welcome to Rocket Singh Portal"

urlpatterns = [
    
    path("",views.home,name="home"),
    path("packages/",views.packages,name="packages"),
    path('get-quote/', views.get_quote, name='get_quote'),
    path('login/', views.custom_login, name='login'),
    path('signup/', views.custom_signup, name='signup'),
    path('logout/', views.custom_logout, name='logout'),
    path('personalinfo/', views.personal_info, name='personalinfo'),
    path('update-info/', views.update_personal_info_ajax, name='update_info_ajax'),
    path('upload-photo/', views.upload_profile_photo, name='upload_profile_photo'),
    path('payment/<int:tour_id>/', views.payment_details, name='payment_details'),
    path('booknow/<int:tour_id>/', views.booknow, name='booknow'),
    path('payment-success/<int:booking_id>/', views.payment_success, name='payment_success'),
    path('download-booking/<int:booking_id>/', views.download_booking_pdf, name='download_booking_pdf'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<uidb64>/<token>/', views.reset_password, name='reset_password'),
    path('change-password/', views.change_password, name='change_password'),
    path('mybookings/', views.my_bookings, name='mybookings'),
    path("booking/<int:booking_id>/cancel/", views.cancel_booking, name="cancel_booking"),
    path("accounts/profile-check/", views.profile_check, name="profile-check"),
    path("complete-profile/", views.complete_profile, name="complete_profile"),
    path("oauth/", include("social_django.urls", namespace="social")),
    path('booking/<int:booking_id>/download/', views.download_booking_pdf, name='download_booking_pdf'),





]