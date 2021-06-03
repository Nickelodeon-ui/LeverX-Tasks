from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

# Create your models here.

POSITION_CHOICES = [
    ("ST", "Student"),
    ("TE", "Teacher"),
]

class User(AbstractUser):
    age = models.IntegerField(blank=True, null=True)
    position = models.CharField(max_length=10, choices=POSITION_CHOICES)

    def __str__(self):
        return f"This is {self.username} ({self.first_name} {self.last_name}) - {self.position}"

class Course(models.Model):
    title = models.CharField(max_length=30)
    description = models.TextField()
    teacher = models.ManyToManyField(User, related_name="teach_courses")
    student = models.ManyToManyField(User, related_name="stud_courses")

def get_path_by_course_title(instance, filename):
    return settings.MEDIA_ROOT + f"/{instance.course.title}/{filename}"

class Lecture(models.Model):
    theme = models.CharField(max_length=30)
    presentation = models.FileField(upload_to=get_path_by_course_title)
    course = models.ForeignKey(Course, related_name="lectures", on_delete=models.CASCADE)

class Homework(models.Model):
    lecture = models.ForeignKey(Lecture, related_name="homeworks", on_delete=models.CASCADE)
    student = models.ForeignKey(User, related_name="homeworks", on_delete=models.CASCADE)
    homework = models.TextField()
    solution = models.TextField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    mark = models.PositiveIntegerField(null=True, blank=True)

class Comment(models.Model):
    homework = models.ForeignKey(Homework, related_name="comments", on_delete=models.CASCADE)
    text = models.CharField(max_length=255)