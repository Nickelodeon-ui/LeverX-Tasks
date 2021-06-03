from rest_framework import permissions

from .models import User

class TeacherStudentPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        user = User.objects.get(username=request.user.username)
        position = user.position
        
        if request.method in permissions.SAFE_METHODS:
            return True

        if view.action in [
            'create',
            'update',
            'partial_update',
            'destroy',
            'add_student',
            'delete_student',
            'add_teacher',
            'completed_homeworks'
        ]:
            return True if position == "TE" else False

    def has_object_permission(self, request, view, obj):
        user = User.objects.get(username=request.user.username)
        position = user.position

        if request.method in permissions.SAFE_METHODS:
            return True

        if view.action in [
            'create',
            'update',
            'partial_update',
            'destroy',
            'add_student',
            'delete_student',
            'add_teacher',
            'completed_homeworks'
        ]:
            return True if position == "TE" else False

class CommentCustomPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        user = User.objects.get(username=request.user.username)
        position = user.position

        if request.method in permissions.SAFE_METHODS:
            return True

        if view.action == 'create':
            return True

        if view.action in [
            'update',
            'partial_update',
            'destroy',
        ]:
            return True if position == "TE" else False

    def has_object_permission(self, request, view, obj):
        user = User.objects.get(username=request.user.username)
        position = user.position

        if request.method in permissions.SAFE_METHODS:
            return True

        if view.action in [
            'create',
            'update',
            'partial_update',
            'destroy',
            'add_student',
            'delete_student',
            'add_teacher',
            'completed_homeworks'
        ]:
            return True if position == "TE" else False
