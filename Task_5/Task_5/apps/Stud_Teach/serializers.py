from django.contrib.auth.models import User
from rest_framework import serializers


from .models import (
    User,
    Course,
    Lecture,
    Homework,
    Comment
)

class HomeworkListingField(serializers.RelatedField):
    def to_representation(self, value):
        data = {
            "id": value.pk,
            "homework": value.homework,
            "completed": value.completed,
            "mark": value.mark
        }
        return data

    def to_internal_value(self, data):
        try:
            try:
                obj_id = data
                return Homework.objects.get(id=obj_id)
            except KeyError:
                raise serializers.ValidationError(
                    'id is a required field.'
                )
            except ValueError:
                raise serializers.ValidationError(
                    'id must be an integer.'
                )
        except Homework.DoesNotExist:
            raise serializers.ValidationError(
                'Obj does not exist.'
            )

class StudentListingField(serializers.RelatedField):
    def to_representation(self, value):
        return f"Student (id:{value.pk}, username:{value.username})"

    def to_internal_value(self, data):
        try:
            try:
                obj_id = data
                return User.objects.get(id=obj_id)
            except KeyError:
                raise serializers.ValidationError(
                    'id is a required field.'
                )
            except ValueError:
                raise serializers.ValidationError(
                    'id must be an integer.'
                )
        except User.DoesNotExist:
            raise serializers.ValidationError(
                'Obj does not exist.'
            )

class LectureListingField(serializers.RelatedField):
    def to_representation(self, value):
        data = {
            "id": value.pk,
            "theme": value.theme
        }
        return data

    def to_internal_value(self, data):
        try:
            try:
                obj_id = data
                return Lecture.objects.get(id=obj_id)
            except KeyError:
                raise serializers.ValidationError(
                    'id is a required field.'
                )
            except ValueError:
                raise serializers.ValidationError(
                    'id must be an integer.'
                )
        except Lecture.DoesNotExist:
            raise serializers.ValidationError(
                'Obj does not exist.'
            )

class UserSerializer(serializers.ModelSerializer):    
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name", 
            "last_name", 
            "age", 
            "email", 
            "position", 
            "password"
            ]
        
    def validate_age(self, value):
        if value and value <= 0:
            raise serializers.ValidationError('Age must be above zero')
        else:
            return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class TeacherListingField(serializers.RelatedField):
    def to_representation(self, value):
        return f"Teacher (id:{value.pk}, username:{value.username})"

class CourseSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField()
    description = serializers.CharField()
    teacher = TeacherListingField(many=True, read_only=True)
    student = StudentListingField(many=True, read_only=True)
    
    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "description",
            "teacher",
            "student"
        ]
    
    def create(self, validated_data):
        teacher = validated_data.pop("teacher")
        course = Course.objects.create(**validated_data)
        course.teacher.add(teacher)
        return course

    def update(self, instance, validated_data):
        title = validated_data.get("title")
        description = validated_data.get("description")
        if title:
            instance.title = title
        if description:
            instance.description = description
        instance.save()
        return instance

class LectureSerializer(serializers.ModelSerializer):
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())
   
    class Meta:
        model = Lecture
        fields = ["id", "theme", "presentation", "course"]
        

    def validate_course(self, value):
        """value is a course object"""
        course = Course.objects.filter(pk=value.pk)
        if not course:
            raise serializers.ValidationError('You must provide an existing course')
        return value
    
    def create(self, validated_data):
        return Lecture.objects.create(**validated_data)

class HomeworkSerializer(serializers.ModelSerializer):
    lecture = LectureListingField(queryset=Lecture.objects.all())
    student = StudentListingField(queryset=User.objects.filter(position="ST"))
    completed = serializers.BooleanField(read_only=True)

    class Meta:
        model = Homework
        fields = ["id", "lecture", "student", "homework", "solution", "completed", "mark"]

    def validate_lecture(self, value):
        """value is a lecture object"""
        lecture = Lecture.objects.filter(pk=value.pk)
        if not lecture:
            raise serializers.ValidationError('You must provide an existing course')
        return value

    def validate_student(self, value):
        """value is a student object"""
        student = User.objects.filter(pk=value.pk, position="ST")
        if not student:
            raise serializers.ValidationError('You must provide an existing course')
        return value

class CommentSerializer(serializers.ModelSerializer):
    homework = HomeworkListingField(queryset=Homework.objects.all())

    class Meta:
        model = Comment
        fields = ["id", "homework", "text"]

    def validate_homework(self, value):
        """value is a homework object"""
        homework = Homework.objects.filter(pk=value.pk)
        if not homework:
            raise serializers.ValidationError('You must provide an existing homework')
        # if not homework.first().mark:
        #     raise serializers.ValidationError('There is no mark to this homework')
        return value
