# speech-to-image
Speech-to-Image

Video Tutorial: https://youtu.be/uNfiu5k6RQk

Setup:
1. Download and install comfyui: https://github.com/comfyanonymous/ComfyUI
2. pip install faster-whisper (https://github.com/SYSTRAN/faster-whisper)
3. Navigate to your ComfyUI directory
4. git clone https://github.com/pydn/ComfyUI-to-Python-Extension.git
5. Navigate to the ComfyUI-to-Python-Extension folder and install requirements
6. pip install -r requirements.txt
7. navigate to /ComfyUI-to-Python-Extension
8. download zip or git clone https://github.com/All-About-AI-YouTube/speech-to-image.git
9. pip install torch, pyaudio (https://pytorch.org/get-started/locally/)
10. download a SD model (ex: https://civitai.com/models/139562/realvisxl-v30-turbo?modelVersionId=272378)
11. place the model in /comfyui/models/checkpoints
12. adjust parameters in workflow_api2.py (see video)
13. set your SD model name in line 157
14. set your save image path in display.py
15. run workflow_api2.py
