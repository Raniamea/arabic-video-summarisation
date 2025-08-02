import os
import json
import subprocess
from django.http import HttpResponse
from django.shortcuts import render
from .forms import UploadForm
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
        result = subprocess.run([
            '/content/env_transcribe/bin/jupyter', 'nbconvert',
            '--to', 'notebook',
            '--execute',
            '--inplace',
            '--ExecutePreprocessor.kernel_name=env_transcribe',  
            '/content/arabic-video-summarisation/notebooks/01_transcribe.ipynb'
        ], capture_output=True, text=True)

        if result.returncode == 0:
            base_url = request.build_absolute_uri('/')[:-1]
            next_url = f"{base_url}/sceneDetect"
            return HttpResponse(f"""
                <h2>✅ Transcription completed</h2>
                <p>Next step:</p>
                <ul><li><a href="{next_url}" target="_blank">📸 Run Scene Detection</a></li></ul>
            """)
        else:
            return HttpResponse(f"<h2>❌ Error</h2><pre>{result.stderr}</pre>")

    except Exception as e:
        return HttpResponse(f"<h2>❌ Transcribe Exception</h2><pre>{str(e)}</pre>")

def sceneDetect(request):
    try:
        result = subprocess.run([
            '/content/env_scene/bin/jupyter', 'nbconvert',
            '--to', 'notebook',
            '--execute',
            '--inplace',
            '--ExecutePreprocessor.kernel_name=env_scene',  
            '/content/arabic-video-summarisation/notebooks/02_sceneDetect.ipynb'
        ], capture_output=True, text=True)

        if result.returncode == 0:
            base_url = request.build_absolute_uri('/')[:-1]
            next_url = f"{base_url}/generateCaptions"
            return HttpResponse(f"""
                <h2>✅ Scene Detection completed</h2>
                <p>Next step:</p>
                <ul><li><a href="{next_url}" target="_blank">📝 Run Caption Generation</a></li></ul>
            """)
        else:
            return HttpResponse(f"<h2>❌ Error</h2><pre>{result.stderr}</pre>")

    except Exception as e:
        return HttpResponse(f"<h2>❌ SceneDetect Exception</h2><pre>{str(e)}</pre>")


def generateCaptions(request):
    try:
        result = subprocess.run([
            '/content/env_caption/bin/jupyter', 'nbconvert',
            '--to', 'notebook',
            '--execute',
            '--inplace',
            '--ExecutePreprocessor.kernel_name=env_caption',  
            '/content/arabic-video-summarisation/notebooks/03_generateCaptions.ipynb'
        ], capture_output=True, text=True)

        if result.returncode == 0:
            return HttpResponse("<h2>✅ Caption Generation completed</h2>")
        else:
            return HttpResponse(f"<h2>❌ Error</h2><pre>{result.stderr}</pre>")

    except Exception as e:
        return HttpResponse(f"<h2>❌ GenerateCaptions Exception</h2><pre>{str(e)}</pre>")
