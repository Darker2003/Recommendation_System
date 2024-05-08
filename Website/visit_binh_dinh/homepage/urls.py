from django.urls import path
from django.contrib.staticfiles.urls import static

from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('page/<int:page>/', views.homepage, name='homepage_page'),
    path('login/', views.log_in, name='log_in'),
    path('signup/', views.signup, name='signup'),
    path('profile/', views.profile, name='profile'),
    path('signup/signup_complete/', views.signup_complete, name='signup_complete'),
    path('signup/signup_register/', views.signup_register, name='signup_register'),
    path('login/login_check/', views.log_in_check, name='log_in_check'),
    path('login/login_complete/', views.log_in_complete, name='log_in_complete'),
    path('logout/', views.log_out, name='log_out'),
    path('place/<slug:slug>/', views.location_detail, name='location_detail'),
    path('search/', views.search_request, name='search'),
]
