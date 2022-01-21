from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from minio import Minio
import os

load_dotenv()

# LOCAL_FILE_PATH = os.environ.get('LOCAL_FILE_PATH')
ACCESS_KEY      = os.environ.get('ACCESS_KEY')
SECRET_KEY      = os.environ.get('SECRET_KEY')

app = Flask(__name__)

MINIO_API_HOST = "http://" + os.environ.get('PUB_IP_ADDRESS') + ":9000"

MINIO_CLIENT = Minio(os.environ.get('PUB_IP_ADDRESS') + ":9000", access_key=ACCESS_KEY, secret_key=SECRET_KEY, secure=False)

BUCKET_NAME = "first"

UPLOAD_PATH = "data/"

app.config['UPLOAD_FOLDER'] = UPLOAD_PATH

def get_all_images():

    images = []

    for single_object in MINIO_CLIENT.list_objects(BUCKET_NAME, recursive=True):

        if single_object.object_name.endswith((".jpg", ".png", ".jpeg",)):

            images.append(single_object.object_name)

    images = [f"{MINIO_API_HOST}/{BUCKET_NAME}/{image}" for image in images]
  
    print(images)
    return images

def get_all_videos():
    
    videos=[]

    for single_object in MINIO_CLIENT.list_objects(BUCKET_NAME, recursive=True):

        if single_object.object_name.endswith((".mp4")):
            videos.append(single_object.object_name)

    videos = [f"{MINIO_API_HOST}/{BUCKET_NAME}/{video}" for video in videos]
    
    print(videos)
    return videos

@app.route('/')
def index():
    all_images = get_all_images()

    all_videos = get_all_videos()

    return render_template('index.html', images = all_images, videos =all_videos)

@app.route('/add', methods = ['GET', 'POST'])
def upload_files():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        global filename
        filename = secure_filename(uploaded_file.filename)
        if filename != '':
            file_ext = os.path.splitext(filename)[1]
            uploaded_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        global LOCAL_FILE_PATH
        LOCAL_FILE_PATH = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        found = MINIO_CLIENT.bucket_exists("first")

        if not found:
            MINIO_CLIENT.make_bucket("first")
        else:
            print("Bucket already exists")

        MINIO_CLIENT.fput_object("first", filename,LOCAL_FILE_PATH,)
        
        print("It is successfully uploaded")

        all_images = get_all_images()

        all_videos = get_all_videos()

        return render_template('index.html', images = all_images, videos =all_videos)

    return render_template('upload.html')

if __name__ == "__main__":
    
    app.run(debug=True,host="0.0.0.0",port="3012")


