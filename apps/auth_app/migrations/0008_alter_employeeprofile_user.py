# Generated by Django 4.2.1 on 2023-05-28 12:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth_app', '0007_alter_employeeprofile_company_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employeeprofile',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='employee_profile', to=settings.AUTH_USER_MODEL),
        ),
    ]