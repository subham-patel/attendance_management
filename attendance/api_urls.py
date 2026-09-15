from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.urls import path

from .api_views import AttendanceRecordViewSet, StudentViewSet, SubjectViewSet, TeacherViewSet

router = DefaultRouter()
router.register('students', StudentViewSet, basename='student-api')
router.register('teachers', TeacherViewSet, basename='teacher-api')
router.register('subjects', SubjectViewSet, basename='subject-api')
router.register('attendance', AttendanceRecordViewSet, basename='attendance-api')

urlpatterns = router.urls + [
    # JWT endpoints: POST username/password to obtain access and refresh tokens.
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
