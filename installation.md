# OmniParser: Screen Parsing tool for Pure Vision Based GUI Agent

## Quick installs
```bash
pip install flask gunicorn torch Pillow python-dotenv
pip install flasgger
pip install --upgrade torch ultralytics
```

## Install environment
```bash
pip install -r requirements.txt

apt-get update && apt-get install -y \
  libgl1-mesa-glx \
  libglib2.0-0 \
  libsm6 \
  libxext6 \
  libxrender-dev \
  libgomp1 \
  libopencv-dev \
  python3-opencv
```

## Version pins (Florence2 compatibility and web stack)
```bash
pip install "transformers==4.51.3"
pip uninstall -y gradio fastapi pydantic starlette
pip install -U \
  "gradio==4.20.0" \
  "fastapi==0.110.*" \
  "pydantic==2.6.*" \
  "starlette==0.37.*"
```

## Gradio Demo
To run gradio demo, simply run:
```bash
python gradio_demo.py
```

## Hosting as API
Use the below installation and then run the API.

### Option 1: Run Flask API with Python
```bash
python gradio_demo_final.py
```

### Option 2: Run with Gunicorn (with fallback handling)
```bash
gunicorn -w 3 --threads 1 --timeout 120 \
  --bind 0.0.0.0:52000 \
  --log-level info \
  --access-logfile - \
  --error-logfile - \
  gradio_demo_final:app
```

## Download model weights (V2)
```bash
for f in icon_detect/{train_args.yaml,model.pt,model.yaml} icon_caption/{config.json,generation_config.json,model.safetensors}; do \
  huggingface-cli download microsoft/OmniParser-v2.0 "$f" --local-dir weights; \
done
mv weights/icon_caption weights/icon_caption_florence
```

## Call the OmniParser API
```bash
curl -X POST http://localhost:52000/ocr -F "image=@/workspace/imgs/temp_image.png"
```

```bash
curl -I http://host.docker.internal:52000/health
```