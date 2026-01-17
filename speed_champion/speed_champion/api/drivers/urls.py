from django.urls import path
from . import views

urlpatterns = [
    path('', views.ListDriversView.as_view(), name='list-drivers'),
    path('<int:driver_id>/', views.DriverDetailView.as_view(), name='driver-detail'),
    path('<int:driver_id>/evolution/', views.DriverEvolutionView.as_view(), name='driver-evolution'),
    path('compare/', views.CompareDriversView.as_view(), name='compare-drivers'),
]
