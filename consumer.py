import os, sys, pika
from pymongo import MongoClient
import gridfs
from convert import utils

def main():
    """
    Converter Service receives messages from the video queue and processes it, proceesed messages are sent back to
    the mp3 queue for consumption by the notification service. 
    """
    # create a connection to the mongodb service
    client = MongoClient("mongodb://mongodb-service", 27017)
    db_videos = client.videos
    db_mp3s = client.mp3s
    
    # connect to gridfs
    fs_videos = gridfs.GridFS(db_videos)
    fs_mp3s  = gridfs.GridFS(db_mp3s)
    
    # create a connection to Rabbitmq
    connection = pika.BlockingConnection(pika.URLParameters("amqp://guest:guest@rabbitmq:5672/"))
    channel = connection.channel()
    
    # define a callback function
    def callback(ch, method, properties, body):
        """
        execute the function when a message is received in the queue
        """
        # convert the video to mp3
        err = utils.start_convert(body,fs_videos,fs_mp3s,ch)
        if err:
            # acknowledge message failure
            ch.basic_nack(delivery_tag=method.delivery_tag)
        else:
            # acknowledge message delivery
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
    # consume messages from the queue
    channel.basic_consume(
        queue=os.environ.get("VIDEO_QUEUE"), on_message_callback=callback
    )
    print('[*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()
    
if __name__ == "__main__":
    try:
        # start listening on the queue for messages
        main()
    except KeyboardInterrupt:
        print("Interruped")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)