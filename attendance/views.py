from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView
from .models import Student, Subject, AttendanceRecord


SUBJECTS = [
    ('IPS1', 'IPS1'),
    ('FMI1', 'FMI1'),
    ('ITC', 'ITC'),
    ('PPWC', 'PPWC'),
    ('DPOS', 'DPOS'),
    ('CN', 'CN'),
    ('MLC1', 'MLC1'),
]


def _build_attendance_summary(attendance_records):
    summary = {}

    for record in attendance_records:
        key = (record.student_id, record.subject_id)
        if key not in summary:
            summary[key] = {
                'student': record.student,
                'subject': record.subject,
                'total_records': 0,
                'attendance_amount': 0,
            }

        summary[key]['total_records'] += 1
        if record.status == 'present':
            summary[key]['attendance_amount'] += 1

    for item in summary.values():
        item['attendance_percentage'] = (
            round((item['attendance_amount'] / item['total_records']) * 100, 2)
            if item['total_records']
            else 0
        )

    return sorted(summary.values(), key=lambda item: (item['student'].regd_no, item['subject'].code))


def home(request):
    return render(request, 'attendance/home.html')


@never_cache
def teacher_login(request):
    if request.user.is_authenticated:
        return redirect('teacher_admin')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('teacher_admin')
    else:
        form = AuthenticationForm()

    return render(request, 'attendance/teacher_login.html', {'form': form})


def teacher_logout(request):
    logout(request)
    return redirect('home')


@never_cache
def student_login(request):
    if request.method == 'POST':
        regd_no = request.POST.get('regd_no', '').strip()
        name = request.POST.get('name', '').strip()

        if not regd_no or not name:
            return render(
                request,
                'attendance/student_login.html',
                {'error': 'Please enter both registration number and name.'},
            )

        student = Student.objects.filter(regd_no=regd_no, name__iexact=name).first()
        if not student:
            registered_student = Student.objects.filter(regd_no=regd_no).first()
            error = (
                'The name does not match this registration number. Please use the name exactly as registered.'
                if registered_student
                else 'Invalid registration number or name. Please try again.'
            )
            return render(
                request,
                'attendance/student_login.html',
                {'error': error},
            )

        request.session['student_id'] = student.id
        return redirect('student_attendance')

    return render(request, 'attendance/student_login.html')


def student_logout(request):
    request.session.pop('student_id', None)
    return redirect('home')


def student_attendance(request):
    student_id = request.session.get('student_id')

    if student_id:
        student = get_object_or_404(Student, id=student_id)
        attendance_records = AttendanceRecord.objects.filter(student=student).select_related('student', 'subject').order_by('subject__code', 'date')
        subjects = Subject.objects.all().order_by('code')

        subject_summary = {}
        for record in attendance_records:
            subject_id = record.subject_id
            if subject_id not in subject_summary:
                subject_summary[subject_id] = {
                    'student': student,
                    'subject': record.subject,
                    'total_records': 0,
                    'attendance_amount': 0,
                }

            subject_summary[subject_id]['total_records'] += 1
            if record.status == 'present':
                subject_summary[subject_id]['attendance_amount'] += 1

        attendance_summary = []
        for subject in subjects:
            item = subject_summary.get(
                subject.id,
                {
                    'student': student,
                    'subject': subject,
                    'total_records': 0,
                    'attendance_amount': 0,
                },
            )
            item['attendance_percentage'] = (
                round((item['attendance_amount'] / item['total_records']) * 100, 2)
                if item['total_records']
                else 0
            )
            attendance_summary.append(item)

        context = {
            'student': student,
            'subjects': subjects,
            'attendance_summary': attendance_summary,
            'is_student_session': True,
        }
        return render(request, 'attendance/student_attendance.html', context)

    regd_no = request.GET.get('regd_no', '').strip()
    selected_subject = request.GET.get('subject', '').strip()

    students = Student.objects.all()
    attendance_records = AttendanceRecord.objects.select_related('student', 'subject').order_by('date', 'student__regd_no')

    if regd_no:
        attendance_records = attendance_records.filter(student__regd_no__icontains=regd_no)
    if selected_subject:
        attendance_records = attendance_records.filter(subject__code=selected_subject)

    subjects = Subject.objects.all()
    attendance_summary = _build_attendance_summary(attendance_records)

    context = {
        'students': students,
        'subjects': subjects,
        'attendance_summary': attendance_summary,
        'selected_regd_no': regd_no,
        'selected_subject': selected_subject,
    }
    return render(request, 'attendance/student_attendance.html', context)


