import os, sys, stat, requests
from typing import final
from bson import objectid
from flask import Flask, Response, request, render_template, flash, redirect, url_for, session, logging
from datetime import date
from werkzeug.utils import secure_filename
from wtforms import Form, StringField, TextAreaField, PasswordField, form, validators
import pymongo


app = Flask("Helpful_Food_App")

@app.route("/", methods = ["GET", "POST"])
def landing():
    return(f"Hello World- {os.environ}")
# app.run(debug=True)
port = int(os.environ.get("PORT", 5000))
app.run(host='0.0.0.0', port=port, debug=True)