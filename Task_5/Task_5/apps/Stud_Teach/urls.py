from django.urls import path

from rest_framework import routers

from .views import (
    StudentViewSet,
    TeacherViewSet,
    CourseViewSet,
    LectureViewSet,
    HomeworkViewSet,
    CommentViewSet
)

router = routers.SimpleRouter()
router.register(r'students', StudentViewSet)
router.register(r'teachers', TeacherViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'lectures', LectureViewSet)
router.register(r'homeworks', HomeworkViewSet)
router.register(r'comments', CommentViewSet)
urlpatterns = router.urls
