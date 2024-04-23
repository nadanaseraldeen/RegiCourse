from xml.etree.ElementInclude import include

from django.urls import path
from RegiCourse_App import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('master/', views.master),
    path('home/', views.home, name='home'),
    path('logout/', views.logout, name='logout'),
    path('signup-login/', views.signup, name='signup'),
    path('', views.login, name='login'),
    path('login/', views.authenticate_user, name='authenticate'),
    path('courses_info/', views.courses_info, name='courses_info'),
    path('courses/', views.courses, name='courses'),
    path('schedule/', views.schedule, name='schedule'),
    path('addToSchedule/', views.addToSchedule, name='addToSchedule'),

]
