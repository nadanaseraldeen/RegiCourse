from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password, check_password

from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from RegiCourse_App.models import Students, Courses, StudentsReg, Notification


def master(request):

    return render(request,'master.html')


@login_required
def home(request):
    user_id = request.session.get('user_id')
    student = Students.objects.get(user=request.user)
    notifications = Notification.objects.all()
    return render(request, 'home.html', {'student_name': student, 'notifications': notifications})


def user_logout(request):

    if request.user:
       logout(request)
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

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email is already in use')
            return render(request, 'login.html', {'signup_errors': messages.get_messages(request)})

        user = User.objects.create(username=email, email=email)
        user.set_password(password)
        user.save()
        student = Students.objects.create(student_name=name, email=email, user=user)

        return redirect('login')
    return render(request, 'login.html')


def loginn(request):
    return render(request, 'login.html')


def authenticate_user(request):
    if request.method == 'POST':
        email = request.POST.get('login-email')
        password = request.POST.get('login-password')
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid email or password')
        return render(request, 'login.html', {'login_errors': messages.get_messages(request)})

    return render(request, 'login.html')

def courses_info(request):
    return render(request, 'courses.html')

@login_required
def courses(request):
    querySearch = request.GET.get('searchCou')
    courses = Courses.objects.all()
    notifications = Notification.objects.all()


    if querySearch:
        courses = Courses.objects.filter(course_name__icontains=querySearch) | \
                  Courses.objects.filter(course_code__icontains=querySearch) | \
                  Courses.objects.filter(instructor_name__icontains=querySearch)

    else:
        for course in courses:
           course.available_spots = course.capacity - course.studentsreg_set.count()

    return render(request, 'courses.html', {'courses': courses, 'notifications': notifications})


def addToSchedule(request):
    if request.method == 'POST':
        course_code = request.POST.get('course_code')
        notifications = Notification.objects.all()

        if not request.user.is_authenticated:
            schedule_message = "User not logged in"
        else:
            try:
                course = Courses.objects.get(course_code=course_code)
                student = request.user.students

                available_spots = course.capacity - course.studentsreg_set.count()

                if StudentsReg.objects.filter(student=student, course__course_code=course.course_code).exists():
                    schedule_message = "Student is already registered for this course"
                elif available_spots <= 0:
                    schedule_message = "No available spots for this course"
                elif StudentsReg.objects.filter(student=student, completed=False,
                                                course__schedule=course.schedule).exists():
                    schedule_message = "Course schedule clashes with another registered course"
                elif course.prerequisites and not prerequisitesCompleted(student, course):
                    schedule_message = "Prerequisite course is not completed"
                else:
                    registration = StudentsReg(student=student, course=course)
                    registration.save()
                    return redirect('schedule')
            except Courses.DoesNotExist:
                schedule_message = "Course does not exist"

        courses = Courses.objects.all()
        for course in courses:
            course.available_spots = course.capacity - course.studentsreg_set.count()
        return render(request, 'courses.html',
                      {'courses': courses, 'schedule_message': schedule_message, 'notifications': notifications})
    else:
        schedule_message = "Invalid add the course"
        return render(request, 'courses.html', {'schedule_message': schedule_message})


def prerequisitesCompleted(student, course):
    """
    if course.prerequisites:
        prereq_registration = StudentsReg.objects.filter(student=student, course=course.prerequisites).first()
        return prereq_registration and prereq_registration.completed
    else:
        return True
    """
    prereq_course = course.prerequisites

    prereq_registration = StudentsReg.objects.filter(student=student, course=prereq_course).first()

    if not prereq_registration or not prereq_registration.completed:
        return False

    return True

     #prereq_course = course.prerequisites
     #return StudentsReg.objects.filter(student=student, course=prereq_course).exists()


@login_required
def schedule(request):
    if not request.user.is_authenticated:
        return HttpResponse("User not logged in")

    student = request.user.students
    registered_courses = StudentsReg.objects.filter(student=student, completed=False).select_related('course')
    student_name = student.student_name if student else None
    notifications = Notification.objects.all()

    return render(request, 'schedule.html', {'registered_courses': registered_courses, 'student_name': student_name, 'notifications': notifications})
@login_required
def completedPre(request):
    if not request.user.is_authenticated:
        return HttpResponse("User not logged in")

    try:
        student = request.user.students
    except Students.DoesNotExist:
        return HttpResponse("Student not found for this user")

    notifications = Notification.objects.all()

    completedPreres = Courses.objects.filter(prerequisites__studentsreg__student=student, prerequisites__studentsreg__completed=True) | Courses.objects.filter(prerequisites__isnull=True)

    for completedPrere in completedPreres:
        completedPrere.available_spots = completedPrere.capacity - completedPrere.studentsreg_set.count()

    return render(request, 'completedPrerequisites.html', {'completedPreres': completedPreres,'notifications': notifications})

def completedPreAddToSchedule(request):
    if request.method == 'POST':
        course_code = request.POST.get('course_code')
        notifications = Notification.objects.all()

        if not request.user.is_authenticated:
            schedule_message2 = "User not logged in"
        else:
            try:
                course = Courses.objects.get(course_code=course_code)
                student = request.user.students

                available_spots = course.capacity - course.studentsreg_set.count()

                if StudentsReg.objects.filter(student=student, course__course_code=course.course_code).exists():
                    schedule_message2 = "Student is already registered for this course"
                elif available_spots <= 0:
                    schedule_message2 = "No available spots for this course"
                elif StudentsReg.objects.filter(student=student, completed=False,
                                                course__schedule=course.schedule).exists():
                    schedule_message2 = "Course schedule clashes with another registered course"
                else:
                    registration = StudentsReg(student=student, course=course)
                    registration.save()
                    return redirect('schedule')

                completedPreres = Courses.objects.filter(prerequisites__studentsreg__student=student, prerequisites__studentsreg__completed=True) | Courses.objects.filter(prerequisites__isnull=True)

                for completedPrere in completedPreres:
                    completedPrere.available_spots = completedPrere.capacity - completedPrere.studentsreg_set.count()

                return render(request, 'completedPrerequisites.html', {
                    'completedPreres': completedPreres,
                    'schedule_message2': schedule_message2,
                    'notifications': notifications
                })

            except Courses.DoesNotExist:
                schedule_message2 = "Course not found"

    else:
        schedule_message2 = "Invalid request to add the course"

    return render(request, 'completedPrerequisites.html', {'schedule_message2': schedule_message2})