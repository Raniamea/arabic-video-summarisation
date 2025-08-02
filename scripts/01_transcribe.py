#!/usr/bin/env python
# coding: utf-8

# <a href="https://colab.research.google.com/github/Raniamea/arabic-video-summarisation/blob/main/notebooks/01_transcribe.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

# In[ ]:


get_ipython().system('apt-get install ffmpeg')
get_ipython().system('pip install -q pydub')


# In[ ]:


import json
from google.colab import drive
import os

# Unmount first
get_ipython().system('fusermount -u /content/drive || echo "Already unmounted"')

# Delete the mount folder entirely
get_ipython().system('rm -rf /content/drive')

# Now mount again
from google.colab import drive
drive.mount('/content/drive')

# Path to your params.json on Google Drive
param_path = "/content/drive/MyDrive/ArabicVideoSummariser/params.json"

# Load it
with open(param_path, "r") as f:
    params = json.load(f)

# Get the filename
video_filename = params.get("video_file")
print("🎥 Transcribing video file:", video_filename)

from pydub import AudioSegment
import math

# Define base paths
base_path = "/content/drive/MyDrive/ArabicVideoSummariser"
videos_path = os.path.join(base_path, "videos")
transcripts_path = os.path.join(base_path, "transcripts")

video_path = os.path.join(videos_path, video_filename)
video_name = os.path.splitext(video_filename)[0]
transcript_path = os.path.join(transcripts_path, f"{video_name}_ar.txt")
trascription_json_path = os.path.join(transcripts_path, f"{video_name}_ar.json")

# Convert video to audio
audio_path = os.path.join(videos_path, f"{video_name}.wav")
get_ipython().system('ffmpeg -y -i "{video_path}" -ar 16000 -ac 1 "{audio_path}"  # Resample to 16kHz mono')

# Load audio using pydub
audio = AudioSegment.from_wav(audio_path)
chunk_length_ms = 30 * 1000  # 30 seconds
total_chunks = math.ceil(len(audio) / chunk_length_ms)

print(f"🔊 Audio duration: {len(audio) / 1000:.1f}s, Chunks: {total_chunks}")


# In[ ]:


import torch, whisper, json, gc

torch.cuda.empty_cache()
gc.collect()

model = whisper.load_model("large", device="cuda", in_memory=True)

results_ar = []
results_en = []

for i in range(total_chunks):
    start_ms = i * chunk_length_ms
    end_ms = min((i + 1) * chunk_length_ms, len(audio))
    chunk = audio[start_ms:end_ms]
    chunk_file = f"/content/chunk_{i}.wav"
    chunk.export(chunk_file, format="wav")

    print(f"⏱️ Transcribing chunk {i+1}/{total_chunks} ({start_ms/1000:.1f}s - {end_ms/1000:.1f}s)")

    # Arabic transcription
    result_ar = model.transcribe(
        chunk_file, language="ar", task="transcribe", verbose=False, fp16=False
    )
    for segment in result_ar["segments"]:
        segment["start"] += start_ms / 1000
        segment["end"] += start_ms / 1000
        results_ar.append(segment)

    # English translation
    result_en = model.transcribe(
        chunk_file, language="ar", task="translate", verbose=False, fp16=False
    )
    for segment in result_en["segments"]:
        segment["start"] += start_ms / 1000
        segment["end"] += start_ms / 1000
        results_en.append(segment)

# === Arabic Output ===
# Save text transcript
with open(transcript_path, "w", encoding="utf-8") as f:
    f.write(" ".join([seg["text"] for seg in results_ar]))

# Save time-coded transcript
with open(transcript_path.replace(".txt", "_with_timecodes.txt"), "w", encoding="utf-8") as f:
    for seg in results_ar:
        f.write(f"[{seg['start']:.2f} - {seg['end']:.2f}] {seg['text']}\n")

# Save JSON
with open(trascription_json_path, "w", encoding="utf-8") as f:
    json.dump({"segments": results_ar}, f, ensure_ascii=False, indent=2)

# === English Output ===
en_txt_path = transcript_path.replace("ar.txt", "en.txt")
with open(en_txt_path, "w", encoding="utf-8") as f:
    f.write(" ".join([seg["text"] for seg in results_en]))

with open(en_txt_path.replace(".txt", "_with_timecodes.txt"), "w", encoding="utf-8") as f:
    for seg in results_en:
        f.write(f"[{seg['start']:.2f} - {seg['end']:.2f}] {seg['text']}\n")

with open(trascription_json_path.replace("ar.json", "en.json"), "w", encoding="utf-8") as f:
    json.dump({"segments": results_en}, f, ensure_ascii=False, indent=2)


# In[ ]:


del model
torch.cuda.empty_cache()
gc.collect()

