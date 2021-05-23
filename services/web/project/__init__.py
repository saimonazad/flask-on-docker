import os

from werkzeug.utils import secure_filename
from flask import(
    Flask,
    jsonify,
    send_from_directory,
    request,
    redirect,
    url_for
)
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object("project.config.Config")
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    image = db.Column(db.String(128), nullable=False)

    def __init__(self, id, name, image):
        self.id = id
        self.name = name
        self.image = image


@app.route("/")
def hello_world():
    return jsonify(hello="world")


@app.route("/static/<path:filename>")
def staticfiles(filename):
    return send_from_directory(app.config["STATIC_FOLDER"], filename)


@app.route("/media/<path:filename>")
def mediafiles(filename):
    return send_from_directory(app.config["MEDIA_FOLDER"], filename)


@app.route("/upload", methods=["GET", "POST"])
def user():
    if ('image' not in request.files):
        resp = jsonify({'message' : 'No file part in the request'})
        resp.status_code = 400
        return resp
    else:
        try:
            id = request.values['id']
            name = request.values['name']
            image = request.files['image']
            filename = secure_filename(image.filename)
            if filename == '':
                resp = jsonify({'message' : 'No file selected for uploading'})
                resp.status_code = 400
                return resp
            else:
                image.save(os.path.join(app.config["MEDIA_FOLDER"], filename))
                
            user = User(id, name, filename)
            db.session.add(user)
            db.session.commit()
            return jsonify({'id': id,'name': name, 'image': filename}), 201
            
        except Exception as e:
            return jsonify({'message' : e}), 400
