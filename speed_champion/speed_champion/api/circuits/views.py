from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Min, Avg
from .models import Circuit
from .serializers import CircuitSerializer
from ..races.models import Race, LapTime, RaceResult


def format_duration(duration):
    """Format timedelta to M:SS.mmm"""
    if not duration:
        return None
    total_seconds = duration.total_seconds()
    minutes = int(total_seconds // 60)
    seconds = int(total_seconds % 60)
    milliseconds = int((total_seconds % 1) * 1000)
    return f"{minutes}:{seconds:02d}.{milliseconds:03d}"


class ListCircuitsView(APIView):
    """List all circuits."""

    def get(self, request):
        circuits = Circuit.objects.all().order_by('name')
        serializer = CircuitSerializer(circuits, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CircuitDetailView(APIView):
    """Get circuit stats."""

    def get(self, request, circuit_id):
        try:
            circuit = Circuit.objects.get(id=circuit_id)
        except Circuit.DoesNotExist:
            return Response(
                {"error": "Circuit not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Total races at this circuit
        total_races = Race.objects.filter(circuit=circuit).count()

        # Total laps at this circuit
        race_ids = Race.objects.filter(circuit=circuit).values_list('id', flat=True)
        total_laps = LapTime.objects.filter(
            race_result__race_id__in=race_ids
        ).count()

        # Fastest lap ever at this circuit with driver name
        fastest_lap_obj = LapTime.objects.filter(
            race_result__race__circuit=circuit
        ).select_related('race_result__driver').order_by('lap_time').first()

        fastest_lap_time = None
        fastest_lap_driver = None
        if fastest_lap_obj:
            fastest_lap_time = format_duration(fastest_lap_obj.lap_time)
            fastest_lap_driver = fastest_lap_obj.race_result.driver.name

        data = {
            "id": circuit.id,
            "name": circuit.name,
            "city": circuit.city,
            "type": circuit.type,
            "stats": {
                "total_races": total_races,
                "total_laps": total_laps,
                "fastest_lap_ever": fastest_lap_time,
                "fastest_lap_driver": fastest_lap_driver
            }
        }

        return Response(data, status=status.HTTP_200_OK)


class CircuitEvolutionView(APIView):
    """Get circuit evolution: fastest lap and average lap over time."""

    def get(self, request, circuit_id):
        try:
            circuit = Circuit.objects.get(id=circuit_id)
        except Circuit.DoesNotExist:
            return Response(
                {"error": "Circuit not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get all races at this circuit ordered by date
        races = Race.objects.filter(circuit=circuit).order_by('date')

        fastest_lap_evolution = []
        average_lap_evolution = []

        for race in races:
            # Get fastest lap in this race
            fastest_lap_in_race = LapTime.objects.filter(
                race_result__race=race
            ).order_by('lap_time').first()

            if fastest_lap_in_race:
                fastest_lap_evolution.append({
                    "date": race.date.isoformat(),
                    "race_id": race.id,
                    "lap_time": format_duration(fastest_lap_in_race.lap_time)
                })

            # Get average lap time across all drivers in this race
            race_results = RaceResult.objects.filter(race=race)
            if race_results.exists():
                # Calculate average of all average_lap values
                avg_of_averages = race_results.aggregate(Avg('average_lap'))['average_lap__avg']
                if avg_of_averages:
                    average_lap_evolution.append({
                        "date": race.date.isoformat(),
                        "race_id": race.id,
                        "lap_time": format_duration(avg_of_averages)
                    })

        data = {
            "circuit_id": circuit.id,
            "circuit_name": circuit.name,
            "fastest_lap_evolution": fastest_lap_evolution,
            "average_lap_evolution": average_lap_evolution
        }

        return Response(data, status=status.HTTP_200_OK)
