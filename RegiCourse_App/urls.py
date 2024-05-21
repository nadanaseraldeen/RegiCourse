from xml.etree.ElementInclude import include

from django.urls import path
from RegiCourse_App import views
from django.contrib.auth import views as auth_views, admin
from .views import course_report



urlpatterns = [
    path('master/', views.master),
    path('home/', views.home, name='home'),
    path('logout/', views.user_logout, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('', views.loginn, name='login'),
    path('authenticate/', views.authenticate_user, name='authenticate'),
    path('courses_info/', views.courses_info, name='courses_info'),
    path('courses/', views.courses, name='courses'),
    path('schedule/', views.schedule, name='schedule'),
    path('addToSchedule/', views.addToSchedule, name='addToSchedule'),
    path('completedPre/', views.completedPre, name='completedPre'),
    path('completedPreAddToSchedule/', views.completedPreAddToSchedule, name='completedPreAddToSchedule'),

    path('admin/course_report/', course_report, name='course_report'),

]