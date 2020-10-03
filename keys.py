# [IMPORTANT]
# *** Here we should add all cameras ***
# - IP Cameras should be added as follows:
#   "rtsp://<ip>:<port>/h264_pcm.sdp"
#   or 
#   "rtsp://<ip>:<port>/h264_ulaw.sdp"
#   - testing on ip webcam app for android
#   - the app should be on the same network as the computer to identify it

# - 0 refers to the webcam of laptop, it is only for testing purposes

CAMERAS = {
    "web_cam": 0,
    "office1": "rtsp://192.168.100.13:8080/h264_pcm.sdp"
}

# [IMPORTANT]
# - Here we should store the follwoing important keys for the database:
#    - the url.
#    - the port.
#    - the name of the database.    

DATABASE = {
    "url": "",
    "port": "",
    "name": ""
}
