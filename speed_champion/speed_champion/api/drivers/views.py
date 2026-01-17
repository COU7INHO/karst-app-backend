from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Min, Avg, Count
from datetime import datetime, timedelta
from .models import Driver
from .serializers import DriverSerializer
from ..races.models import RaceResult, LapTime


def format_duration(duration):
    """Format timedelta to M:SS.mmm"""
    if not duration:
        return None
    total_seconds = duration.total_seconds()
    minutes = int(total_seconds // 60)
    seconds = int(total_seconds % 60)
    milliseconds = int((total_seconds % 1) * 1000)
    return f"{minutes}:{seconds:02d}.{milliseconds:03d}"


class ListDriversView(APIView):
    """List all drivers."""

    def get(self, request):
        drivers = Driver.objects.all().order_by('name')
        serializer = DriverSerializer(drivers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DriverDetailView(APIView):
    """Get driver stats."""

    def get(self, request, driver_id):
        try:
            driver = Driver.objects.get(id=driver_id)
        except Driver.DoesNotExist:
            return Response(
                {"error": "Driver not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Total races
        total_races = RaceResult.objects.filter(driver=driver).count()

        # Total laps
        total_laps = LapTime.objects.filter(race_result__driver=driver).count()

        data = {
            "id": driver.id,
            "name": driver.name,
            "total_races": total_races,
            "total_laps": total_laps
        }

        return Response(data, status=status.HTTP_200_OK)


class DriverEvolutionView(APIView):
    """Get driver lap time evolution over time. Optional filter by circuit."""

    def get(self, request, driver_id):
        try:
            driver = Driver.objects.get(id=driver_id)
        except Driver.DoesNotExist:
            return Response(
                {"error": "Driver not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        results = RaceResult.objects.filter(
            driver=driver
        ).select_related('race').order_by('race__date')

        # Optional circuit filter
        circuit_id = request.query_params.get('circuit')
        if circuit_id:
            try:
                circuit_id_int = int(circuit_id)
                results = results.filter(race__circuit_id=circuit_id_int)
            except ValueError:
                pass

        evolution = []
        for result in results:
            evolution.append({
                "date": result.race.date,
                "circuit_id": result.race.circuit.id,
                "fastest_lap": format_duration(result.fastest_lap),
                "average_lap": format_duration(result.average_lap)
            })

        return Response({
            "driver_id": driver.id,
            "driver_name": driver.name,
            "evolution": evolution
        }, status=status.HTTP_200_OK)


class CompareDriversView(APIView):
    """Compare up to 4 drivers. Optional filter by circuit."""

    def get(self, request):
        ids_param = request.query_params.get('ids', '')

        if not ids_param:
            return Response(
                {"error": "Missing 'ids' query parameter"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            driver_ids = [int(id.strip()) for id in ids_param.split(',')]
        except ValueError:
            return Response(
                {"error": "Invalid driver IDs"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(driver_ids) > 4:
            return Response(
                {"error": "Maximum 4 drivers allowed"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Optional circuit filter
        circuit_id = request.query_params.get('circuit')

        drivers_data = []

        for driver_id in driver_ids:
            try:
                driver = Driver.objects.get(id=driver_id)
            except Driver.DoesNotExist:
                continue

            results = RaceResult.objects.filter(driver=driver)

            # Apply circuit filter if provided
            if circuit_id:
                try:
                    circuit_id_int = int(circuit_id)
                    results = results.filter(race__circuit_id=circuit_id_int)
                except ValueError:
                    pass

            total_races = results.count()
            best_lap = results.aggregate(Min('fastest_lap'))['fastest_lap__min']
            avg_lap = results.aggregate(Avg('average_lap'))['average_lap__avg']

            # Get total laps for this driver (filtered by circuit if applicable)
            race_result_ids = results.values_list('id', flat=True)
            total_laps = LapTime.objects.filter(race_result_id__in=race_result_ids).count()

            drivers_data.append({
                "id": driver.id,
                "name": driver.name,
                "total_races": total_races,
                "total_laps": total_laps,
                "best_lap": format_duration(best_lap),
                "average_lap": format_duration(avg_lap)
            })

        return Response({"drivers": drivers_data}, status=status.HTTP_200_OK)
