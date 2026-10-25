from django.contrib import admin

from .models import Evidence


@admin.register(Evidence)
class EvidenceAdmin(admin.ModelAdmin):
    list_display = ('title', 'case', 'evidence_type', 'collected_on', 'confidence', 'implicates')
    list_filter = ('evidence_type', 'case')
    search_fields = ('title', 'description')
