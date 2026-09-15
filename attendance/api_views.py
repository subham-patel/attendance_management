from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import AttendanceRecord, Student, Subject
from .permissions import AttendanceOwnerOrAdmin, IsAdminOrReadOnly
from .serializers import AttendanceRecordSerializer, StudentSerializer, SubjectSerializer, TeacherSerializer


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all().order_by('regd_no')
    serializer_class = StudentSerializer
    permission_classes = (IsAdminOrReadOnly,)
    search_fields = ('name', 'regd_no', 'class_name', 'email')
    filterset_fields = ('class_name',)


class TeacherViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.filter(is_staff=True, is_active=True).select_related('teacher_profile').prefetch_related('assigned_subjects')
    serializer_class = TeacherSerializer
    permission_classes = (IsAuthenticated,)


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all().prefetch_related('teachers')
    serializer_class = SubjectSerializer
    permission_classes = (IsAdminOrReadOnly,)


class AttendanceRecordViewSet(viewsets.ModelViewSet):
    queryset = AttendanceRecord.objects.select_related('student', 'teacher', 'subject').all()
    serializer_class = AttendanceRecordSerializer
    permission_classes = (AttendanceOwnerOrAdmin,)
    filterset_fields = ('student', 'teacher', 'subject', 'date', 'status')

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(Q(teacher=self.request.user) | Q(subject__teachers=self.request.user) | Q(subject__teacher=self.request.user)).distinct()

    def perform_update(self, serializer):
        if not self.request.user.is_staff and serializer.instance.teacher_id != self.request.user.id:
            self.permission_denied(self.request, message='Teachers may edit only attendance they created.')
        serializer.save()
