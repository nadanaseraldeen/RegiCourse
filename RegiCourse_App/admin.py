from django.contrib import admin
from django.urls import path
from RegiCourse_App.models import *
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .views import course_report

admin.site.register(CourseSchedules)
admin.site.register(Notification)


class StudentRegi(admin.ModelAdmin):
    list_display = ('student', 'course', 'completed')


admin.site.register(StudentsReg, StudentRegi)


class coursesReport(admin.ModelAdmin):
    list_display = ('course_code', 'course_name')
    change_list_template = "admin/course_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('course_report/', self.admin_site.admin_view(course_report), name='course-report'),
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['course_report_url'] = 'course-report'
        return super(coursesReport, self).changelist_view(request, extra_context=extra_context)


admin.site.register(Courses, coursesReport)

"""
class coursesReport(admin.ModelAdmin):
    list_display = ('course_code', 'course_name', 'instructor_name', 'capacity', 'enrollment_number', 'enrollment_percentage' )

admin.site.register(Courses, coursesReport)
"""


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



