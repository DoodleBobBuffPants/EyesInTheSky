# EyesInTheSky
Group Project

Requirements:
- pyparrot
- zeroconf
- opencv (and FFmpeg)
- MATLAB

MATLAB Requirements:
- Deep Learning Toolbox
- Computer Vision Toolkit

Required environment variable:
	OPENCV_FFMPEG_CAPTURE_OPTIONS = protocol_whitelist;file,rtp,udp

Do `pip install -r requirements.txt` to install all requirements.

The MIT license covers use of the pyparrot library.

SDP files need to be configured locally because IP addresses differ.

Documentation:

Run app.py (located in backend\server) to start the web interface on localhost:5000.
The interface has self-explanatory buttons, and the code is all commented and self-documenting.