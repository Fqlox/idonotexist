from main_function import base64Input

from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS, cross_origin
import base64

app = Flask(__name__)

app.config['JSON_AS_ASCII'] = False
app.config['JSON_SORT_KEYS'] = False
app.config['CORS_HEADERS'] = 'Content-Type'

cors = CORS(app, resources={r"/*": {"origins": "*"}})


@app.route("/post_image", methods=["POST"])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def process_image():
    r = request.get_data() 
    r_64 = base64.b64encode(r)


    #file = request.files['image']
    # Read the image via file.stream
    #img = Image.open(file.stream)
    #print(file.stream)
    return base64Input(r_64)




@app.route('/<path:path>', methods=['GET'])
def send_files(path):
    return send_from_directory('static', path)


@app.route("/")
def index():
    print("hshjszkszhjszhs")
    return send_from_directory('static', 'index.html')









if __name__ == "__main__":
    app.run(debug=True,
            #static_url_path='/dist',
            #host="192.168.0.33")
            host="127.0.0.1")



