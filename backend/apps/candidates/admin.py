from django.contrib import admin

from apps.candidates.models import Candidate


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "user", "created_at"]
    search_fields = ["name", "email", "resume_text"]
