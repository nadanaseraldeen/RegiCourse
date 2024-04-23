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
    return render(request, 'home.html')


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
                return redirect('home')
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


def schedule(request):
    if request.user.is_authenticated:
        user_id = request.user.id  # Get the user's ID
        scheduled_courses = StudentsReg.objects.filter(student_Id=user_id)
        return render(request, 'schedule.html', {'scheduled_courses': scheduled_courses})
    else:
        # Handle the case where the user is not authenticated
        return render(request, 'schedule.html', {'scheduled_courses': []})


def addToSchedule(request):
    if request.method == 'POST':
        # Get the student ID from the session
        student_id = request.session.get('student_id')

        if student_id is None:
            return HttpResponse("User not logged in")

        # Retrieve the student object based on the ID
        student = Students.objects.get(student_Id=student_id)

        # Assuming the course_code is passed as part of the request POST data
        course_code = request.POST.get('course_code')

        # Query the Courses model based on the course_code
        try:
            course = Courses.objects.get(course_code=course_code)
        except Courses.DoesNotExist:
            return HttpResponse("Course with this code does not exist")

        # Check if the course is already in the student's schedule
        if StudentsReg.objects.filter(student=student, course__schedule=course.schedule).exists():
            return HttpResponse("Student is already registered for a course at this time")

        # Check if the course has any prerequisites
        if course.prerequisites:
            # Check if the student has completed the prerequisites
            if not meets_prerequisites(student, course):
                return HttpResponse("Student has not completed the prerequisites for this course")

        # Check if the course has available spots
        if course.availableSpots() <= 0:
            return HttpResponse("No available spots for this course")

        # Check for course clashes with other registered courses
        registered_courses = StudentsReg.objects.filter(student=student)
        for registered_course in registered_courses:
            if registered_course.course.schedule == course.schedule:
                return HttpResponse("Course schedule clashes with another registered course")

        # Create a new instance of StudentsReg
        registration = StudentsReg(student=student, course=course)
        # Save the registration to the database
        registration.save()

        return redirect('schedule')
    else:
        return HttpResponse("Invalid request method")

def meets_prerequisites(request, student, course):
    # Retrieve the prerequisite course code
    prerequisite_course_code = course.prerequisites

    # If the course has no prerequisite, the student meets it by default
    if not prerequisite_course_code:
        return True

    # Retrieve the prerequisite course object
    try:
        prerequisite_course = Courses.objects.get(course_code=prerequisite_course_code)
    except Courses.DoesNotExist:
        # If the prerequisite course doesn't exist, the student doesn't meet the prerequisite
        return False

    # Check if the student is registered for the prerequisite course
    return StudentsReg.objects.filter(student=student, course=prerequisite_course).exists()
