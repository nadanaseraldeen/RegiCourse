from django.contrib.auth.hashers import make_password, check_password

from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib import messages

from RegiCourse_App.models import Students, Courses, StudentsReg, Notification


def master(request):

    return render(request,'master.html')



def home(request):
    student_name = request.session.get('student_name')
    notifications = Notification.objects.all()
    return render(request, 'home.html', {'student_name': student_name,'notifications': notifications})


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
        student_id = request.session.get('student_id')
        course_code = request.POST.get('course_code')
        notifications = Notification.objects.all()

        if student_id is None:
            schedule_message = "User not logged in"
        else:
            student = Students.objects.get(student_Id=student_id)
            try:
                course = Courses.objects.get(course_code=course_code)
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
        return render(request, 'courses.html', {'courses': courses, 'schedule_message': schedule_message, 'notifications': notifications})
    else:
        schedule_message = "Invalid add the course"
        return render(request, 'courses.html', {'schedule_message': schedule_message})

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
    notifications = Notification.objects.all()

    if student_id is None:
        return HttpResponse("User not logged in")

    registered_courses = StudentsReg.objects.filter(student__student_Id=student_id, completed=False).select_related('course')
    student_name = request.session.get('student_name')
    return render(request, 'schedule.html', {'registered_courses': registered_courses, 'student_name': student_name,'notifications': notifications})


def completedPre(request):
    student_id = request.session.get('student_id')

    if not student_id:
        return redirect('login')

    notifications = Notification.objects.all()
    try:
        student = Students.objects.get(student_Id=student_id)
    except Students.DoesNotExist:
        return redirect('login')

    completedPreres = Courses.objects.filter(prerequisites__studentsreg__student=student,
                                             prerequisites__studentsreg__completed=True) | \
                      Courses.objects.filter(prerequisites__isnull=True)

    for completedPrere in completedPreres:
            completedPrere.available_spots = completedPrere.capacity - completedPrere.studentsreg_set.count()
    return render(request,'completedPrerequisites.html', {'completedPreres':completedPreres,'notifications':notifications})


def completedPreAddToSchedule(request):
    if request.method == 'POST':
        student_id = request.session.get('student_id')
        course_code = request.POST.get('course_code')
        notifications = Notification.objects.all()

        if student_id is None:
            schedule_message2 = "User not logged in"
        else:
            student = Students.objects.get(student_Id=student_id)
            try:
                course = Courses.objects.get(course_code=course_code)
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
            except Courses.DoesNotExist:
                schedule_message2 = "Course does not exist"

        completedPreres = Courses.objects.filter(prerequisites__studentsreg__student=student, prerequisites__studentsreg__completed=True) | \
                          Courses.objects.filter(prerequisites__isnull=True)

        #    Q(prerequisites__studentsreg__student=student, prerequisites__studentsreg__completed=True) |
         #   Q(prerequisites__isnull=True)
       # ).distinct()



        for completedPrere in completedPreres:
            completedPrere.available_spots = completedPrere.capacity - completedPrere.studentsreg_set.count()

        return render(request, 'completedPrerequisites.html', {
            'completedPreres': completedPreres,
            'schedule_message2': schedule_message2,
            'notifications': notifications
        })
    else:
        schedule_message2 = "Invalid add the course"
        return render(request, 'completedPrerequisites.html', {'schedule_message2': schedule_message2})
