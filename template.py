##############SET UP 🙏🏾#####################
#Import Key Libraries: os, flask(response, request), pymango, json, bson.objectid objectid
from os import name
from flask import Flask, Response, request, render_template, flash, redirect, url_for
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
import pymongo
import json

from bson.objectid import ObjectId
#Instantiate app
app = Flask(__name__)

#****************DB Connection imte🌍**************
connection_string = ''
client = pymongo.MongoClient(connection_string, serverSelectionTimeoutMS=5000)
##Check if the connection was made to the DB
try:
    print("Connected to Database")
    # This code will show the client info, use to test connectivity
    print(client.server_info())
    db = client.<database name>
except Exception:
    print("Unable to connect to the server.")
    # print(client)

##############Routes 🙏🏾#####################



#Create Routes 🦾
@app.route("/users", methods=["POST"])
def foo(
    try:
        #😋 FRONT END WINDOW
        ##object_var = Module.Model(request.form)

        #If logic for POST verb
        #Create an object of the model you which to make
        #make DB connection and use an action method
        #print/track key identifiers

        #Return Response tree
        return Response(
            #response data
            response = json.dumps(
                {"message": "user created", 
                "id": f"{dbResponse.inserted_id}"
                }),
            status = 200,
            mimetype='application/json'
        ) and render_template('stuff.html')
    except Exception as ex:
        pass
    # return render_template('add_article.html', form=actual_user)
)
#Read Routes 👀


#Update Routes 🦿

#Delete Routes 👣

if __name__ == "__main__":
    app.run(port = 80, debug=True)