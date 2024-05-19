from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.safestring import mark_safe

from RegiCourse_App.models import *
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


# Register your models here.

#admin.site.register(Courses)

admin.site.register(CourseSchedules)


#admin.site.register(StudentsReg)
#admin.site.register(Students)


admin.site.register(Notification)

"""
class analysis(admin.ModelAdmin):
    list_display = ('course_code', 'course_name', 'instructor_name', 'capacity', 'enrolled_students')

    def enrolled_students(self, obj):
        return StudentsReg.objects.filter(course=obj).count()

admin.site.register(Courses, analysis)
"""

class CoursesAnalysis(admin.ModelAdmin):
    list_display = ('course_code', 'course_name', 'instructor_name', 'capacity', 'enrollment_number', 'enrollment_percentage' )

admin.site.register(Courses, CoursesAnalysis)


class StudentRegi(admin.ModelAdmin):
    list_display = ('student', 'course', 'completed')


admin.site.register(StudentsReg, StudentRegi)


class studentAnalysis(admin.ModelAdmin):
    list_display = ('student_name', 'registered_Courses_Count', 'currently_courses_registered_count')

admin.site.register(Students, studentAnalysis)



class UserAdmin(BaseUserAdmin):
    list_display = ('username','get_groups','is_staff')

    def get_groups(self, obj):
        return ", ".join([group.name for group in obj.groups.all()])

    get_groups.short_description = 'Groups'

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
