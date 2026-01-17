from rest_framework import serializers
from speed_champion.api.drivers.models import Driver


class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = ['id', 'name']
