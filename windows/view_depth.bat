@echo off
REM Windows viewer for Pi-Kinect depth stream
REM Requires GStreamer on Windows

echo Starting Pi-Kinect depth viewer...
echo Listening for stream from Pi on port 5001
echo Press Ctrl+C to stop
echo.

REM GStreamer pipeline to receive RTP/MJPEG stream
gst-launch-1.0 udpsrc port=5001 caps="application/x-rtp" ^
  ! rtpjpegdepay ! jpegdec ! autovideosink sync=false

pause
