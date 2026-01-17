from django.contrib import admin
from .models import Race, RaceResult, LapTime


def format_duration(duration):
    """Format timedelta to M:SS.mmm"""
    if not duration:
        return "-"
    total_seconds = duration.total_seconds()
    minutes = int(total_seconds // 60)
    seconds = int(total_seconds % 60)
    milliseconds = int((total_seconds % 1) * 1000)
    return f"{minutes}:{seconds:02d}.{milliseconds:03d}"


class LapTimeInline(admin.TabularInline):
    model = LapTime
    extra = 1
    fields = ['lap_number', 'formatted_lap_time']
    readonly_fields = ['formatted_lap_time']

    def formatted_lap_time(self, obj):
        return format_duration(obj.lap_time) if obj.lap_time else "-"
    formatted_lap_time.short_description = "Lap Time"


@admin.register(RaceResult)
class RaceResultAdmin(admin.ModelAdmin):
    list_display = ['driver', 'race', 'formatted_total', 'formatted_fastest', 'formatted_average']
    search_fields = ['driver__name', 'race__circuit__name']
    list_filter = ['race__date', 'race__circuit']
    autocomplete_fields = ['race', 'driver']
    inlines = [LapTimeInline]

    def formatted_total(self, obj):
        return format_duration(obj.total_time)
    formatted_total.short_description = "Total Time"

    def formatted_fastest(self, obj):
        return format_duration(obj.fastest_lap)
    formatted_fastest.short_description = "Fastest Lap"

    def formatted_average(self, obj):
        return format_duration(obj.average_lap)
    formatted_average.short_description = "Average Lap"


class RaceResultInline(admin.TabularInline):
    model = RaceResult
    extra = 0
    fields = ['driver', 'formatted_total', 'formatted_fastest', 'formatted_average']
    readonly_fields = ['formatted_total', 'formatted_fastest', 'formatted_average']
    autocomplete_fields = ['driver']

    def formatted_total(self, obj):
        return format_duration(obj.total_time)
    formatted_total.short_description = "Total"

    def formatted_fastest(self, obj):
        return format_duration(obj.fastest_lap)
    formatted_fastest.short_description = "Fastest"

    def formatted_average(self, obj):
        return format_duration(obj.average_lap)
    formatted_average.short_description = "Average"


@admin.register(Race)
class RaceAdmin(admin.ModelAdmin):
    list_display = ['circuit', 'date']
    search_fields = ['circuit__name']
    list_filter = ['date', 'circuit']
    autocomplete_fields = ['circuit']
    inlines = [RaceResultInline]
