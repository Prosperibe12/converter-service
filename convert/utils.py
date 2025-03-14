import json, pika, tempfile, os
from bson.objectid import ObjectId
from moviepy import *
import pika.spec

def start_convert(body, fs_videos, fs_mps3, ch):
    """
    convert uploaded videos to mp3
    """
    # deserialize
    message  = json.loads(body)
    
    # create temp file
    tf = tempfile.NamedTemporaryFile()
    # get video contects
    out = fs_videos.get(ObjectId(message["video_fid"]))
    # add video to emptyfile
    tf.write(out.read())
    # create audio from temp video file
    audio = VideoFileClip(tf.name).audio
    # close temp file
    tf.close()
    
    # write audio to file
    tf_path = tempfile.gettempdir() + f"/{message["video_fid"]}.mp3"
    audio.write_audiofile(tf_path)
    
    # save file to mongo
    f = open(tf_path, "rb")
    data= f.read()
    fid = fs_mps3.put(data)
    f.close()
    os.remove(tf_path)
    
    # save message to queue
    message["mp3_fid"] = str(fid)
    try:
        ch.basic_publish(
            "",
            routing_key=os.environ.get("MP3_QUEUE"),
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            )
        )
    except Exception as err:
        fs_mps3.delete(fid)
        return "Failed to publish message"