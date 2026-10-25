from django.contrib import admin

from .models import Alibi, Suspect


class AlibiInline(admin.TabularInline):
    model = Alibi
    extra = 0


@admin.register(Suspect)
class SuspectAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'alias', 'date_of_birth')
    search_fields = ('first_name', 'last_name', 'alias')
    filter_horizontal = ('cases',)
    inlines = (AlibiInline,)


@admin.register(Alibi)
class AlibiAdmin(admin.ModelAdmin):
    list_display = ('suspect', 'location', 'starts_at', 'ends_at')
    list_filter = ('suspect',)
