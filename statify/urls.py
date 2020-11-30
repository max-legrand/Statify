"""statify URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('about/', views.about),
    path('', views.home),
    path('login/', views.loginspotify),
    path('logout/', views.logoutspotify),
    path('authorize/', views.authorize),
    path('recent_tracks/', views.recent_tracks),
    path('recent_genres/', views.recent_genres),
    path('recent_artists/', views.recent_artists),
    path('top_tracks/', views.top_tracks),
    path('top_tracks_med/', views.top_tracks_med),
    path('top_tracks_long/', views.top_tracks_long),
    path('top_artists/', views.top_artists),
    path('top_artists_med/', views.top_artists_med),
    path('top_artists_long/', views.top_artists_long),
    path('top_genres/', views.top_genres),
    path('top_genres_med/', views.top_genres_med),
    path('top_genres_long/', views.top_genres_long),
]
