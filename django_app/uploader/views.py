import os
import json
import subprocess
from django.http import HttpResponse
from django.shortcuts import render
from .forms import UploadForm
import papermill as pm
from django.http import HttpResponse


import os
from google.colab import drive

def home(request):
    return HttpResponse("Arabic Video Summarization App is running.")

def upload_video(request):
    uploaded = False
    file_name = ""

    # Mount Google Drive if not mounted
    if not os.path.exists("/content/drive/MyDrive"):
        drive.mount('/content/drive')
    
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.cleaned_data['video']
            file_name = video.name

            # Save video to Google Drive folder (assuming mounted at /content/drive)
            drive_path = "/content/drive/MyDrive/ArabicVideoSummariser/videos"
            os.makedirs(drive_path, exist_ok=True)

            save_path = os.path.join(drive_path, file_name)
            with open(save_path, 'wb+') as destination:
                for chunk in video.chunks():
                    destination.write(chunk)

            # Save video filename to params.json
            params_path = "/content/drive/MyDrive/ArabicVideoSummariser/params.json"
            with open(params_path, "w") as f:
                json.dump({ "video_file": file_name }, f)

            uploaded = True

    else:
        form = UploadForm()

    return render(request, 'upload.html', {
        'form': form,
        'uploaded': uploaded,
        'file_name': file_name
    })


def transcribe(request):
    try:
        pm.execute_notebook(
            '/content/arabic-video-summarisation/notebooks/01_transcribe.ipynb',
            '/content/arabic-video-summarisation/notebooks/out_transcribe.ipynb'
        )
        return HttpResponse("<h2>✅ Transcription completed</h2>")
    except Exception as e:
        return HttpResponse(f"<h2>❌ Error in transcription</h2><pre>{str(e)}</pre>")


def sceneDetect(request):
    try:
        pm.execute_notebook(
            '/content/arabic-video-summarisation/notebooks/02_sceneDetect.ipynb',
            '/content/arabic-video-summarisation/notebooks/out_sceneDetect.ipynb'
        )
        return HttpResponse("<h2>✅ Scene Detection completed</h2>")
    except Exception as e:
        return HttpResponse(f"<h2>❌ Error in sceneDetection</h2><pre>{str(e)}</pre>")

