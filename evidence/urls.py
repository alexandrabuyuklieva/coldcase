from django.urls import path

from . import views

app_name = 'evidence'

urlpatterns = [
    path('', views.EvidenceListView.as_view(), name='list'),
    path('create/', views.EvidenceCreateView.as_view(), name='create'),
    path('<int:pk>/', views.EvidenceDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.EvidenceUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.EvidenceDeleteView.as_view(), name='delete'),
]
