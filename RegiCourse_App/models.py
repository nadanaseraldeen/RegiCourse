from django.db import models


class Students(models.Model):

    student_Id = models.AutoField(primary_key=True)
    student_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)


class CourseSchedules(models.Model):

    courseSchedule_Id = models.AutoField(primary_key=True)
    days = models.CharField(max_length=30, null=False)
    startTime = models.TimeField(null=False)
    endTime = models.TimeField(null=False)
    roomNo = models.CharField(max_length=30, null=False)

    def __str__(self):
        return f"{self.courseSchedule_Id}"


class Courses(models.Model):

    course_code = models.CharField(max_length=20, primary_key=True)
    course_name = models.CharField(max_length=150, null=False)
    description = models.CharField(max_length=300, null=False)
    prerequisites = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    instructor_name = models.CharField(max_length=150, null=False)
    capacity = models.IntegerField(null=False)
    schedule = models.ForeignKey(CourseSchedules, on_delete=models.CASCADE, blank=True)

    def __str__(self):
        return f"{self.course_name}"

    def availableSpots(self):
        registered_count = self.studentsreg_set.count()
        return self.capacity - registered_count


class StudentsReg(models.Model):

    studentReg_Id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Students, on_delete=models.CASCADE)
    course = models.ForeignKey(Courses, on_delete=models.CASCADE)

