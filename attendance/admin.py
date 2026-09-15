from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from import_export.admin import ImportExportModelAdmin

from .models import AttendanceRecord, Student, Subject, TeacherProfile
from .resources import AttendanceRecordResource, StudentResource, SubjectResource


class TeacherAdmin(UserAdmin):
    list_display = ('username', 'get_name', 'email', 'get_employee_id', 'get_subjects')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'teacher_profile__employee_id')
    list_filter = ('is_staff', 'is_active', 'is_superuser')

    @admin.display(description='Name')
    def get_name(self, obj):
        return obj.get_full_name() or obj.username

    @admin.display(description='Employee ID')
    def get_employee_id(self, obj):
        return getattr(getattr(obj, 'teacher_profile', None), 'employee_id', '-')

    @admin.display(description='Assigned Subjects')
    def get_subjects(self, obj):
        codes = list(obj.assigned_subjects.values_list('code', flat=True))
        codes.extend(obj.teaching_subjects.values_list('code', flat=True))
        return ', '.join(sorted(set(codes)))

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('assigned_subjects', 'teaching_subjects')

    def has_module_permission(self, request):
        return request.user.is_superuser


admin.site.unregister(User)
admin.site.register(User, TeacherAdmin)


@admin.register(TeacherProfile)
class TeacherProfileAdmin(ImportExportModelAdmin):
    list_display = ('employee_id', 'user', 'get_email')
    search_fields = ('employee_id', 'user__username', 'user__first_name', 'user__last_name', 'user__email')

    def has_module_permission(self, request):
        return request.user.is_superuser

    @admin.display(description='Email')
    def get_email(self, obj):
        return obj.user.email


@admin.register(Student)
class StudentAdmin(ImportExportModelAdmin):
    resource_class = StudentResource
    list_display = ('roll_no', 'regd_no', 'name', 'class_name', 'email')
    search_fields = ('roll_no', 'regd_no', 'name', 'class_name', 'email')
    list_filter = ('class_name',)

    def has_module_permission(self, request):
        return request.user.is_superuser


@admin.register(Subject)
class SubjectAdmin(ImportExportModelAdmin):
    resource_class = SubjectResource
    list_display = ('code', 'name', 'get_teachers')
    search_fields = ('code', 'name', 'teacher__username', 'teachers__username')
    list_filter = ('teachers', 'teacher')

    @admin.display(description='Teachers')
    def get_teachers(self, obj):
        names = list(obj.teachers.values_list('username', flat=True))
        if obj.teacher_id:
            names.append(obj.teacher.username)
        return ', '.join(sorted(set(names)))

    def has_module_permission(self, request):
        return request.user.is_superuser


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(ImportExportModelAdmin):
    resource_class = AttendanceRecordResource
    list_display = ('date', 'student', 'subject', 'teacher', 'status')
    search_fields = ('student__name', 'student__regd_no', 'subject__code', 'teacher__username')
    list_filter = ('student__class_name', 'subject', 'teacher', 'date', 'status')
    date_hierarchy = 'date'
    list_select_related = ('student', 'subject', 'teacher')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(teacher=request.user)

    def has_module_permission(self, request):
        return request.user.is_authenticated and request.user.is_staff

    def has_add_permission(self, request):
        return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or (obj is None and request.user.is_staff) or (obj and obj.teacher_id == request.user.id)

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser or (obj and obj.teacher_id == request.user.id)

    def get_readonly_fields(self, request, obj=None):
        return ('teacher',) if not request.user.is_superuser else ()

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            obj.teacher = request.user
        super().save_model(request, obj, form, change)
