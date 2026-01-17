from rest_framework import serializers
from .models import Race, RaceResult, LapTime
from ..circuits.models import Circuit


def format_duration(duration):
    """Format timedelta to M:SS.mmm"""
    if not duration:
        return None
    total_seconds = duration.total_seconds()
    minutes = int(total_seconds // 60)
    seconds = int(total_seconds % 60)
    milliseconds = int((total_seconds % 1) * 1000)
    return f"{minutes}:{seconds:02d}.{milliseconds:03d}"


class OCRUploadSerializer(serializers.Serializer):
    image = serializers.ImageField()

    def validate_image(self, value):
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("Image too large. Maximum 10MB.")
        return value


class LapTimeDataSerializer(serializers.Serializer):
    lap_number = serializers.IntegerField()
    lap_time = serializers.CharField()


class DriverRaceDataSerializer(serializers.Serializer):
    name = serializers.CharField()
    laps = LapTimeDataSerializer(many=True)
    fastest_lap = serializers.CharField(required=False, allow_null=True)
    average_lap = serializers.CharField(required=False, allow_null=True)


class SaveRaceResultSerializer(serializers.Serializer):
    circuit_id = serializers.IntegerField()
    date = serializers.DateField()
    selected_drivers = serializers.ListField(
        child=serializers.DictField(),
        help_text="List of driver data to register"
    )

    def validate_circuit_id(self, value):
        if not Circuit.objects.filter(id=value).exists():
            raise serializers.ValidationError("Circuit does not exist.")
        return value


class LapTimeSerializer(serializers.ModelSerializer):
    lap_time = serializers.SerializerMethodField()

    class Meta:
        model = LapTime
        fields = ['lap_number', 'lap_time']

    def get_lap_time(self, obj):
        return format_duration(obj.lap_time)


class RaceResultSerializer(serializers.ModelSerializer):
    driver_name = serializers.CharField(source='driver.name')
    laps = LapTimeSerializer(many=True, read_only=True)
    total_time = serializers.SerializerMethodField()
    fastest_lap = serializers.SerializerMethodField()
    average_lap = serializers.SerializerMethodField()

    class Meta:
        model = RaceResult
        fields = ['driver_name', 'total_time', 'fastest_lap', 'average_lap', 'laps']

    def get_total_time(self, obj):
        return format_duration(obj.total_time)

    def get_fastest_lap(self, obj):
        return format_duration(obj.fastest_lap)

    def get_average_lap(self, obj):
        return format_duration(obj.average_lap)


class RaceListSerializer(serializers.ModelSerializer):
    circuit_id = serializers.IntegerField(source='circuit.id')
    circuit_name = serializers.CharField(source='circuit.name')

    class Meta:
        model = Race
        fields = ['id', 'date', 'circuit_id', 'circuit_name']


class RaceDetailSerializer(serializers.ModelSerializer):
    circuit = serializers.SerializerMethodField()
    results = RaceResultSerializer(many=True, read_only=True)

    class Meta:
        model = Race
        fields = ['id', 'circuit', 'date', 'results']

    def get_circuit(self, obj):
        return obj.circuit.id
