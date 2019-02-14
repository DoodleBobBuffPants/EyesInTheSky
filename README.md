# EyesInTheSky
Group Project

Requirements:
- pyparrot
- zeroconf
- opencv (and FFmpeg)
- filelock (for more reliable, non naive locking)

Required environment variable:
	OPENCV_FFMPEG_CAPTURE_OPTIONS = protocol_whitelist;file,rtp,udp

Do `pip install -r requirements.txt` to install all requirements

The MIT license covers use of the pyparrot library.

SDP files need to be configured locally because IP addresses differ.