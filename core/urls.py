from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Main home page (Doctor list & search)
    path('', views.home, name='home'),

    # Doctor details & profile page
    path('doctor/<int:doctor_id>/', views.doctor_profile, name='doctor_profile'),

    # Sign up for a user (account)
    path('signup/', views.signup, name='signup'),

    # Register as Doctor (after signup)
    path('register/', views.register_doctor, name='register_doctor'),

    # Logged-in Doctor can edit their profile
    path('doctor/edit/', views.edit_doctor, name='edit_doctor'),

    # Login/Logout
    path('login/', views.doctor_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # Doctor connections: send & accept
    path('connect/<int:doctor_id>/', views.send_connection_request, name='send_connection_request'),
    path('accept/<int:conn_id>/', views.accept_connection_request, name='accept_connection_request'),

    # Chat between Doctors
    path('chat/<int:doctor_id>/', views.chat, name='chat'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
