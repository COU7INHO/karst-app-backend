from django.urls import path
from . import views

urlpatterns = [
    path('', views.ListCircuitsView.as_view(), name='list-circuits'),
    path('<int:circuit_id>/', views.CircuitDetailView.as_view(), name='circuit-detail'),
    path('<int:circuit_id>/evolution/', views.CircuitEvolutionView.as_view(), name='circuit-evolution'),
]
