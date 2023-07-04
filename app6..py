from keras.models import load_model
import cv2
from matplotlib import pyplot as plt
import tensorflow as tf
import os
import pika
import numpy as np
import threading
import requests
from io import BytesIO
from PIL import Image
from flask import Flask,render_template,request , jsonify, Response

sess = tf.compat.v1.Session()
graph = tf.compat.v1.get_default_graph()

#load model 
model = load_model("models/new_model3.h5")
#ham tai anh và sử lý ảnh 
def process_image_from_url(url):
    headers = ""
    # Gửi yêu cầu HTTP GET để tải xuống dữ liệu ảnh từ URL
    response = requests.get(url=url,headers=headers)
    
    # Kiểm tra mã trạng thái của yêu cầu
    if response.status_code != 200:
        raise ValueError(f"Failed to download image from {url}")
    
    # Tạo đối tượng Image từ dữ liệu ảnh trong bộ nhớ
    image = Image.open(BytesIO(response.content))
    img = tf.convert_to_tensor(np.array(image))
    
    # Xử lý ảnh
    resize = tf.image.resize(img, (256,256))
    yhat = model.predict(np.expand_dims(resize/255, 0))
    return yhat
    # image.show()
    
    # Trả về ảnh đã được xử lý
    # return image
    # return print(type(image))
#ham gửi message
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
    
    channel.basic_publish(
        exchange='',
        routing_key='nextfarm_ai_message',
        body=message
    )
    connection.close()
    return 'Message sent successfully'

#ham gửi img url
def send_img_url(url):
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
    channel.basic_publish(
        exchange='',
        routing_key='nextfarm_ai_data',
        body=url
    )
    connection.close()
    return 'Url sent successfully'


app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
#da luồng để lấy cái queue
def start_consuming():
    thread = threading.Thread(target=consume_queue)
    thread.start()
    return render_template('index7.html')

@app.route('/upload', methods=['GET', 'POST'])
#da luồng để lấy cái queue
# def start_consuming():
#     thread = threading.Thread(target=consume_queue)
#     thread.start()
#     return render_template('index7.html')
def upload():
    if request.method == "POST":

        # url = request.form['url']
        url = request.form.get('url') 
        send_img_url(url)
    
    
        return render_template("index7.html",url_img = url)
    

    #upload ảnh và sử lý
# def upload_file():
#     ketqua = ""
#     if request.method == 'POST':
#         # lấy file 
#         file = request.files['file']
        
#         #Trường hợp 1 : ko lưu ảnh , xử lý luôn
#         npimg = np.fromstring(file.read(), np.uint8)
#         img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

#         #trường hợp 2 : save img , rồi load ảnh từ chỗ lưu để xử lý
#         # if not os.path.exists('img_save_by_flask'):
#         #     os.makedirs('img_save_by_flask')
#         # filename = file.filename
#         # file.save(os.path.join('img_save_by_flask', filename))
#         # img = cv2.imread(f"img_save_by_flask/{filename}")

#         resize = tf.image.resize(img, (256,256))
#         yhat = model.predict(np.expand_dims(resize/255, 0))
#         if yhat > 0.5: 
#             # return "potato"
#             # send_to_rabbitmq("potato")
#             send_message("potato")
#             return render_template("index7.html",ketqua = "potato")
            
#         else:
#             # return "apple"
#             # send_to_rabbitmq("apple")
#             send_message("apple")
#             return render_template("index7.html",ketqua = "apple")

            
#         return 'File uploaded successfully!'
#     return render_template('index7.html')


#gửi message lên queue
# @app.route('/send_message_to_queue')
# def send_message_to_queue():
#     # if response.status_code == 200:
#     #     image_content = response.content
#     return

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


#upload img url

# @app.route('/upload_img', methods=['POST'])
# def upload():
#     url = request.form['url']
#     send_img_url(url)
#     # xử lý url ở đây
#     return "Đã upload URL: {}".format(url)

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

@app.route('/receive_img_url')
def receive_url_img():
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
    method_frame, header_frame, body = channel.basic_get(queue='nextfarm_ai_data')
    if method_frame:
        channel.basic_ack(method_frame.delivery_tag)
        return f'url received: {body}'
    else:
        return 'No url in queue'

@app.route('/get_img')
def get_img():
    return jsonify(list_img)

#xử lý lấy queue liên tục 
def callback(ch, method, properties, body):
    # Xử lý message ở đây
    data = body.decode('utf-8')
    yhat  = process_image_from_url(data)
    print(f"yhat = {yhat}")
    if yhat > 0.5: 
            # return "potato"
            # send_to_rabbitmq("potato")
            send_message("potato")
            # return render_template("index7.html",ketqua = "potato")
            
    else:
            # return "apple"
            # send_to_rabbitmq("apple")
            send_message("apple")
            # return render_template("index7.html",ketqua = "apple")
    # print(f"Received message: {data}")

def consume_queue():
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
    channel.basic_consume(queue='nextfarm_ai_data', on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

# chạy app đa luồng khi start-consuming được chạy
# @app.route('/start_consuming')
# def start_consuming():
#     thread = threading.Thread(target=consume_queue)
#     thread.start()
#     return 'Started consuming from queue'


if __name__ == "__main__":
    # listener_thread = threading.Thread(target=start_listening)
    # listener_thread.start()
    app.run(port=5000,debug=True)