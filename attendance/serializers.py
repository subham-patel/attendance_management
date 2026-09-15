from django.contrib.auth.models import User
from rest_framework import serializers

from .models import AttendanceRecord, Student, Subject, TeacherProfile


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ('id', 'name', 'regd_no', 'class_name', 'roll_no', 'email')


class TeacherSerializer(serializers.ModelSerializer):
    employee_id = serializers.CharField(source='teacher_profile.employee_id', read_only=True)
    subjects = serializers.SlugRelatedField(many=True, read_only=True, slug_field='code', source='assigned_subjects')

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'employee_id', 'subjects')


class SubjectSerializer(serializers.ModelSerializer):
    teachers = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all())

    class Meta:
        model = Subject
        fields = ('id', 'code', 'name', 'teachers')


class AttendanceRecordSerializer(serializers.ModelSerializer):
    teacher_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = AttendanceRecord
        fields = ('id', 'student', 'teacher', 'teacher_name', 'subject', 'date', 'status')
        read_only_fields = ('teacher',)

    def get_teacher_name(self, obj):
        if not obj.teacher:
            return None
        return obj.teacher.get_full_name() or obj.teacher.username

    def create(self, validated_data):
        validated_data['teacher'] = self.context['request'].user
        return super().create(validated_data)
