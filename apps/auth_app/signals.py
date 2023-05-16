from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.auth_app.models import Employer, JobSeeker, EmployerProfile, JobSeekerProfile


@receiver(post_save, sender=Employer)
def create_employer_profile(sender: Employer, instance: Employer, created: bool, **kwargs):
    if created and instance.account_type == "EMPLOYER":
        EmployerProfile.objects.create(user=instance)


@receiver(post_save, sender=JobSeeker)
def create_job_seeker_profile(sender: JobSeeker, instance: JobSeeker, created: bool, **kwargs):
    if created and instance.account_type == "JOBSEEKER":
        JobSeekerProfile.objects.create(user=instance)
