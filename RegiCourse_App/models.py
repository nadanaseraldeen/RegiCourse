from django.db import models


class Students(models.Model):

    student_Id = models.AutoField(primary_key=True)
    student_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=50)


class CourseSchedules(models.Model):

    courseSchedule_Id = models.AutoField(primary_key=True)
    days = models.CharField(max_length=30, null=False)
    startTime = models.TimeField(null=False)
    endTime = models.TimeField(null=False)
    roomNo = models.CharField(max_length=30, null=False)


class Courses(models.Model):

    course_code = models.CharField(max_length=20, primary_key=True)
    course_name = models.CharField(max_length=150, null=False)
    description = models.CharField(max_length=300, null=False)
    prerequisites = models.OneToOneField('self', on_delete=models.CASCADE, null=True)
    instructor_name = models.CharField(max_length=150, null=False)
    capacity = models.IntegerField(null=False)
    schedule = models.OneToOneField(CourseSchedules, on_delete=models.CASCADE)


class StudentsReg(models.Model):

    studentReg_Id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Students, on_delete=models.CASCADE)
    course = models.ForeignKey(Courses, on_delete=models.CASCADE)

