from django.contrib import admin

from apps.jobs.models import JobPosting


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ["title", "user", "created_at"]
    search_fields = ["title", "description"]
