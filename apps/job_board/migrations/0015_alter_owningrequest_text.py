# Generated by Django 4.2.2 on 2023-08-10 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job_board', '0014_owningrequest_company_owning_requests'),
    ]

    operations = [
        migrations.AlterField(
            model_name='owningrequest',
            name='text',
            field=models.TextField(blank=True, default=None, null=True),
        ),
    ]
