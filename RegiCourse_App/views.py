from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib import messages
from RegiCourse_App.models import Students


def master(request):

    return render(request,'master.html')


def home(request):

    return render(request,'home.html')


def logout(request):

    return redirect('login')


def signup(request):

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirmPassword = request.POST.get('confirmPassword')

        if password != confirmPassword:
             messages.error(request, 'Passwords do not match')
             return render(request, 'login.html', {'signup_errors': messages.get_messages(request)})


        if User.objects.filter(email=email).exists():

           messages.error(request, 'Email is already in use')
           return render(request, 'login.html', {'signup_errors': messages.get_messages(request)})

        student = User.objects.create_user(email, email, password)
        student.name = name
        student.save()

        students = Students(student_name=name, email=email, password=password)
        students.save()

        return redirect('home')

    return render(request, 'login.html')


def login(request):
    return render(request, 'login.html')


def authenticate_user(request):

    if request.method == 'POST':
        email = request.POST.get('login-email')
        password = request.POST.get('login-password')

        try:
            user = Students.objects.get(email=email)

            if user.password == password:
                return redirect('home')
            else:
                messages.error(request, 'The email or password is incorrect')
                return render(request, 'login.html', {'login_errors': messages.get_messages(request)})

        except Students.DoesNotExist:
            messages.error(request, 'The email or password is incorrect')
            return render(request, 'login.html', {'login_errors': messages.get_messages(request)})

    return redirect('login')
