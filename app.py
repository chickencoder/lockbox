import os
from hashlib import md5
from flask import Flask, request, flash, redirect, url_for, send_from_directory, jsonify
from flask import render_template
from werkzeug.utils import secure_filename
from lockbox.database import init_db, db_session
from lockbox.models import File

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.secret_key = "SUPERSECRET"
app.config.update(
    UPLOAD_FOLDER=os.getcwd() + "/uploads/",
    MAX_CONTENT_LENGTH=1024*1024*1024,
    CELERY_BROKER_URL='sqlite:///storage.db',
    CELERY_RESULT_BACKEND='sqlite:///storage.db'
)

# Initialise Database Connection
init_db()

def generate_passcode(filename, iteration):
    return str(md5(filename.encode("utf-8") + str(iteration).encode("utf-8")).hexdigest()[:4]).upper()

def hash_passcode(passcode):
    # Use the secret key as the salt
    # hash(passcode + salt)
    return md5(passcode.encode("utf-8") + app.secret_key.encode("utf-8")).hexdigest()

def is_not_unique(passcode):
    if File.query.filter(File.file_passcode_hash == hash_passcode(passcode)).first():
        return True
    else:
        return False

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/help")
def help():
    return render_template("help.html")

@app.route('/uploads/<path:filename>')
def uploads_static(filename):
    return send_from_directory(app.root_path + '/uploads/', filename)

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        f = request.files['file']

        # Save file to disk
        f.save(app.config["UPLOAD_FOLDER"] + secure_filename(f.filename))

        # Generate a unqiue filename
        fname = secure_filename(f.filename)
        validFileName = False
        iteration = 0
        while not validFileName:
            if fname in os.listdir(app.config["UPLOAD_FOLDER"]):
                validFileName = True
            else:
                fname = secure_filename(str(iteration) + f.filename)
                iteration += 1

        # Generate the retreival code
        iteration = 0
        passcode = generate_passcode(fname, iteration)
        while is_not_unique(passcode):
            passcode = generate_passcode(fname, iteration)
            iteration += 1

        # Add to database
        parts = fname.split(".")
        ext = "Plain"
        if len(parts) > 1:
            ext = parts[1]

        path = app.config["UPLOAD_FOLDER"] + secure_filename(fname)
        size = os.stat(path).st_size

        # Let's set it to 24 hours
        timeout = 60 * 60 * 24

        # We'll use md5 to hash the passcode
        passcode_hash = hash_passcode(passcode)

        file = File(fname, ext, size, path, timeout, passcode_hash)
        db_session.add(file)
        db_session.commit()

        # Render uploaded
        return redirect(url_for("uploaded", passcode=passcode, filename=fname))
    else:
        return redirect("/")

@app.route("/uploaded")
def uploaded():
    passcode = request.args.get("passcode")
    filename = request.args.get("filename")
    return render_template("uploaded.html", passcode=passcode, filename=filename)

@app.route("/unlock", methods=["GET", "POST"])
def unlock():
    if request.method == "POST":
        # Query the database
        passcode = (request.form["entry-0"] +
                    request.form["entry-1"] +
                    request.form["entry-2"] +
                    request.form["entry-3"]).upper()
        result = File.query.filter(File.file_passcode_hash == hash_passcode(passcode)).first()
        if result:
            file_path = result.file_name
            return render_template("unlocked.html", path=file_path)
        else:
            return render_template("/unlock.html", failed=True)
    else:
        return render_template("unlock.html", failed=False)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()