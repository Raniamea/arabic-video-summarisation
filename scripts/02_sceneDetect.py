#!/usr/bin/env python
# coding: utf-8

# <a href="https://colab.research.google.com/github/Raniamea/arabic-video-summarisation/blob/main/notebooks/02_sceneDetect.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

# In[ ]:


import os, torch, cv2, json
from PIL import Image
from scenedetect import open_video, SceneManager
from scenedetect import VideoManager, SceneManager
from scenedetect.detectors import ContentDetector
from transformers import AutoProcessor, Blip2ForConditionalGeneration
from transformers import MarianMTModel, MarianTokenizer

# Path to your params.json on Google Drive
param_path = "/content/drive/MyDrive/ArabicVideoSummariser/params.json"

# Load it
with open(param_path, "r") as f:
    params = json.load(f)

# Get the filename
video_filename = params.get("video_file")
print("🎥 Transcribing video file:", video_filename)


# In[ ]:


# Define base paths
base_path = "/content/drive/MyDrive/ArabicVideoSummariser"
videos_path = os.path.join(base_path, "videos")
captions_path = os.path.join(base_path, "captions")
keyframes_path = os.path.join(base_path, "keyframes")

video_path = os.path.join(videos_path, video_filename)
video_name = os.path.splitext(video_filename)[0]
keyframe_dir = os.path.join(keyframes_path, video_name)
os.makedirs(keyframe_dir, exist_ok=True)
captions_json_path = os.path.join(captions_path, f"{video_name}.json")


# In[ ]:


# ============ SETUP ============
device = "cuda" if torch.cuda.is_available() else "cpu"

# BLIP-2 model
caption_processor = AutoProcessor.from_pretrained("Salesforce/blip2-opt-2.7b",use_fast=False)
caption_model = Blip2ForConditionalGeneration.from_pretrained(
    "Salesforce/blip2-opt-2.7b",
    device_map="auto",
    torch_dtype=torch.float16 if device == "cuda" else torch.float32
).to(device)

# Translation model (EN → AR)
translator_tokenizer = MarianTokenizer.from_pretrained("Helsinki-NLP/opus-mt-en-ar")
translator_model = MarianMTModel.from_pretrained("Helsinki-NLP/opus-mt-en-ar").to(device)

captions = {}

scene_manager = SceneManager()
scene_manager.add_detector(ContentDetector(threshold=30.0))
video = open_video(video_path)
scene_manager.detect_scenes(video)
scene_list = scene_manager.get_scene_list()

# --- Extract frames ---
cap = cv2.VideoCapture(video_path)
fps = cap.get(cv2.CAP_PROP_FPS)

for i, (start, _) in enumerate(scene_list):
  frame_num = int(start.get_seconds() * fps)
  cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
  ret, frame = cap.read()
  if not ret:
    continue

  frame_name = f"scene_{i:03}.jpg"
  frame_path = os.path.join(keyframe_dir, frame_name)
  cv2.imwrite(frame_path, frame)

  # Convert to PIL
  image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

  # --- Captioning with BLIP-2 ---
  inputs = caption_processor(images=image, return_tensors="pt").to(device, torch.float16 if device == "cuda" else torch.float32)
  generated_ids = caption_model.generate(**inputs, max_new_tokens=50)
  english_caption = caption_processor.decode(generated_ids[0], skip_special_tokens=True).strip()

  # --- Translate to Arabic ---
  translation_inputs = translator_tokenizer(english_caption, return_tensors="pt", padding=True).to(device)
  translated = translator_model.generate(**translation_inputs)
  arabic_caption = translator_tokenizer.decode(translated[0], skip_special_tokens=True).strip()

  # --- Save result with scene start time ---
  captions[frame_name] = {
    "scene_time": round(start.get_seconds(), 2),  # Time in seconds, rounded for readability
    "english": english_caption,
    "arabic": arabic_caption
    }

  print(f"✓ {frame_name} @ {start.get_seconds():.2f}s | EN: {english_caption} | AR: {arabic_caption}")

cap.release()

# Save JSON
with open(captions_json_path, "w", encoding="utf-8") as f:
  json.dump(captions, f, ensure_ascii=False, indent=2)
print(f"✅ Captions saved to: {captions_json_path}")

