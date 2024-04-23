from django.contrib import admin

from RegiCourse_App.models import Courses, CourseSchedules, Students, StudentsReg

# Register your models here.

admin.site.register(Courses)

admin.site.register(CourseSchedules)

admin.site.register(Students)

admin.site.register(StudentsReg)