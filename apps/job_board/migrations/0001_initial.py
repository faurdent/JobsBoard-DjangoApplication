# Generated by Django 4.2.1 on 2023-05-17 10:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='PositionType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Vacancy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('position', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='job_board.positiontype')),
            ],
        ),
        migrations.CreateModel(
            name='CompanyOwnership',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_creator', models.BooleanField(default=False)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='job_board.company')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth_app.employerprofile')),
            ],
        ),
        migrations.AddField(
            model_name='company',
            name='owners',
            field=models.ManyToManyField(through='job_board.CompanyOwnership', to='auth_app.employerprofile'),
        ),
    ]
