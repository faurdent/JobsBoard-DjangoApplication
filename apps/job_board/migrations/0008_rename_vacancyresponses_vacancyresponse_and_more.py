# Generated by Django 4.2.1 on 2023-05-23 14:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('job_board', '0007_alter_vacancyresponses_user_profile_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='VacancyResponses',
            new_name='VacancyResponse',
        ),
        migrations.AlterField(
            model_name='vacancyresponse',
            name='user_profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='left_responses', to=settings.AUTH_USER_MODEL),
        ),
    ]
