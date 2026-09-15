from django import forms

from .models import AttendanceRecord, Student, TeacherProfile


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ('name', 'regd_no', 'class_name', 'roll_no', 'email')


class TeacherProfileForm(forms.ModelForm):
    class Meta:
        model = TeacherProfile
        fields = ('employee_id',)


class AttendanceRecordForm(forms.ModelForm):
    class Meta:
        model = AttendanceRecord
        fields = ('student', 'subject', 'date', 'status')

    def clean(self):
        cleaned_data = super().clean()
        student = cleaned_data.get('student')
        subject = cleaned_data.get('subject')
        date = cleaned_data.get('date')
        if student and subject and date:
            queryset = AttendanceRecord.objects.filter(student=student, subject=subject, date=date)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise forms.ValidationError('Attendance already exists for this student, subject, and date.')
        return cleaned_data
