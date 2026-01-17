from django.contrib import admin
from .models import Circuit


@admin.register(Circuit)
class CircuitAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'type']
    search_fields = ['name', 'city']
    list_filter = ['type', 'city']
