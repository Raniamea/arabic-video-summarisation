from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_video, name='upload_video'),  # This handles the root "/"
    path('upload/', views.upload_video, name='upload_video'), 
    path('transcribe/', views.transcribe, name='transcribe'),
    path('sceneDetect/', views.sceneDetect, name='sceneDetect'),
    #path('generateCaptions/', views.generateCaptions, name='generateCaptions'),
    #path('validate/', views.validate, name='validate'),
   # path('summarise/', views.summarise, name='summarise'),
]
