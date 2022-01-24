from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from minio import Minio
import pymongo
import json
import os
from pymongo import MongoClient

load_dotenv()

# LOCAL_FILE_PATH = os.environ.get('LOCAL_FILE_PATH')
ACCESS_KEY      = os.environ.get('ACCESS_KEY')
SECRET_KEY      = os.environ.get('SECRET_KEY')

cluster = MongoClient(os.environ.get('MONGO_URI'))
db = cluster["TactDraw"]
col = db["Details"]

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
  
    return images



def get_all_videos():
    
    videos=[]

    for single_object in MINIO_CLIENT.list_objects(BUCKET_NAME, recursive=True):

        if single_object.object_name.endswith((".mp4")):
            videos.append(single_object.object_name)

    videos = [f"{MINIO_API_HOST}/{BUCKET_NAME}/{video}" for video in videos]
    
    return videos

@app.route('/')
def index():
    names = get_details()
    
    all_images = get_all_images()

    all_videos = get_all_videos()

    return render_template('index.html', images = all_images, videos =all_videos,names = names)


@app.route('/add', methods = ['GET', 'POST'])
def upload_files():
    
    if request.method == 'POST':

        name             = request.values.get("name")
        mail_id          = request.values.get("mailid")
        phone_no         = request.values.get("phno")
        uploaded_file    = request.files['file']

        global filename
        filename = secure_filename(uploaded_file.filename)
        if filename != '':
            file_ext = os.path.splitext(filename)[1]
            uploaded_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        global LOCAL_FILE_PATH
        LOCAL_FILE_PATH = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        my_dict = {}
 
        my_dict ["Name"]                = name
        my_dict ["mail_id"]             = mail_id
        my_dict ["phone_no "]           = phone_no 
        my_dict ["uploaded_file"]       = filename


        found = MINIO_CLIENT.bucket_exists("first")
        if not found:
            MINIO_CLIENT.make_bucket("first")
        else:
            print("Bucket already exists")
        MINIO_CLIENT.fput_object("first",filename,LOCAL_FILE_PATH,)       
        print("It is successfully uploaded")

        all_images = get_all_images()
        all_videos = get_all_videos()

        my_dict["url"] =  get_url(filename)

        upload_details(my_dict)

        names = get_details()

        return render_template('index.html', images = all_images, videos =all_videos, names = names)

    return render_template('upload.html')


def get_url(filename):

    for single_object in MINIO_CLIENT.list_objects(BUCKET_NAME, recursive=True):

        if (single_object.object_name.endswith((".jpg", ".png", ".jpeg",))) and  single_object.object_name == filename :

          images = f"{MINIO_API_HOST}/{BUCKET_NAME}/{single_object.object_name}"

          break
  
    return images


def upload_details(my_dict):

    x = col.insert_one(my_dict)

    return x

def get_details():

    name = []
    for x in col.find({},{ "_id":0,"Name": 1, "uploaded_file": 1, "url":1}):
        name.append(x)

    return name


if __name__ == "__main__":
    
    app.run(debug=True,host="0.0.0.0",port="3012")


     
        # if os.stat(f"users.json").st_size==0:
        #     global user_dict
        #     user_dict={}
        #     user_dict.update(my_dict)
        # else:


        #filename='users.json'
        # with open( f"users.json", "r+") as outfile:

        #     file_data= json.load(outfile)
        #     print(file_data)
        #     file_data.update(my_dict)
        #     #outfile.seek(0)

        #     outfile.write(json.dumps(file_data))


        # with open( f"users.json", "r+") as outfile:
        #     file_data = json.load(outfile)
        #     print(file_data)
        #     file_data['users'][name]=my_dict
        #     #outfile.seek(0)

        #     outfile.write(json.dumps(file_data))

        #except json.decoder.JSONDecodeError:
            #file_data



