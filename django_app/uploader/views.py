import os
import json
from django.http import HttpResponse
from django.shortcuts import render
from .forms import UploadForm

def home(request):
    return HttpResponse("✅ Arabic Video Summarization App is running.")

def upload_video(request):
    uploaded = False
    file_name = ""
    
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.cleaned_data['video']
            file_name = video.name

            # Save video to Google Drive folder (assuming mounted at /content/drive)
            drive_path = "/content/drive/MyDrive/arabic_summarizer/videos"
            os.makedirs(drive_path, exist_ok=True)

            save_path = os.path.join(drive_path, file_name)
            with open(save_path, 'wb+') as destination:
                for chunk in video.chunks():
                    destination.write(chunk)

            # Save video filename to params.json
            params_path = "/content/drive/MyDrive/arabic_summarizer/params.json"
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
