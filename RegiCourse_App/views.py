from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.contrib import messages
from RegiCourse_App.models import Students, Courses, StudentsReg
from django.contrib.auth import logout, authenticate


def master(request):

    return render(request,'master.html')



def home(request):
    student_name = request.session.get('student_name')
    return render(request, 'home.html', {'student_name': student_name})


def logout(request):
    request.session.clear()
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

        request.session['student_id'] = student.student_Id

        request.session['student_name'] = student.student_name
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
                request.session['student_id'] = student.student_Id
                request.session['student_name'] = student.student_name
                return redirect('home')
                #return redirect('home')
            else:
                messages.error(request, 'Invalid email or password')
                return render(request, 'login.html', {'login_errors': messages.get_messages(request)})
        except Students.DoesNotExist:
            messages.error(request, 'Invalid email or password')
            return render(request, 'login.html', {'login_errors': messages.get_messages(request)})
    else:
        return render(request, 'login.html')


def courses_info(request):
    return render(request, 'courses.html')


def courses(request):
    querySearch = request.GET.get('searchCou')
    courses = Courses.objects.all()

    if querySearch:
        courses = Courses.objects.filter(course_name__icontains=querySearch) | \
                  Courses.objects.filter(course_code__icontains=querySearch) | \
                  Courses.objects.filter(instructor_name__icontains=querySearch)

    else:
        for course in courses:
           course.available_spots = course.capacity - course.studentsreg_set.count()

    return render(request, 'courses.html', {'courses': courses})



def addToSchedule(request):
    if request.method == 'POST':
        student_id = request.session.get('student_id')
        course_code = request.POST.get('course_code')

        if student_id is None:
            return HttpResponse("User not logged in")

        student = Students.objects.get(student_Id=student_id)

        try:
            course = Courses.objects.get(course_code=course_code)
        except Courses.DoesNotExist:
            return HttpResponse("Course does not exist")

        if StudentsReg.objects.filter(student=student, course__course_code=course.course_code).exists():
            return HttpResponse("Student is already registered for this course")


        if course.availableSpots() <= 0:
            return HttpResponse("No available spots for this course")

        registered_courses = StudentsReg.objects.filter(student=student, completed=False )
        for registered_course in registered_courses:
            if registered_course.course.schedule == course.schedule:
                return HttpResponse("Course schedule clashes with another registered course")

        if course.prerequisites:
            if not prerequisitesCompleted(student, course):
                return HttpResponse("Prerequisite course is not completed")

        registration = StudentsReg(student=student, course=course)
        registration.save()

        return redirect('schedule')
    else:
        return HttpResponse("Invalid add the course")

def prerequisitesCompleted(student, course):
    prereq_course = course.prerequisites

    prereq_registration = StudentsReg.objects.filter(student=student, course=prereq_course).first()

    if not prereq_registration or not prereq_registration.completed:
        return False

    return True

     #prereq_course = course.prerequisites
     #return StudentsReg.objects.filter(student=student, course=prereq_course).exists()

def schedule(request):
    student_id = request.session.get('student_id')

    if student_id is None:
        return HttpResponse("User not logged in")

    registered_courses = StudentsReg.objects.filter(student__student_Id=student_id, completed=False).select_related('course')

    return render(request, 'schedule.html', {'registered_courses': registered_courses})