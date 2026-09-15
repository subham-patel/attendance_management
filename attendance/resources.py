from import_export import resources

from .models import AttendanceRecord, Student, Subject, TeacherProfile


class StudentResource(resources.ModelResource):
    class Meta:
        model = Student
        import_id_fields = ('regd_no',)
        fields = ('name', 'regd_no', 'class_name', 'roll_no', 'email')


class TeacherProfileResource(resources.ModelResource):
    class Meta:
        model = TeacherProfile
        import_id_fields = ('employee_id',)
        fields = ('employee_id', 'user__username', 'user__first_name', 'user__last_name', 'user__email')


class SubjectResource(resources.ModelResource):
    class Meta:
        model = Subject
        import_id_fields = ('code',)
        fields = ('code', 'name')


class AttendanceRecordResource(resources.ModelResource):
    class Meta:
        model = AttendanceRecord
        import_id_fields = ('student', 'subject', 'date')
        fields = ('student', 'teacher', 'subject', 'date', 'status')
