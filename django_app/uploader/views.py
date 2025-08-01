import os
import json
import subprocess
from django.http import HttpResponse
from django.shortcuts import render
from .forms import UploadForm



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
        result = subprocess.run(
            ['python3', '/content/arabic-video-summarisation/scripts/transcribe.py'],
            capture_output=True,
            text=True,
            check=True
        )
        return HttpResponse(f"<h2>✅ Transcription Completed</h2><pre>{result.stdout}</pre>")
    except subprocess.CalledProcessError as e:
        return HttpResponse(f"<h2>❌ Error Running Script</h2><pre>{e.stderr}</pre>")

