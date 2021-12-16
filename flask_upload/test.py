import os, csv
import pandas as pd
from flask import (
    Flask,
    request,
    redirect,
    url_for,
    render_template,
    send_from_directory,
    send_file,
)
from werkzeug.utils import secure_filename
from subprocess import Popen, PIPE, run
import subprocess


UPLOAD_FOLDER = "./tmp/"
ALLOWED_EXTENSIONS = {"csv"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# layout
@app.route("/")
def main():
    return render_template("buttons_trial.html")


# main page
@app.route("/home")
def home():
    return render_template("home.html", title="Home")


# about page
@app.route("/about")
def about():
    return render_template("about.html", title="About")


# run R - SAIGE
def run_R_saige(file):
    p = subprocess.check_output(
        ["Rscript groupfile.R SAIGE-GENE" + file + "All"],
        shell=True,
        stderr=subprocess.DEVNULL,
    )
    return p


# run R - SKAT
def run_R_skat(file):
    p = subprocess.check_output(
        ["Rscript groupfile.R SKAT" + file + "All"],
        shell=True,
        stderr=subprocess.DEVNULL,
    )
    return p


# set allowed file
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1] in ALLOWED_EXTENSIONS


# download file
@app.route("/upload/<name>")
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)


# code to run saige
@app.route("/upload_run_saige", methods=["GET", "POST"])
def upload_run_saige():
    if request.method == "POST":
        # check if the post request has the file part
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files["file"]
        # if the user doesn't select a file, the browser submits an empty file without filename
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        run_R_saige(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        return send_file("./groupfile.txt", as_attachment=True)
    return render_template("upload_saige.html")


# code to run skat
@app.route("/upload_run_skat", methods=["GET", "POST"])
def upload_run_skat():
    if request.method == "POST":
        # check if the post request has the file part
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files["file"]
        # if the user doesn't select a file, the browser submits an empty file without filename
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        run_R_skat(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        return send_file("./groupfile.txt", as_attachment=True)
    return render_template("upload_skat.html")


# select SAIGE/SKAT
@app.route("/upload")
def index():
    return render_template(
        "selectSaigeSkat.html", data=[{"name": "SAIGE-GENE"}, {"name": "SKAT"}]
    )


# send user selection to corresponding SAIGE/SKAT view functions
@app.route("/test", methods=["GET", "POST"])
def test():
    select = str(request.form.get("comp_select"))
    if select == "SAIGE-GENE":
        return redirect(url_for("upload_run_saige"))
    if select == "SKAT":
        return redirect(url_for("upload_run_skat"))


if __name__ == "__main__":
    app.run(debug=True)
