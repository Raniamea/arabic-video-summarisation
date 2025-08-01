from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # This handles the root "/"
    path('upload/', views.upload_video, name='upload_video'),  # You can keep this if you already have it
]
