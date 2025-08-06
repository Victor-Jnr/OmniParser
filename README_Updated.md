# OmniParser: Screen Parsing tool for Pure Vision Based GUI Agent

<p align="center">
  <img src="imgs/logo.png" alt="Logo">
</p>

[![arXiv](https://img.shields.io/badge/Paper-green)](https://arxiv.org/abs/2408.00203)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

📢 [[Project Page](https://microsoft.github.io/OmniParser/)] [[Blog Post](https://www.microsoft.com/en-us/research/articles/omniparser-for-pure-vision-based-gui-agent/)] [[Models](https://huggingface.co/microsoft/OmniParser)] [[Huggingface demo](https://huggingface.co/spaces/microsoft/OmniParser)]

**OmniParser** is a comprehensive method for parsing user interface screenshots into structured and easy-to-understand elements, which significantly enhances the ability of GPT-4V to generate actions that can be accurately grounded in the corresponding regions of the interface. 

## News
- [2024/10] OmniParser is the #1 trending model on huggingface model hub (starting 10/29/2024). 
- [2024/10] Feel free to checkout our demo on [huggingface space](https://huggingface.co/spaces/microsoft/OmniParser)! (stay tuned for OmniParser + Claude Computer Use)
- [2024/10] Both Interactive Region Detection Model and Icon functional description model are released! [Hugginface models](https://huggingface.co/microsoft/OmniParser)
- [2024/09] OmniParser achieves the best performance on [Windows Agent Arena](https://microsoft.github.io/WindowsAgentArena/)! 

## Install

---------------------------------------------APRIL START
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

## Hosting as API, use below installation and run the api.py
pip install flask gunicorn torch Pillow python-dotenv
pip install flasgger

pip install --upgrade torch ultralytics

## Option-5 GPU-Quality OCR: Run Gunicorn with the following command to capture logs in /workspace/gunicorn.log
gunicorn -w 1 -b 0.0.0.0:20001 app_gpu:app --log-level info --access-logfile gunicorn.log --error-logfile gunicorn.log --capture-output --timeout 120

curl -F "file=@/opt/app-root/src/omniparser-api/imgs/windows_home.png" "localhost:20001/process_image"

Above is running in the Training Namespace as workbench.
Now we identify the IP address of this pods using command below
hostname -i
10.128.8.31

Update this IP addres in below UnserNamespace and create them in Unsernamespace

---  Below are the static pod resources for the OmniParser
# Once deployment and service created you can use the port formwarding 
# Service definition for OmniParser oc port-forward service/omniparser-version-2000 9999:8080
apiVersion: v1
kind: Service
metadata:
  name: omniparser-version-2000
spec:
  selector:
    app: omniparser-version-2000
  ports:
    - protocol: TCP
      port: 8080
      targetPort: 8080

---
# Deployment definition for OmniParser
apiVersion: apps/v1
kind: Deployment
metadata:
  name: omniparser-version-2000
spec:
  replicas: 1
  selector:
    matchLabels:
      app: omniparser-version-2000
  template:
    metadata:
      labels:
        app: omniparser-version-2000
    spec:
      priorityClassName: system-node-critical
      tolerations:
        - operator: "Exists"
      containers:
        - name: omniparser-version-2000
          image: alpine/socat
          command:
            - sh
            - -c
            - |
              socat TCP-LISTEN:8080,fork,reuseaddr TCP:10.128.8.31:20001
          ports:
            - containerPort: 8080
          resources:
            requests:
              cpu: "500m"
              memory: "512Mi"
            limits:
              cpu: "2000m"
              memory: "2048Mi"
      restartPolicy: Always

# To test it from Lpatop use 
curl -X POST http://host.docker.internal:9999/process_image  -F "file=@/workspace/static/images/LandingPage.png"

---------------------------------------------APRIL END





Install environment:
```python
echo 'export PYTHONPATH="/workspace:$PYTHONPATH"' >> ~/.bashrc
source ~/.bashrc
echo $PYTHONPATH
/workspace:

pip install -r requirements.txt

apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libopencv-dev \
    python3-opencv
```

pip install --upgrade torch ultralytics

# Change directory to some other place to clone microsoft/OmniParser checkpoint
brew install git-lfs
git lfs install
git clone https://huggingface.co/microsoft/OmniParser

Then download the model ckpts files in: https://huggingface.co/microsoft/OmniParser, and put them under weights/, default folder structure is: weights/icon_detect, weights/icon_caption_florence, weights/icon_caption_blip2. 

Copy /opt/app-root/src/omniparser-api/weights/icon_detect/model.safetensors to /opt/app-root/src/omniparser-api/weights/icon_detect_v1_5/model.safetensors

Finally, convert the safetensor to .pt file. 
```python
python weights/convert_safetensor_to_pt.py
```

## Examples:
We put together a few simple examples in the demo.ipynb. 

## Gradio Demo
To run gradio demo, simply run:
```python
python gradio_demo.py
```
## Gradio Demo using gradio_demo_1.py
To run gradio demo, with Optimized Code for Quick Execution. Here’s a stripped-down version of your gradio_demo.py that removes unnecessary UI components and focuses only on the image upload and parsed screen elements output::
```python
python gradio_demo_1.py

## Gradio Demo using gradio_demo_2.py
To run gradio demo, with Optimized Code for Quick Execution. UI varaibles are added:
```python
python gradio_demo_2.py

## Gradio Demo using gradio_demo_2.py
To run gradio demo, with Optimized Code for Quick Execution. 
gradio_demo.py to read all parameters from a .env file, which will act as a centralized configuration. The default values will be moved to this file along with comments explaining each parameter.

```python
python gradio_demo_3.py


## Hosting as API, use below installation and run the api.py
pip install flask gunicorn torch Pillow python-dotenv
pip install flasgger


## Option-1 : Run below command to host the api
python app.py

## Option-2 : Run below command to host the api
gunicorn -w 4 -b 0.0.0.0:58090 app:app --log-level info --capture-output --worker-class gthread --threads 4 --preload

## Option-3 : Run Gunicorn with the following command to capture logs in /workspace/gunicorn.log
gunicorn -w 1 -b 0.0.0.0:58090 app:app --log-level info --access-logfile gunicorn.log --error-logfile gunicorn.log --capture-output --timeout 120

## Option-4 CPU-Faster OCR: Run Gunicorn with the following command to capture logs in /workspace/gunicorn.log
gunicorn -w 1 -b 0.0.0.0:58090 app_cpu:app --log-level info --access-logfile gunicorn.log --error-logfile gunicorn.log --capture-output --timeout 120

## Option-5 GPU-Quality OCR: Run Gunicorn with the following command to capture logs in /workspace/gunicorn.log
gunicorn -w 1 -b 0.0.0.0:58090 app_gpu:app --log-level info --access-logfile gunicorn.log --error-logfile gunicorn.log --capture-output --timeout 120

## Option-6 GPU-Quality OCR: Run Gunicorn with the following command to capture logs in /workspace/gunicorn.log
python gradio_demo_final.py 

## Call the OmniParser API
curl -X POST http://localhost:52000/ocr  -F "image=@/workspace/imgs/temp_image.png"

curl -I http://host.docker.internal:52000/health

## You can access the Swagger documentation by navigating to:
http://localhost:58090/apidocs/

## Remember to run the gradio_demo_4_api.py first before calling the api

## Model Weights License
For the model checkpoints on huggingface model hub, please note that icon_detect model is under AGPL license since it is a license inherited from the original yolo model. And icon_caption_blip2 & icon_caption_florence is under MIT license. Please refer to the LICENSE file in the folder of each model: https://huggingface.co/microsoft/OmniParser.

## 📚 Citation
Our technical report can be found [here](https://arxiv.org/abs/2408.00203).
If you find our work useful, please consider citing our work:
Yes- Sure
```
@misc{lu2024omniparserpurevisionbased,
      title={OmniParser for Pure Vision Based GUI Agent}, 
      author={Yadong Lu and Jianwei Yang and Yelong Shen and Ahmed Awadallah},
      year={2024},
      eprint={2408.00203},
      archivePrefix={arXiv},
      primaryClass={cs.CV},
      url={https://arxiv.org/abs/2408.00203}, 
}
```
apt install tree
tree -L 4 -I 'node_modules|git|ls_volume|ui|public'


To Start Application Run below command:-

SERVER_PORT=58000 WORKERS=2 ./start_server.py
python start_server.py
./start_server.py

---------Running on Platform
OmniParser Application Management Guide

>Stop the Existing Application
# Find and kill the running process
pkill -f "python gradio_demo_4_api.py"

>Set Up the Monitoring Script
Create the monitor script:
cat > /opt/app-root/src/OmniParser/monitor_app.sh << 'EOL'
#!/bin/bash

LOG_FILE="/opt/app-root/src/logs/monitor.log"

start_app() {
    cd /opt/app-root/src/OmniParser
    
    if [ ! -d "venv" ]; then
        echo "$(date): Creating virtual environment..." >> $LOG_FILE
        python3 -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
        
        if [ -f "requirements.txt" ]; then
            pip install -r requirements.txt
        fi
    else
        source venv/bin/activate
    fi
    
    if ! pgrep -f "python gradio_demo_4_api.py" > /dev/null; then
        echo "$(date): Starting application..." >> $LOG_FILE
        nohup python gradio_demo_4_api.py > /opt/app-root/src/logs/omniparser.log 2>&1 &
    fi
}

start_app

(
    while true; do
        if ! pgrep -f "python gradio_demo_4_api.py" > /dev/null; then
            echo "$(date): Application not running, restarting..." >> $LOG_FILE
            start_app
        fi
        sleep 60
    done
) &

echo $! > /opt/app-root/src/logs/monitor.pid
echo "Monitor started with PID $(cat /opt/app-root/src/logs/monitor.pid)"
EOL

chmod +x /opt/app-root/src/OmniParser/monitor_app.sh


>Make the startup persisting:
echo '
# Auto-start OmniParser on login
if [ -f /opt/app-root/src/OmniParser/monitor_app.sh ]; then
    /opt/app-root/src/OmniParser/monitor_app.sh
fi' >> ~/.bashrc

Usage Instructions:-
1. Start application with monitoring:
   /opt/app-root/src/OmniParser/monitor_app.sh

2. Stop application:
   pkill -f "python gradio_demo_4_api.py"
   pkill -f "monitor_app.sh"

3. Restart application:
   pkill -f "python gradio_demo_4_api.py"
   /opt/app-root/src/OmniParser/monitor_app.sh

4. View application logs:
   tail -f /opt/app-root/src/logs/omniparser.log

5. View monitor logs
   tail -f /opt/app-root/src/logs/monitor.log

6. To Stop the current monitor (if running):
   if [ -f /opt/app-root/src/logs/monitor.pid ]; then
     kill $(cat /opt/app-root/src/logs/monitor.pid)
   fi

7. Start the monitor again:
   /opt/app-root/src/OmniParser/monitor_app.sh


