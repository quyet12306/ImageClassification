from keras.models import load_model
import cv2
from matplotlib import pyplot as plt
import tensorflow as tf
import os
import numpy as np
from flask import Flask,render_template,request 

sess = tf.compat.v1.Session()
graph = tf.compat.v1.get_default_graph()

# with sess.as_default():
#     with graph.as_default():
model = load_model("models/new_model3.h5")
app = Flask(__name__)





@app.route('/', methods=['GET', 'POST'])
def upload_file():
    ketqua = ""
    if request.method == 'POST':
        file = request.files['file']
        # Xử lý file ở đây
        # resize = tf.image.resize(file, (256,256))
        # # yhat = model.predict(np.expand_dims(resize/255, 0))
        # with sess.as_default():
        #     with graph.as_default():
        #         yhat = model.predict(np.expand_dims(resize/255, 0))
        # print(yhat)
        # if yhat > 0.5: 
        #     return "potato"
        #     print("potato")
        # else:
        #     return "apple"
        #     print("apple")

        #save img
        if not os.path.exists('img_save_by_flask'):
            os.makedirs('img_save_by_flask')
        filename = file.filename
        file.save(os.path.join('img_save_by_flask', filename))
        img = cv2.imread(f"img_save_by_flask/{filename}")
        resize = tf.image.resize(img, (256,256))
        yhat = model.predict(np.expand_dims(resize/255, 0))
        if yhat > 0.5: 
            # return "potato"
            return render_template("index7.html",ketqua = "potato")
            
        else:
            # return "apple"
            return render_template("index7.html",ketqua = "apple")

            
        return 'File uploaded successfully!'
    return render_template('index7.html')

if __name__ == "__main__":
    app.run(port=5000,debug=True)