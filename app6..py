from keras.models import load_model
import cv2
from matplotlib import pyplot as plt
import tensorflow as tf
import os
import pika
import numpy as np
import threading
from flask import Flask,render_template,request , jsonify

sess = tf.compat.v1.Session()
graph = tf.compat.v1.get_default_graph()

def send_message(message):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host='125.212.228.171',
            port=5672,
            virtual_host='nextfarm',
            credentials=pika.PlainCredentials('ai', '123456Aa')
        )
    )
    channel = connection.channel()
    channel.queue_declare(queue='api_queue')
    # message = 'Hello, Rabbitmq!'
    channel.basic_publish(
        exchange='',
        routing_key='nextfarm_ai_message',
        body=message
    )
    connection.close()
    return 'Message sent successfully'

# with sess.as_default():
#     with graph.as_default():
model = load_model("models/new_model3.h5")
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    ketqua = ""
    if request.method == 'POST':
        file = request.files['file']
        
        npimg = np.fromstring(file.read(), np.uint8)
        img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

        #save img
        # if not os.path.exists('img_save_by_flask'):
        #     os.makedirs('img_save_by_flask')
        # filename = file.filename
        # file.save(os.path.join('img_save_by_flask', filename))
        # img = cv2.imread(f"img_save_by_flask/{filename}")

        resize = tf.image.resize(img, (256,256))
        yhat = model.predict(np.expand_dims(resize/255, 0))
        if yhat > 0.5: 
            # return "potato"
            # send_to_rabbitmq("potato")
            # send_message("potato")
            return render_template("index7.html",ketqua = "potato")
            
        else:
            # return "apple"
            # send_to_rabbitmq("apple")
            # send_message("apple")
            return render_template("index7.html",ketqua = "apple")

            
        return 'File uploaded successfully!'
    return render_template('index7.html')

#test xem đã gửi lên chưa
@app.route('/receive_message')
def receive_message():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host='125.212.228.171',
            port=5672,
            virtual_host='nextfarm',
            credentials=pika.PlainCredentials('ai', '123456Aa')
        )
    )
    channel = connection.channel()
    channel.queue_declare(queue='nextfarm_ai_message')
    method_frame, header_frame, body = channel.basic_get(queue='nextfarm_ai_message')
    if method_frame:
        channel.basic_ack(method_frame.delivery_tag)
        return f'Message received: {body}'
    else:
        return 'No message in queue'

#cũng là test nhưng xem tất tin nhắn
messages = []
def process_message(channel, method_frame, header_frame, body):
    message = body.decode('utf-8')
    messages.append(message)
    channel.basic_ack(delivery_tag=method_frame.delivery_tag)

@app.route('/listen_message')
def listen_message():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host='125.212.228.171',
            port=5672,
            virtual_host='nextfarm',
            credentials=pika.PlainCredentials('ai', '123456Aa')
        )
    )
    channel = connection.channel()
    channel.queue_declare(queue='nextfarm_ai_message')
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='nextfarm_ai_message', on_message_callback=process_message)
    channel.start_consuming()
    return 'Listening for messages...'
    # return jsonify(messages)


@app.route('/get_messages')
def get_messages():
    return jsonify(messages)

#test ok 

#test đa luồng

# messages = []

# def process_message(channel, method_frame, header_frame, body):
#     message = body.decode('utf-8')
#     messages.append(message)
#     channel.basic_ack(delivery_tag=method_frame.delivery_tag)

# @app.route('/get_messages')
# def get_messages():
#     return jsonify(messages)

# def start_listening():
#     connection = pika.BlockingConnection(
#         pika.ConnectionParameters(
#             host='125.212.228.171',
#             port=5672,
#             virtual_host='nextfarm',
#             credentials=pika.PlainCredentials('ai', '123456Aa')
#         )
#     )
#     channel = connection.channel()
#     channel.queue_declare(queue='nextfarm_ai_message')
#     channel.basic_qos(prefetch_count=1)
#     channel.basic_consume(queue='nextfarm_ai_message', on_message_callback=process_message)
#     channel.start_consuming()


#get img test
list_img = []
def process_img(channel, method_frame, header_frame, body):
    list_img = body.decode('utf-8')
    list_img.append(list_img)
    channel.basic_ack(delivery_tag=method_frame.delivery_tag)

@app.route('/listen_img')
def listen_img():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host='125.212.228.171',
            port=5672,
            virtual_host='nextfarm',
            credentials=pika.PlainCredentials('ai', '123456Aa')
        )
    )
    channel = connection.channel()
    channel.queue_declare(queue='nextfarm_ai_data')
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='nextfarm_ai_data', on_message_callback=process_message)
    channel.start_consuming()
    return 'Listening for img...'
    # return jsonify(messages)


@app.route('/get_img')
def get_img():
    return jsonify(list_img)

if __name__ == "__main__":
    # listener_thread = threading.Thread(target=start_listening)
    # listener_thread.start()
    app.run(port=5000,debug=True)