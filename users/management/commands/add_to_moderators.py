from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group


class Command(BaseCommand):
    help = 'Add users to moderators group and set permissions'

    def add_arguments(self, parser):
        parser.add_argument('emails', nargs='+', type=str, help='User emails')

    def handle(self, *args, **options):
        # Создаем или получаем группу модераторов
        moderators_group, created = Group.objects.get_or_create(name='moderators')

        # Добавляем разрешения для модераторов
        content_types = ContentType.objects.filter(app_label='materials')
        permissions = Permission.objects.filter(content_type__in=content_types, codename__in=[
            'view_course', 'change_course', 'view_lesson', 'change_lesson'
        ])

        moderators_group.permissions.set(permissions)

        # Добавляем пользователей в группу
        for email in options['emails']:
            try:
                user = User.objects.get(email=email)
                user.groups.add(moderators_group)
                user.is_staff = True
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully added {email} to moderators group')
                )
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'User with email {email} does not exist')
                )