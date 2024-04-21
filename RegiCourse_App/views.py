from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib import messages
from RegiCourse_App.models import Students, Courses
from django.contrib.auth import logout



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

        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters long')
            return render(request, 'login.html', {'signup_errors': messages.get_messages(request)})
        if not any(char.isalpha() for char in password):
            messages.error(request, 'Password must contain at least one letter')
            return render(request, 'login.html', {'signup_errors': messages.get_messages(request)})

        if password != confirmPassword:
             messages.error(request, 'Passwords do not match')
             return render(request, 'login.html', {'signup_errors': messages.get_messages(request)})


        if Students.objects.filter(email=email).exists():

           messages.error(request, 'Email is already in use')
           return render(request, 'login.html', {'signup_errors': messages.get_messages(request)})

        hashed_password = make_password(password)
        student = Students(student_name=name, email=email, password=hashed_password)
        student.save()

        return redirect('home')

    return render(request, 'login.html')


def login(request):
    return render(request, 'login.html')


def authenticate_user(request):

    if request.method == 'POST':
        email = request.POST.get('login-email')
        password = request.POST.get('login-password')

        try:
            student = Students.objects.get(email=email)

            if check_password(password, student.password):
                return redirect('home')
            else:
                messages.error(request, 'The email or password is incorrect')
                return render(request, 'login.html', {'login_errors': messages.get_messages(request)})

        except Students.DoesNotExist:
            messages.error(request, 'The email or password is incorrect')
            return render(request, 'login.html', {'login_errors': messages.get_messages(request)})

    return redirect('login')

def courses_info(request):
    return render(request, 'courses.html')

def courses(request):
    query = request.GET.get('q')
    courses = Courses.objects.all()

    if query:
        courses = Courses.objects.filter(course_name__icontains=query) | \
                  Courses.objects.filter(course_code__icontains=query) | \
                  Courses.objects.filter(instructor_name__icontains=query)

    else:
        for course in courses:
           course.available_spots = course.capacity - course.studentsreg_set.count()
        courses = Courses.objects.all()

    return render(request, 'courses.html', {'courses': courses})
