import csv
from pathlib import Path

from django.core.management.base import BaseCommand

from attendance.models import Student, Subject


class Command(BaseCommand):
    help = 'Load students from a CSV file into the database and ensure default subjects exist'

    def add_arguments(self, parser):
        parser.add_argument('--file', default='students_sample.csv', help='Path to the student CSV file')

    def handle(self, *args, **options):
        default_subjects = [
            ('IPS1', 'IPS1'),
            ('FMI1', 'FMI1'),
            ('ITC', 'ITC'),
            ('PPWC', 'PPWC'),
            ('DPOS', 'DPOS'),
            ('CN', 'CN'),
            ('MLC1', 'MLC1'),
        ]

        for code, name in default_subjects:
            Subject.objects.update_or_create(code=code, defaults={'name': name})

        csv_path = Path(options['file'])
        if not csv_path.is_absolute():
            csv_path = Path(__file__).resolve().parents[3] / csv_path
        with csv_path.open(newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            created = 0
            for row in reader:
                regd_no = (row.get('Regd_No') or row.get('regd_no') or '').strip()
                name = (row.get('Name') or row.get('name') or '').strip()
                email = (row.get('Email') or row.get('email') or '').strip()
                roll_no_value = (row.get('roll_No') or row.get('roll_no') or '').strip()
                Student.objects.update_or_create(
                    regd_no=regd_no,
                    defaults={
                        'roll_no': int(roll_no_value) if roll_no_value else None,
                        'name': name,
                        'class_name': (row.get('Class') or row.get('class_name') or '').strip(),
                        'email': email,
                    },
                )
                created += 1

        self.stdout.write(
            self.style.SUCCESS(f'Successfully loaded {created} students and seeded {len(default_subjects)} subjects.')
        )
