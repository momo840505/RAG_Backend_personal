# api/urls.py
"""
Purpose
-------
API URL routes. Keep it minimal and import only existing views.
"""
from django.urls import path
from .views import chat, search, feedback_view

urlpatterns = [
    path('chat/', chat, name='chat'),
    path('search/', search, name='search'),
    path("feedback/", feedback_view, name="feedback"),
]
