from django.urls import path

from . import views

app_name = 'suspects'

urlpatterns = [
    path('', views.SuspectListView.as_view(), name='list'),
    path('create/', views.SuspectCreateView.as_view(), name='create'),
    path('<int:pk>/', views.SuspectDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.SuspectUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.SuspectDeleteView.as_view(), name='delete'),
    path('<int:suspect_pk>/alibis/create/', views.AlibiCreateView.as_view(), name='alibi-create'),
    path('alibis/<int:pk>/edit/', views.AlibiUpdateView.as_view(), name='alibi-edit'),
    path('alibis/<int:pk>/delete/', views.AlibiDeleteView.as_view(), name='alibi-delete'),
]
