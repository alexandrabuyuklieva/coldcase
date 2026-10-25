from django.contrib import admin

from .models import Case


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ('case_number', 'title', 'status', 'crime_date', 'location')
    list_filter = ('status',)
    search_fields = ('case_number', 'title', 'location', 'victim')
    readonly_fields = ('case_number', 'created_at', 'updated_at')
