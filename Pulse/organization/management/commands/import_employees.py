import json
from django.core.management.base import BaseCommand
from django.db import transaction
from organization.models import Employee
from organization.serializers import EmployeeSerializer


class Command(BaseCommand):
    help = 'Imports employees from a hierarchical JSON file'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to the json file')

    def handle(self, *args, **options):
        file_path = options['json_file']

        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

            self.stdout.write(self.style.SUCCESS('Starting import...'))

            with transaction.atomic():
                self.process_node(data)

            self.stdout.write(self.style.SUCCESS('Import completed successfully!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Import failed: {str(e)}'))

    def process_node(self, node, supervisor_instance=None):
        """Recursively processes JSON nodes."""

        # Skip the root company node
        if node.get('id') == 'root':
            for child in node.get('children', []):
                self.process_node(child, None)
            return

        # Clean name and prep data
        raw_name = node.get('name', '').replace('\n', ' ')
        clean_name = " ".join(raw_name.split()) # Remove extra whitespace
        name_parts = clean_name.split()

        first_name = name_parts[0] if name_parts else ""
        last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
        email = node.get('email')

        # Fallback username if email is empty
        username = email.split('@')[0] if email else f"emp_{node['id'][:8]}"

        payload = {
            "user": {
                "username": username,
                "password": "InitialPassword123!", # Set a temporary password
                "first_name": first_name,
                "last_name": last_name,
                "email": email
            },
            "supervisor": supervisor_instance.id if supervisor_instance else None
        }

        # Check if employee already exists to prevent duplicates
        existing = Employee.objects.filter(user__email=email).first() if email else None

        if existing:
            serializer = EmployeeSerializer(existing, data=payload, partial=True)
        else:
            serializer = EmployeeSerializer(data=payload)

        if serializer.is_valid():
            employee = serializer.save()
            self.stdout.write(f"Processed: {clean_name}")

            # Recurse into children
            for child in node.get('children', []):
                self.process_node(child, employee)
        else:
            self.stdout.write(self.style.WARNING(f"Skip {clean_name}: {serializer.errors}"))
