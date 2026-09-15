import csv
from pathlib import Path

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from attendance.models import Subject, TeacherProfile


class Command(BaseCommand):
    help = 'Generate 7 teacher accounts, save them to teachers.csv, and assign each teacher to a subject.'

    def handle(self, *args, **options):
        subject_codes = ['IPS1', 'FMI1', 'ITC', 'PPWC', 'DPOS', 'CN', 'MLC1']

        for subject_code in subject_codes:
            Subject.objects.update_or_create(code=subject_code, defaults={'name': subject_code})

        candidates = [
            'Aarav', 'Vihaan', 'Ishita', 'Riya', 'Kabir', 'Meera', 'Aditya', 'Aanya',
            'Pranav', 'Diya', 'Yash', 'Sneha', 'Kian', 'Tara', 'Harsh', 'Nisha',
            'Rohan', 'Pooja', 'Dev', 'Sanya'
        ]

        teacher_names = candidates[:7]
        teacher_rows = []

        for index, (teacher_name, subject_code) in enumerate(zip(teacher_names, subject_codes), start=1):
            teacher_id = f'TCH-{index:03d}'
            password = teacher_id
            profile = TeacherProfile.objects.filter(employee_id=teacher_id).select_related('user').first()
            username = slugify(teacher_name)
            if username == '':
                username = f'teacher{index}'

            if profile:
                user = profile.user
                unique_username = user.username
            else:
                unique_username = username
                username_counter = 1
                while User.objects.filter(username=unique_username).exists():
                    username_counter += 1
                    unique_username = f'{username}{username_counter}'
                user = User.objects.create(username=unique_username)

            user.first_name = teacher_name
            user.last_name = 'Teacher'
            user.email = f'{unique_username}@attendance.local'
            user.is_staff = True
            user.is_active = True
            user.is_superuser = False

            user.set_password(password)
            user.save()

            subject = Subject.objects.get(code=subject_code)
            subject.teacher = user
            subject.save()
            subject.teachers.add(user)
            TeacherProfile.objects.update_or_create(user=user, defaults={'employee_id': teacher_id})

            teacher_rows.append({
                'username': unique_username,
                'name': teacher_name,
                'teacher_id': teacher_id,
                'password': password,
                'assigned_subject': subject_code,
            })

        csv_path = Path(__file__).resolve().parents[3] / 'teachers.csv'
        with csv_path.open('w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['username', 'name', 'teacher_id', 'password', 'assigned_subject'])
            writer.writeheader()
            writer.writerows(teacher_rows)

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {len(teacher_rows)} teacher accounts and saved them to {csv_path}.'
            )
        )
