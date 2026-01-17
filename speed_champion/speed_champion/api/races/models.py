from django.db import models
from speed_champion.api.circuits.models import Circuit
from speed_champion.api.drivers.models import Driver

class Race(models.Model):
    circuit = models.ForeignKey(Circuit, on_delete=models.CASCADE)
    date = models.DateField()

    def __str__(self):
        return f"{self.circuit.name} - {self.date}"
    
class RaceResult(models.Model):
    race = models.ForeignKey(Race, on_delete=models.CASCADE, related_name='results')
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)

    total_time = models.DurationField(null=True, blank=True)
    fastest_lap = models.DurationField(null=True, blank=True)
    average_lap = models.DurationField(null=True, blank=True)

    def __str__(self):
        return f"{self.driver} - {self.race}"

class LapTime(models.Model):
    race_result = models.ForeignKey(
        RaceResult,
        on_delete=models.CASCADE,
        related_name='laps'
    )
    lap_number = models.PositiveSmallIntegerField()
    lap_time = models.DurationField()

    def __str__(self):
        return f"Lap {self.lap_number} - {self.lap_time}"
