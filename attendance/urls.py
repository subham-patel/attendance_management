from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', views.teacher_admin, name='admin'),
    path('attendance/', views.student_attendance, name='student_attendance'),
    path('student/login/', views.student_login, name='student_login'),
    path('student/logout/', views.student_logout, name='student_logout'),
    path('teacher/login/', views.teacher_login, name='teacher_login'),
    path('teacher/logout/', views.teacher_logout, name='teacher_logout'),
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/admin/', views.teacher_admin, name='teacher_admin'),
    path('admin-dashboard/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('teacher/attendance/<str:subject_code>/', views.teacher_subject_attendance, name='teacher_subject_attendance'),
]
