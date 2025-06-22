# Arabic Video Summarisation

A multimodal pipeline for summarising Arabic news videos using ASR, object detection, and NLP.

# Arabic Video Summarisation

A multimodal system for summarising Arabic news videos using:
- 🎤 Whisper for speech transcription
- 🎥 YOLOv8 for object detection
- 🧠 AraBERT/mBART for text summarization
- 🧪 Sentence-BERT for semantic validation

## Project Structure

- `notebooks/`: Colab-ready notebooks for each pipeline step
- `scripts/`: Optional automation scripts
- `videos/`: Stored on Google Drive
- `transcripts/`, `summaries/`, `keyframes/`: Output folders in Drive

## How to Run

1. Open a notebook in [Google Colab](https://colab.research.google.com)
2. Mount your Drive
3. Install the required libraries
4. Run transcription, detection, summarization, and evaluation
