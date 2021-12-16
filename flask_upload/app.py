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
import matplotlib.pyplot as plt
import numpy as np
import pylab
import json, jsonify
import plotly
import plotly.express as px
from flask_wtf import FlaskForm
from wtforms import widgets, SelectMultipleField


SECRET_KEY = "development"
UPLOAD_FOLDER = "./tmp/"
ALLOWED_EXTENSIONS = {"csv"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config.from_object(__name__)


# layout


@app.route("/")
def main():
    return render_template("upload.html")


@app.route("/ensembl")
def ensembl():
    return render_template("ensembl2.html")


# main page


@app.route("/home")
def home():
    return render_template("home.html", title="Home")


# about page


@app.route("/about")
def about():
    return render_template("about.html", title="About")


# download file
@app.route("/upload/<name>")
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)


# upload file
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1] in ALLOWED_EXTENSIONS


# run R script
def run_R(file):
    p = subprocess.check_output(
        ["Rscript groupfile.R SAIGE-GENE" + file + "All"],
        shell=True,
        stderr=subprocess.DEVNULL,
    )
    return p


@app.route("/upload", methods=["GET", "POST"])
def upload_file():
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
        # run_R(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        # return send_file("./groupfile.txt", as_attachment=True)
    return render_template("upload.html")


@app.route("/pie", methods=["GET", "POST"])
def index():
    return render_template("index_image.html")


@app.route("/num_genes", methods=["GET", "POST"])
def number_genes():
    data = pd.read_csv("./tmp/annovar_output_example.csv")
    result_1 = str(len(data["Gene.refGene"].unique()))
    return result_1


@app.route("/pie_function", methods=["GET", "POST"])
def summary_function():
    data = pd.read_csv("./tmp/annovar_output_example.csv")
    # generate plot
    result_2 = pd.DataFrame(data["Func.refGene"].value_counts(normalize=True))
    result_2.index.name = "function"
    result_2.reset_index(inplace=True)
    result_2 = result_2.rename(columns={"Func.refGene": "ratio"})

    fig = px.pie(result_2, values="ratio", names="function")
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    header = "Pie Chart for Gene Function"

    return render_template("image.html", graphJSON=graphJSON, header=header)


@app.route("/pie_exonic_function", methods=["GET", "POST"])
def summary_exonic():
    data = pd.read_csv("./tmp/annovar_output_example.csv")

    # generate plot
    result_3 = data["ExonicFunc.refGene"]
    result_3 = result_3[result_3 != "."]
    result_3 = pd.DataFrame(result_3.value_counts(normalize=True))
    result_3.index.name = "exonic_function"
    result_3.reset_index(inplace=True)
    result_3 = result_3.rename(columns={"ExonicFunc.refGene": "ratio"})

    fig = px.pie(result_3, values="ratio", names="exonic_function")
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    header = "Pie Chart for Exonic Gene Function"

    return render_template("image.html", graphJSON=graphJSON, header=header)


# select options
@app.route("/trial", methods=["GET", "POST"])
def trial():
    if request.method == "POST":
        options = str(request.form.getlist("test_option"))
    return options


# run R script with selected options
@app.route("/options", methods=["GET", "POST"])
def run_R_options(file):
    if request.method == "POST":
        options = str(request.form.getlist("test_option"))

    p = subprocess.check_output(
        ["Rscript groupfile.R SAIGE-GENE" + file + options],
        shell=True,
        stderr=subprocess.DEVNULL,
    )


if __name__ == "__main__":
    app.run(debug=True)
