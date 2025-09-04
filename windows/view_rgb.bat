@echo off
REM Windows viewer for Pi-Kinect RGB stream
REM Requires GStreamer on Windows

echo Starting Pi-Kinect RGB viewer...
echo Listening for stream from Pi on port 5000
echo Press Ctrl+C to stop
echo.

REM GStreamer pipeline to receive RTP/MJPEG stream
gst-launch-1.0 udpsrc port=5000 caps="application/x-rtp" ^
  ! rtpjpegdepay ! jpegdec ! autovideosink sync=false

pause
