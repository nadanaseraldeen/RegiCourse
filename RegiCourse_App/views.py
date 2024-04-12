from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect

# Create your views here.

def master(request):

    return render(request,'master.html')

def login(request):

    return render(request,'login.html')

def home(request):

    return render(request,'home.html')

def logout(request):

    return redirect('login')
