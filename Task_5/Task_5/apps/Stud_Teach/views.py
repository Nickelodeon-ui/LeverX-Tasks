from django.shortcuts import render

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

from django.shortcuts import get_object_or_404

from .serializers import (
    UserSerializer,
    CourseSerializer,
    LectureSerializer,
    HomeworkSerializer,
    CommentSerializer,
)

from .models import (
    User,
    Course,
    Lecture,
    Homework,
    Comment
)

from .permissions import TeacherStudentPermission, CommentCustomPermission


class StudentViewSet(ModelViewSet):
    queryset = User.objects.filter(position="ST")
    serializer_class = UserSerializer

class TeacherViewSet(ModelViewSet):
    queryset = User.objects.filter(position="TE")
    serializer_class = UserSerializer

class CourseViewSet(ModelViewSet):

    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated, TeacherStudentPermission]

    def get_queryset(self):
        self.user = User.objects.get(username = self.request.user.username)
        user = self.user
        if user.position == "ST":
            qs = self.queryset.filter(student=user)
        else:
            qs = self.queryset.filter(teacher=user)
        return qs
    
    def create(self, request, *args, **kwargs):
        self.user = User.objects.get(username = self.request.user.username)
        user = self.user
        if user.position == "ST":
            return Response("You don't have permission to do that", status.HTTP_403_FORBIDDEN)
        else:
            return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(teacher=self.user, **self.request.data)

    @action(detail=True, methods=['post'], url_path=r'add-student/(?P<student_pk>[^/.]+)')
    def add_student(self, request, pk=None, student_pk=None):
        try:
            pk = int(pk)
            student_pk = int(student_pk)
        except Exception as e:
            return Response("One of the primmary keys is not a number", status.HTTP_400_BAD_REQUEST)
        course = get_object_or_404(self.get_queryset(), pk=pk)
        student = get_object_or_404(User, pk=student_pk)
        if student in course.student.all():
            return Response("This student is already attending this course", status.HTTP_400_BAD_REQUEST)
        course.student.add(student)
        return Response("Student was succesfully added to course", status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'], url_path=r'delete-student/(?P<student_pk>[^/.]+)')
    def delete_student(self, request, pk=None, student_pk=None):
        try:
            pk = int(pk)
            student_pk = int(student_pk)
        except Exception as e:
            return Response("One of the primmary keys is not a number", status.HTTP_400_BAD_REQUEST)
        course = get_object_or_404(self.get_queryset(), pk=pk)
        student = get_object_or_404(course.student.all(), pk=student_pk)
        course.student.remove(student)
        return Response("Student was succesfully deleted from course", status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'], url_path=r'add-teacher/(?P<teacher_pk>[^/.]+)')
    def add_teacher(self, request, pk=None, teacher_pk=None):
        try:
            pk = int(pk)
            teacher_pk = int(teacher_pk)
        except Exception as e:
            return Response("One of the primmary keys is not a number", status.HTTP_400_BAD_REQUEST)
        course = get_object_or_404(self.get_queryset(), pk=pk)
        teacher = get_object_or_404(User, pk=teacher_pk)
        if teacher in course.teacher.all():
            return Response("This teacher is already assigned to this course", status.HTTP_400_BAD_REQUEST)
        course.teacher.add(teacher)
        return Response("Teacher was succesfully added to course", status.HTTP_200_OK)

class LectureViewSet(ModelViewSet):
    queryset = Lecture.objects.all()
    serializer_class = LectureSerializer
    permission_classes = [IsAuthenticated, TeacherStudentPermission]

    def get_queryset(self):
        self.user = User.objects.get(username = self.request.user.username)
        user = self.user
        if user.position == "ST":
            qs = self.queryset.filter(course__student=user)
        else:
            qs = self.queryset.filter(course__teacher=user)
        return qs

    @action(detail=False, methods=['get'], url_path=r'by-course/(?P<course_pk>[^/.]+)')
    def lectures_by_course(self, request, course_pk=None):
        try:
            course_pk = int(course_pk)
        except Exception as e:
            return Response("Primmary key of course is not a number", status.HTTP_400_BAD_REQUEST)
        course = Course.objects.filter(pk=course_pk)
        if not course:
            return Response("There is no course with this pk", status.HTTP_400_BAD_REQUEST)
        course = course.first()
        lectures = self.get_queryset().filter(course=course)
        if not lectures:
            return Response("There are no lectures to this course or you don't attend this course", status.HTTP_400_BAD_REQUEST)
        serializer = LectureSerializer(lectures, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

class HomeworkViewSet(ModelViewSet):
    queryset = Homework.objects.all()
    serializer_class = HomeworkSerializer
    permission_classes = [IsAuthenticated, TeacherStudentPermission]

    def get_queryset(self):
        self.user = User.objects.get(username=self.request.user.username)
        user = self.user
        if user.position == "ST":
            qs = self.queryset.filter(student=user)
        else:
            qs = self.queryset.filter(lecture__course__teacher=user)
        return qs
    
    def update(self, request, *args, **kwargs):
        if request.data.get("mark"):
            homework = self.get_object()
            if not homework.completed:
                return Response("This homework is not completed yet", status.HTTP_403_FORBIDDEN)
        return super(HomeworkViewSet, self).update(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.validated_data.pop("mark", None)
        return super(HomeworkViewSet, self).perform_create(serializer)

    @action(detail=False, methods=['post'], url_path='completed')
    def completed_homeworks(self, request, pk=None):
        homeworks = self.get_queryset().filter(completed=True)
        serializer = HomeworkSerializer(homeworks, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path=r'by-lecture/(?P<lecture_pk>[^/.]+)')
    def homeworks_by_lecture(self, request, lecture_pk=None):
        try:
            lecture_pk = int(lecture_pk)
        except Exception as e:
            return Response("Primmary key of lecture is not a number", status.HTTP_400_BAD_REQUEST)
        lecture = Lecture.objects.filter(pk=lecture_pk)
        if not lecture:
            return Response("There is no lecture with this pk", status.HTTP_400_BAD_REQUEST)
        lecture = lecture.first()
        homeworks = self.get_queryset().filter(lecture=lecture)
        if not homeworks:
            return Response("There are no homeworks to this lecture or you don't attend this course", status.HTTP_400_BAD_REQUEST)
        serializer = HomeworkSerializer(homeworks, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='send-solution', permission_classes=[IsAuthenticated])
    def send_solution(self, request, pk=None):
        try:
            pk = int(pk)
        except Exception as e:
            return Response("Primmary key of homework is not a number", status.HTTP_400_BAD_REQUEST)
        homework = get_object_or_404(self.get_queryset(), pk=pk)
        try:
            solution = request.data.get("solution")
        except Exception as e:
            return Response("There is no solution or you misspelled solution", status.HTTP_400_BAD_REQUEST)
        homework.solution = solution
        homework.completed = True
        homework.save()
        serializer = HomeworkSerializer(homework)
        return Response(serializer.data, status.HTTP_202_ACCEPTED)

class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, CommentCustomPermission]

    def get_queryset(self):
        self.user = User.objects.get(username=self.request.user.username)
        user = self.user
        if user.position == "ST":
            qs = self.queryset.filter(homework__student=user)
        else:
            qs = self.queryset.filter(homework__lecture__course__teacher=user)
        return qs

    def create(self, request, *args, **kwargs):
        self.user = User.objects.get(username=self.request.user.username)
        try:
            homework_pk = request.data.get("homework")
        except Exception as e:
            return Response("You must provide homework to which you want to add comment")

        homework = get_object_or_404(Homework, pk=homework_pk)

        if self.user.position == "ST" and not homework.student == self.user:
            return Response("You are not assigned to this homework", status.HTTP_403_FORBIDDEN)
        return super(CommentViewSet, self).create(request, *args, **kwargs)

