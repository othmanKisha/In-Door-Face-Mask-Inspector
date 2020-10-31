from pymongo import MongoClient
import app_config


client = MongoClient(app_config.MONGO_HOST, app_config.MONGO_PORT)
db = client[app_config.MONGO_DB]

cameras = db.cameras
cameras.insert_many([
    {
        "office": "web_cam",
        "rtsp": 0
    },
    {
        "office": "office1",
        "rtsp": "rtsp://192.168.100.13:8080/h264_pcm.sdp"
    }
])