@login_required(login_url='teacher_login')
def teacher_dashboard(request):
    assigned_subjects = Subject.objects.filter(
        Q(teachers=request.user) | Q(teacher=request.user)
    ).distinct().order_by('code')
    teacher_records = AttendanceRecord.objects.filter(
        Q(teacher=request.user) | Q(subject__in=assigned_subjects)
    )
    total_records = teacher_records.count()
    present_records = teacher_records.filter(status='present').count()
    return render(
        request,
        'attendance/teacher_dashboard.html',
        {
            'assigned_subjects': assigned_subjects,
            'teacher_name': request.user.get_full_name() or request.user.username,
            'teacher_id': request.user.id,
            'total_records': total_records,
            'present_percentage': round((present_records / total_records) * 100, 2) if total_records else 0,
        },
    )


@login_required(login_url='teacher_login')
def teacher_admin(request):
    return teacher_dashboard(request)


class AdminDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'attendance/admin_dashboard.html'
    login_url = 'teacher_login'

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        records = AttendanceRecord.objects.all()
        total_records = records.count()
        context.update({
            'total_students': Student.objects.count(),
            'total_teachers': User.objects.filter(is_staff=True, is_active=True).count(),
            'total_records': total_records,
            'present_percentage': round((records.filter(status='present').count() / total_records) * 100, 2) if total_records else 0,
        })
        return context


@login_required(login_url='teacher_login')
def teacher_subject_attendance(request, subject_code):
    subject = get_object_or_404(
        Subject,
        Q(code=subject_code) & (Q(teachers=request.user) | Q(teacher=request.user)),
    )
    students = Student.objects.all().order_by('regd_no')
    subject_records = AttendanceRecord.objects.filter(subject=subject).select_related('student')
    student_summary = {}

    for record in subject_records:
        student_id = record.student_id
        if student_id not in student_summary:
            student_summary[student_id] = {
                'total_records': 0,
                'attendance_amount': 0,
            }

        student_summary[student_id]['total_records'] += 1
        if record.status == 'present':
            student_summary[student_id]['attendance_amount'] += 1

    for student in students:
        summary = student_summary.get(student.id, {'total_records': 0, 'attendance_amount': 0})
        student.total_records = summary['total_records']
        student.attendance_amount = summary['attendance_amount']
        student.attendance_percentage = (
            round((summary['attendance_amount'] / summary['total_records']) * 100, 2)
            if summary['total_records']
            else 0
        )

    if request.method == 'POST':
        attendance_date = request.POST.get('attendance_date', '').strip()
        if not attendance_date:
            messages.error(request, 'Please select an attendance date.')
        else:
            saved = 0
            for student in students:
                status = request.POST.get(f'status_{student.id}', '').strip()
                if status in dict(AttendanceRecord.STATUS_CHOICES):
                    AttendanceRecord.objects.update_or_create(
                        student=student,
                        subject=subject,
                        date=attendance_date,
                        defaults={'status': status, 'teacher': request.user},
                    )
                    saved += 1
            messages.success(request, f'Attendance saved for {subject.code}.')
            return redirect('teacher_dashboard')

    context = {
        'subject': subject,
        'students': students,
        'attendance_date': request.GET.get('attendance_date', ''),
    }
    return render(request, 'attendance/teacher_subject_attendance.html', context)
