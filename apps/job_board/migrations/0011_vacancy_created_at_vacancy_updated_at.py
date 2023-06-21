# Generated by Django 4.2.1 on 2023-06-21 11:12

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('job_board', '0010_vacancy_is_closed_delete_employee'),
    ]

    operations = [
        migrations.AddField(
            model_name='vacancy',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='vacancy',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]