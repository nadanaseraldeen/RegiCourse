from django.urls import  path

from RegiCourse_App import views

urlpatterns = [
    path('master/', views.master),
    path('login/', views.login, name='login'),
    path('home/', views.home),
    path('logout/', views.logout, name='logout'),
]