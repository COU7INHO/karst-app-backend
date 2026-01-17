from django.urls import path
from . import views

urlpatterns = [
    path('', views.ListRacesView.as_view(), name='list-races'),
    path('leaderboard/', views.LeaderboardView.as_view(), name='leaderboard'),
    path('<int:race_id>/', views.RaceDetailView.as_view(), name='race-detail'),
    path('upload-image/', views.UploadRaceImageView.as_view(), name='upload-race-image'),
    path('save-results/', views.SaveRaceResultsView.as_view(), name='save-race-results'),
]
