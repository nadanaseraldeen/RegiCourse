from django.urls import path
from RegiCourse_App import views

urlpatterns = [
    path('master/', views.master),
    path('', views.home, name='home'),
    path('logout/', views.logout, name='logout'),
    path('signup-login/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('authenticate/', views.authenticate_user, name='authenticate'),
    path('courses', views.courses, name='courses_info'),

]
