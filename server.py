######################################################################********************************SET UP 🙏🏾********************************#################################################
#Import Key Libraries: os, flask(response, request), pymango, json, bson.objectid objectid
import os, sys, stat, requests
from typing import final
from bson import objectid
from flask import Flask, Response, request, render_template, flash, redirect, url_for, session, logging
from datetime import date
from werkzeug.utils import secure_filename
from wtforms import Form, StringField, TextAreaField, PasswordField, form, validators
import pymongo
from flask_mysqldb import MySQL
from getpass import getpass
import mysql.connector
from mysql.connector import connect, Error

import json
from bson.objectid import ObjectId
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from jwt_okta_middleware import is_access_token_valid, is_id_token_valid, config
#Instantiate app
app = Flask(__name__)
#************************************************DB Connection 🌍**********************************************
#Pull DB Config for NoSQL and SQL
db_config_data = None
with open('db_credentials.json') as f:
    db_config_data = json.load(f)
#Prepping NoSQL Connection string
connection_string_array = [db_config_data['mongodb'][key] for key in db_config_data['mongodb'].keys()]
connection_string_NoSQL = "".join(connection_string_array)
client = pymongo.MongoClient(connection_string_NoSQL, serverSelectionTimeoutMS=15000)
##Check if the connection was made to the DBs
try:
    # Check for NoSQL connection
    db = client.Adulting_Food
    print("Connected to Admin/Dev Mongo Database  😁: ", "availible data collections are - ", db.list_collection_names() )
    #Prep SQL Connection
    mysqldb = mysql.connector.connect(
    host=db_config_data['mysql']['MYSQL_ADDON_HOST'],
    user=db_config_data['mysql']['MYSQL_ADDON_USER'],
    password=db_config_data['mysql']['MYSQL_ADDON_PASSWORD'],
    database = db_config_data['mysql']['MYSQL_ADDON_DB']
    )
    mycursor = mysqldb.cursor()
    mycursor.execute("SHOW TABLES")
    print("SQL DB Connection Successful, tables below 😁: ")
    for x in mycursor:
        print (x)
except Exception:
    print("Unable to connect to the server.")
#Identity and Access Mangement - LOGIN and LOGOUT 🚪
#Creating, Loging In, Validating a User
from Models_Plan import User
app.config.update({'SECRET_KEY': 'SomethingNotEntirelySecret'}) #used to sign off on tokens
login_manager = LoginManager()
login_manager.init_app(app)
APP_STATE = 'ApplicationState'
NONCE = 'SampleNonce'
app.config["SESSION_PERMANENT"] = False

@login_manager.user_loader
def load_user(user_id):
    dbAction = db.users.find_one({"OKTAid": user_id})
    unique_id = dbAction["OKTAid"]
    user_email = dbAction["email"]
    user_firstName = dbAction["firstName"]
    user_lastName = dbAction["lastName"]
    user_displayname = dbAction["displayname"]
    user_fullName = dbAction["name"]
    user = User(
        id_= unique_id,
        name = user_fullName,
        email = user_email,
        preferred_username= user_displayname,
        given_name= user_firstName,
        family_name= user_lastName
    )
    return user

# Authorization Code Request to/authorize, redirect to the Okta Widget, then enter credentials for AuthN!
@app.route("/login")
def login():
    # get request params
    query_params = {'client_id': config["web"]["client_id"],
                    'redirect_uri': config["web"]["redirect_uri"],
                    'scope': "openid email profile",
                    'state': APP_STATE,
                    'nonce': NONCE,
                    'response_type': 'code',
                    'response_mode': 'query'}
    # build request_uri
    request_uri = "{base_url}?{query_params}".format(
        base_url=config["web"]["auth_uri"],
        query_params=requests.compat.urlencode(query_params)
    )
    return redirect(request_uri) #Redirect to OKTA

##############Steps 4-6 OIDC Token Exchange  i
#you get redirect to this endpoint from OKTA to begin token exchange
@app.route("/authorization-code/callback")  # Step 4 Redirect to authentication prompt
def callback():
    # global user_custom_NoSQLdatabase
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    code = request.args.get("code") #Step 4 AuthZ code response
    if not code:
        return "The code was not returned or is not accessible", 403
    query_params = {'grant_type': 'authorization_code',
                    'code': code,
                    'redirect_uri': request.base_url
                    }
    query_params = requests.compat.urlencode(query_params)
    #This is where the token exchange begins, we send in the token URI from the app
    #pass in wuth credentials (client ID and secret)
    #OKTA hoepfully sends back access and ID tokens
    exchange = requests.post(
        config["web"]["token_uri"],
        headers=headers,
        data=query_params,
        auth=(config["web"]["client_id"], config["web"]["client_secret"]),
    ).json() ##############STEP 5 sending credentials to toekn endpoint

    # Get tokens and validate
    if not exchange.get("token_type"):
        return "Unsupported token type. Should be 'Bearer'.", 403
    access_token = exchange["access_token"]  
    id_token = exchange["id_token"]
    print("#access TOKEN - 🟢: \n"f"{access_token}\n" +  " #identity TOKEN - 🔵: \n"f"{id_token}")
    if not is_access_token_valid(access_token, config["web"]["issuer"]):
        return "Access token is invalid", 403
    if not is_id_token_valid(id_token, config["web"]["issuer"], config["web"]["client_id"], NONCE):
        return "ID token is invalid", 403
    
    #If tokens are exhcnages successfully then we get user credentials
    # Authorization flow successful, get userinfo and login user
    userinfo_response = requests.get(config["web"]["userinfo_uri"],  headers={'Authorization': f'Bearer {access_token}'}).json()
    # for item in userinfo_response.keys():
    #     print(userinfo_response.keys())
    unique_id = userinfo_response["sub"]
    user_email = userinfo_response["email"]
    user_firstName = userinfo_response["given_name"]
    user_lastName = userinfo_response["family_name"]
    user_displayname = userinfo_response["preferred_username"]
    user_fullName = userinfo_response["name"]
    #Write to Users Database
    user = User(
        id_= unique_id,
        name = user_fullName,
        email = user_email,
        preferred_username= user_displayname,
        given_name= user_firstName,
        family_name= user_lastName
    )
    session["user"] = user.export()
    find_already = db.users.find_one({"OKTAid": unique_id})
    
    if find_already is None:
        dbAction = db.users.insert_one(user.export())
    
    login_user(user)
    
    return redirect(url_for("profile"))
#presents the profile endpoint from your app

#Create Custom User NoSQLDB Connections
def create_user_NoSQLdatabases():
    holder_user = session['user']
    NoSQLConnection = client[str(holder_user['OKTAid'])]
    return NoSQLConnection
def print_collections(NoSQLConnection):
    for collection in NoSQLConnection.list_collection_names():
        print(collection)
@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html", user = current_user)

@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect("/")
#Rules of the road
#**** forcing U&D routes access via the front end only (unless you want to remember ids)

###❗Testing Prices Middleware => will add feature to groceriy table
from krogger_middleware import get_zip_code, configuration_var, Engine, authorize, store_locator, product_price
@app.route("/price", methods = ['GET'])
def tester():
    bearer = authorize()
    zip_code = get_zip_code()
    locationids = store_locator(zip_code, bearer)
    product_price("milk", bearer, 70200931)
    # for location in locationids:
    #     product_price("milk", bearer,70200931)
    return "Done"

#************************************************Configuration for File Uploads 📂**************
upload_folder = "static/"
if not os.path.exists(upload_folder):
   os.mkdir(upload_folder)
app.config['UPLOAD_FOLDER'] = upload_folder
app.secret_key = 'whatitiscuhwhatisup'
#######################********************************Handles File Uploads ⬆
def uploadfile(id, route_indicator):
    if request.method == 'POST':
        f = request.files['file'] # get the file from the files object
        uploaded_image_name =f.filename[f.filename.find("-")+1: f.filename.find(".")]
        if os.getcwd().find("static") < 0:
            os.chdir(os.getcwd()+ '/static')
        if f.filename =="":
            for file in os.listdir(os.getcwd()):
            #👁‍🗨Edit string slicing
                img_search = file[file.find("_")+1: file.find("-")]
                handle = file[0: file.find("_")]
                if (img_search == id and handle == route_indicator):
                    return file
                else:
                     return " "
        else:
            for file in os.listdir(os.getcwd()):
                #👁‍🗨Edit string slicing
                img_search = file[file.find("-")+1: file.find(".")]
                handle = file[0: file.find("_")]
                # print(uploaded_image_name + " : "+ handle + " : " + img_search)
                if (img_search == uploaded_image_name and handle == route_indicator):
                    os.remove(file)
                    flash('Old Picture Deleted upload new picture', 'success')
        if os.getcwd().find("static") < 0:
            os.chdir(os.getcwd()+ '/static')
        # Saving the file in the required destination
        #👁‍🗨Edit string slicing
        f.save(secure_filename(route_indicator+"_"+ id + "-" + f.filename))
      #Get file path from the folder
        if os.getcwd().find("static") < 0:
            os.chdir(os.getcwd()+ '/static')
        for file in os.listdir(os.getcwd()):
            handle = file[0: file.find("_")]
            img_search = file[file.find("_")+1: file.find("-")]
            if (img_search == id and handle == route_indicator):
                img_file = file
        return img_file

######################################################################********************************Routes 🧳****************#################################################
#Home Route ✅[FE finish]
@app.route("/", methods = ["GET", "POST"])
def landing():
    return render_template("home.html")

#############********************************************************************Ingridients 🍍
from Models_Plan import Ingredient

##########################################Create Routes 🦾
#Create  an Ingredient ✅[FE finish]
@app.route("/ingredient", methods=["GET","POST"])
@login_required
def create_ingredient():
    #this binds form entries to the object class, it's like saying all the 
    #let the data entered in the form or postman map to the attributes defined in the class
    ###👁‍🗨so does 2 things, sends form entries to class attributes and let's you use class methods!!!!
    form = Ingredient(request.form)
    if request.method == "POST" and form.validate():
        try:    
            dbAction = db.ingredients.insert_one(form.export())
            form.img_URI = uploadfile(str(dbAction.inserted_id), 'Ingredient')
            dbUpdate_image = db.ingredients.update_one({"_id": dbAction.inserted_id},{'$set':{'img_URI': form.img_URI}})
            flash("Ingredient Added!", 'success')
            return Response(
                response = json.dumps(
                        {"message": "ingridient created", 
                        "id": f"{dbAction.inserted_id}"
                        }),
                    status = 200,
                    mimetype='application/json'
            ) and redirect('/ingredient/'f"{dbAction.inserted_id}")
        except Exception as ex:
            return Response(
                    response = json.dumps(
                            {"message": "Unable to Create Ingredient"
                            }),
                        status = 400,
                        mimetype='application/json'
                )
    return render_template('/create_ingredient.html', form=form)
 
######################################Read/Search Routes 📚
#Standard Read by ID route ✅[FE finish]
@app.route('/ingredient/<id>', methods = ['GET'])
def read_ingredient_standard(id):
    if request.method == 'GET':
        try:
            dbConfirm = db.ingredients.find_one({"_id": ObjectId(id)})
            #Search Recipe DB to pull out recipes with this ingredient
            #Search Grocereis DB to pull list/times this has been references over time
            return Response(
                        response = json.dumps(
                                {"message": "Ingredient found", 
                                "id": f"{dbConfirm['_id']}",
                                "name": f"{dbConfirm['title']}",
                                }),
                            status = 200,
                            mimetype='application/json'
                    ) and render_template('read_ingredient.html', ingredient = dbConfirm)
        except Exception as ex:
            return Response(
                    response = json.dumps(
                            {"message": "Unable to Retrieve"
                            }),
                        status = 400,
                        mimetype='application/json'
                )

#✅See All Ingredients in the DB
@app.route('/ingredient/all', methods = ['GET'])
def read_ingredients():
    if request.method == 'GET':
        try:
            all_ingredients = list(db.ingredients.find({}))
            return Response(
                    response = json.dumps(
                            {"message": "here are all the ingredients"
                            }),
                        status = 200,
                        mimetype='application/json'
                ) and render_template('read_ingredient_all.html', ingredients = all_ingredients)
        except  Exception as ex:
            return Response(
                    response = json.dumps(
                            {"message": "Unable to show all Ingredients"
                            }),
                        status = 400,
                        mimetype='application/json'
                )

#Complex Search against MongoDB✅   [FE finish]
@app.route('/ingredient/search_complex',  methods = ['GET', 'POST'])
def read_ingredient_search():
    form = request.form
    if request.method == 'POST':
        tree_filter = form['diselecta']
        tree_filter2 = tree_filter[tree_filter.find("by")+3: len(tree_filter)]
        search = form['dasearch']
        if tree_filter2 == '_id':
            search = ObjectId(search)
        try:   
            dbConfirm = db.ingredients.find({tree_filter2: search})
            dbData = list(dbConfirm)
            if len(dbData) == 1:
                for doc in dbData:
                    doc['_id'] = str(doc['_id'])
                return Response(
                    response = json.dumps(
                            {"message": "ingredient found", 
                            "id": f"{dbData[0]['_id']}",
                            "name": f"{dbData[0]['title']}",
                            }),
                        status = 200,
                        mimetype='application/json'
                ) and render_template('read_ingredient_search.html', ingredients = dbData, type_search = tree_filter2)
            elif len(dbData) >1 :
                for doc in dbData:
                    doc['_id'] = str(doc['_id'])
                return Response(
                    response = json.dumps({"message": "query made successfuly, returning array of ingredients"f"{dbData}"}),
                        status = 200,
                        mimetype='application/json'
                ) and render_template('read_ingredient_search.html', ingredients = dbData, type_search = tree_filter2)
        except Exception as ex:
            return Response(
                    response = json.dumps(
                            {"message": "Unable to Find Ingredient"
                            }),
                        status = 400,
                        mimetype='application/json'
                )
    return render_template('read_ingredient_search.html')
   
#Simple Search against MongoDB✅   [FE finish]
@app.route('/ingredient/search_simple',  methods = ['GET', 'POST'])
def read_ingredient_search2():
    form = request.form
    if request.method == 'GET':
        try:
            all_ingredients = list(db.ingredients.find({}))
            return Response(
                    response = json.dumps(
                            {"message": "Simple Search Against DB"
                            }),
                        status = 200,
                        mimetype='application/json'
                ) and render_template('read_ingredient_search2.html', ingredients = all_ingredients, desired_ingredient='all')
        except  Exception as ex:
           return Response(
                    response = json.dumps(
                            {"message": "Unable to show the page for some reason"
                            }),
                        status = 400,
                        mimetype='application/json'
                )
    if request.method == 'POST':
        try:
            hold = form.to_dict()
            searcher = hold['ingredients']
            dbAction = db.ingredients.find_one({"title": searcher})
            ingredient_id = dbAction["_id"]
            # return redirect("/ingredient/"f"{ingredient_id}")
            return Response(
                    response = json.dumps(
                            {"message": "here is your desired ingredient"
                            }),
                        status = 200,
                        mimetype='application/json'
                ) and render_template('read_ingredient_search2.html',desired_ingredient = str(ingredient_id))
            # return list(dbAction)
        except Exception as ex:
            return Response(
                    response = json.dumps(
                            {"message": "Unable to Find this Ingredient"
                            }),
                        status = 404,
                        mimetype='application/json'
                )

##Search against USGov DB (file)

##########################################Update Routes 🚅
#Standard update Route ✅ [FE finish]
@app.route('/ingredient/update/<id>', methods = ['GET', 'POST'])
@login_required
def update_ingredient(id):
    form = Ingredient(request.form)
    #Form Binding -Sets data in the form oject attributes to what's already in the database so when html template presents you see the previous data
    dbAction_findrecord = db.ingredients.find_one({"_id": ObjectId(id)})
    form.name.data = dbAction_findrecord['title']
    form.description.data = dbAction_findrecord['description']
    form.state.data = dbAction_findrecord['state']
    form.type.data = dbAction_findrecord['type']  
    if request.method == 'POST':
        # print(request.form.keys())
        try:
            #create variable placeholders to take any changes you make to the request.form object
            title = request.form['name']
            description = request.form['description']
            state = request.form['state']
            type_ingredient = str(request.form['type'])
            new_IMG_URI = uploadfile(str(id), "Ingredient")
            if new_IMG_URI == " ":
                new_IMG_URI = dbAction_findrecord['img_URI']
            dbAction = db.ingredients.update_one(
                {"_id": ObjectId(id)},
                {"$set": 
                    {
                    "title": title,
                    "description": description,
                    "state": state,
                    "type": type_ingredient,
                    "img_URI": new_IMG_URI,
                    "date_modified": str(date.today())
                    }
                }
            )
            flash('Ingredient Updated', 'success')
            return Response(
                response = json.dumps({"message": "query made successfuly, updated ingredient " f"{title}"}),
                status = 200,
                mimetype='application/json'
            ) and redirect('/ingredient/'f"{id}")
        except Exception as ex:
            return Response(
                    response = json.dumps(
                            {"message": "Unable to Update Ingredient"
                            }),
                        status = 400,
                        mimetype='application/json'
                )
    return render_template('/update_ingredient.html', form=form, current_state = form.state.data, current_type = dbAction_findrecord['type'])

###########################################Delete Route 🚮
@app.route('/ingredient/delete/<id>', methods = ['GET', 'POST'])
@login_required
def delete_ingredient(id):
    if request.method == 'GET':
        print("Ammount of documents before deletion:" f"{db.ingredients.count_documents({})}")
        try:
            dbAction = db.ingredients.delete_one({"_id": ObjectId(id)})
            print("Ammount of documents AFTER deletion:" f"{db.ingredients.count_documents({})}")
            #Delete Picture file as well
            #Get file path from the folder
            if os.getcwd().find("static") < 0:
                os.chdir(os.getcwd()+ '/static')
            flash('Ingredient Deleted', 'success')
            for file in os.listdir(os.getcwd()):
                img_search = file[file.find("_")+1: file.find("-")]
                # print(img_search)
                if (img_search == id):
                    os.remove(file)
            flash('Ingredient and image Deleted', 'success')
            return Response(
                response = json.dumps(
                            {"message": "ingredient Delete", 
                            "id": f"{id}"
                            }),
                        status = 200,
                        mimetype='application/json'
            ) and redirect(url_for('read_ingredient_search'))
        except Exception as ex:
            return Response(
                    response = json.dumps(
                            {"message": "Unable to Delete"
                            }),
                        status = 400,
                        mimetype='application/json'
                )
    return render_template("home.html")

#############********************************************************************Recipes 🧾
from Models_Plan import Recipe
##########################################Create Routes 🦾
#Create Recipee => ✅ [FE finish] MV2
@app.route("/recipe", methods = ["GET", "POST"])
@login_required
def create_recipe():
    form = Recipe(request.form)
    all_ingredients_shell = db.ingredients.find({})
    all_ingredients = list(all_ingredients_shell)
    selected_ingredients = []
    instructions = []
    # Connect to User NoSQL
    user_db = create_user_NoSQLdatabases()
    user_dbcollection = user_db['recipes']
    if request.method == 'GET':
        try:
            types = [target['type'] for target in all_ingredients]
            types2 = []
            for item in types:
                if (item != ""):
                    types2.append(item)
            types2 = list(set(types2))
            return render_template('create_recipe.html', form=form, ingredients=all_ingredients, types = types2)
        except Exception as ex:
            return Response(
                    response = json.dumps(
                            {"message": "Unable to show the form for some reason"
                            }),
                        status = 400,
                        mimetype='application/json'
                )
    if request.method =="POST" and form.validate():
        recipe_ingredients = []
        recipe_prep = []
        recipe_execution = []
        desired_user = session['user']
        author = desired_user["OKTAid"]
        try:
            #Create Recipe Shell
            dbAction = db.recipes.insert_one(form.export())
            db_user_Action = user_dbcollection.insert_one(form.export())
            form_dict = request.form.to_dict() #Parse The Form, convert request.form to dictionary then to list of Tuples
            ingredient_array = []
            rest_of_paylod = []
            final_recipe_ingredients =[]
            ###Handle Ingredients
            #Get raw ingredient, quantity and unit information from the request
            for key in form_dict.keys():
                true_value = form_dict[key]
                print(true_value)
                for ingredient in all_ingredients:
                    if true_value == ingredient["title"]:
                        ingredient_array.append(ingredient)
                    if key.find(ingredient["title"]) >=1 and true_value != "" :
                        rest_of_paylod.append(key + "-" + true_value)
            titles = [stuff['title'] for stuff in ingredient_array]
            #Format raw ingredient information store ingredient, quantity and unit in seperate arrays
            quantity_array = []
            unit_array=[]
            holder_ingredients_array=[]
            for stuff in rest_of_paylod:
                parser = stuff[stuff.find("_")+1: stuff.find("-")]
                if parser in titles:
                    title = stuff[stuff.find("_")+1:stuff.find("-")]
                    if db.ingredients.find_one({"title":title}) not in holder_ingredients_array:
                     holder_ingredients_array.append(db.ingredients.find_one({"title":title}))
                    quantity = stuff[stuff.find("quantity_")+len(title)+10: len(stuff)]
                    if quantity.isdigit():
                        quantity = int(quantity)
                        quantity_array.append(quantity)
                    unit = stuff[stuff.find("unit_")+len(title)+6: len(stuff)]
                    if unit[-1].isdigit() == False:
                        unit = str(unit)
                        unit_array.append(unit)
            #Consolidate these arrays to full recipe ingredient objects and append to recipe_ingredients final array
            for x in range(0,len(holder_ingredients_array)):
                final_recipe_ingredients.append({"ingredient": holder_ingredients_array[x], "quantity":quantity_array[x], "unit": unit_array[x]})
            
            #Handle Instructions using prep and execution handles then create instructions object
            for key,value in form_dict.items():
                if value !='':
                    if key.find("prep")>=0:
                        recipe_prep.append({key:value})
                    elif key.find("execution")>=0:
                        recipe_execution.append({key:value})
            instructions = {'prep': recipe_prep, 'execution': recipe_execution}
            #Handle Creation to Master
            dbAction_ingredients = db.recipes.update_one(
            {"_id": dbAction.inserted_id},
            {"$set": {
                "ingredients": final_recipe_ingredients,
                "instructions": instructions,
                "img_URI": uploadfile(str(dbAction.inserted_id), "Recipe"),
                "crossreference_recipe_URI": db_user_Action.inserted_id,
                "author": author
                }}
            )
            #Hanlde Custom User Upload from session
            dbAction_user_ingredients = user_dbcollection.update_one(
            {"_id": db_user_Action.inserted_id},
            {"$set": {
                "ingredients": final_recipe_ingredients,
                "instructions": instructions,
                "img_URI": uploadfile(str(db_user_Action.inserted_id), "Recipe"),
                "crossreference_recipe_URI":dbAction.inserted_id,
                "author": author
                }}
            )
            flash("Recipe Created!", 'success')
            redirector = "/recipe/"f"{db_user_Action.inserted_id}"
            return Response(
                response = json.dumps(
                        {"message": "Recipee created", 
                        "id": "hi"
                        }),
                    status = 200,
                    mimetype='application/json'
            )  and redirect(redirector)
        except Exception as ex:
            return Response(
                response = json.dumps(
                        {"message": "Couldn't create recipee",
                        }),
                    status = 401,
                    mimetype='application/json'
            )
    
######################################Read/Search Routes 📚
#Standard Read by ID route for User✅[FE finish]
@app.route('/recipe/<id>', methods = ['GET'])
def read_recipe(id):
    user_db = create_user_NoSQLdatabases()
    user_dbcollection = user_db['recipes']
    if request.method == 'GET':
        ingredients = []
        try:
            dbConfirm = user_dbcollection.find_one({"_id": ObjectId(id)})
            types = [target['ingredient']['type'] for target in dbConfirm['ingredients']]
            types2 = []
            for item in types:
                if (item != ""):
                    types2.append(item)
            types2 = list(set(types2))
            prep = []
            execution = []
            for item in dbConfirm['instructions']['prep']:
                value_holder = str(item.values())
                final_value = value_holder[value_holder.find("[")+2:value_holder.find("]")-1]
                prep.append(final_value)
            for item in dbConfirm['instructions']['execution']:
                value_holder = str(item.values())
                final_value = value_holder[value_holder.find("[")+2:value_holder.find("]")-1]
                execution.append(final_value)
            
            return Response(
                        response = json.dumps(
                                {"message": "Recipee found", 
                                "id": f"{dbConfirm['_id']}",
                                "name": f"{dbConfirm['title']}",
                                }),
                            status = 200,
                            mimetype='application/json'
                    ) and render_template('read_recipe.html', recipe = dbConfirm, ingredient_type= types2, prep=prep, execution=execution)
        except Exception as ex:
            return Response(
                        response = json.dumps(
                                {"message": "Unable to retrieve Recipe"}),
                            status = 401,
                            mimetype='application/json'
                    )

#Standard Show Recipe route for global
@app.route('/recipe/global/<id>', methods = ['GET'])
def read_recipe_global(id):
    if request.method == 'GET':
        ingredients = []
        try:
            dbConfirm = db.recipes.find_one({"_id": ObjectId(id)})
            types = [target['ingredient']['type'] for target in dbConfirm['ingredients']]
            types2 = []
            for item in types:
                if (item != ""):
                    types2.append(item)
            types2 = list(set(types2))
            prep = []
            execution = []
            for item in dbConfirm['instructions']['prep']:
                value_holder = str(item.values())
                final_value = value_holder[value_holder.find("[")+2:value_holder.find("]")-1]
                prep.append(final_value)
            for item in dbConfirm['instructions']['execution']:
                value_holder = str(item.values())
                final_value = value_holder[value_holder.find("[")+2:value_holder.find("]")-1]
                execution.append(final_value)
            
            return Response(
                        response = json.dumps(
                                {"message": "Recipee found", 
                                "id": f"{dbConfirm['_id']}",
                                "name": f"{dbConfirm['title']}",
                                }),
                            status = 200,
                            mimetype='application/json'
                    ) and render_template('read_recipe.html', recipe = dbConfirm, ingredient_type= types2, prep=prep, execution=execution)
        except Exception as ex:
            return Response(
                        response = json.dumps(
                                {"message": "Unable to retrieve Recipe"}),
                            status = 401,
                            mimetype='application/json'
                    )

#Standard show all recipes ✅[FE finish]
@app.route('/recipe/all', methods = ['GET'])
def read_recipes_all():
    if request.method == 'GET':
        try:
            all_recipes = list(db.recipes.find({}))
            return Response(
                    response = json.dumps(
                            {"message": "here are all the recipes"
                            }),
                        status = 200,
                        mimetype='application/json'
                ) and render_template('read_recipes_all.html', recipes = all_recipes)
        except  Exception as ex:
            return('Unable to return all ingredients')

#Show All Your Recipees ✅[FE finish]
@app.route('/recipe/mine', methods = ['GET'])
@login_required
def read_recipes_mine():
    if request.method == 'GET':
        try:
            user_db = create_user_NoSQLdatabases()
            user_dbcollection = user_db['recipes']
            all_my_recipes = list(user_dbcollection.find({}))
            return Response(
                    response = json.dumps(
                            {"message": "here are all the recipes"
                            }),
                        status = 200,
                        mimetype='application/json'
                ) and render_template('read_recipes_mine.html', recipes = all_my_recipes)
        except Exception as ex:
            return('Unable to return all your recipes')


#Search Against your specifed Recipe Database

##Search against MongoDB✅ [FE finish]
@app.route('/recipe/search_complex',  methods = ['GET', 'POST'])
def read_recipe_search():
    form = request.form
    #Do Get Landing Request that sends back the table of all posible recipes?
    if request.method == 'GET':
        return render_template('read_recipe_search.html')
    if request.method == 'POST':
        tree_filter = form['diselecta']
        tree_filter2 = tree_filter[tree_filter.find("by")+3: len(tree_filter)]
        search = form['dasearch']
        if tree_filter2 == '_id':
            search = ObjectId(search)
        try:   
            dbConfirm = db.recipes.find({tree_filter2: search})
            dbData = list(dbConfirm)
            if len(dbData) == 0:
                stringer = tree_filter2+".title"
                new_cur = db.recipes.find({stringer: search})
                new_list = list(new_cur)
                for doc in new_list:
                    doc['_id'] = str(doc['_id'])
                return Response(
                    response = json.dumps(
                            {"message": "recipe found", 
                            "id": f"{new_list[0]['_id']}",
                            "name": f"{new_list[0]['title']}",
                            }),
                        status = 200,
                        mimetype='application/json'
                ) and render_template('read_recipe_search.html', recipes = new_list, type_search = tree_filter2)        
            elif len(dbData) == 1:
                for doc in dbData:
                    doc['_id'] = str(doc['_id'])
                return Response(
                    response = json.dumps(
                            {"message": "recipe found", 
                            "id": f"{dbData[0]['_id']}",
                            "name": f"{dbData[0]['title']}",
                            }),
                        status = 200,
                        mimetype='application/json'
                ) and render_template('read_recipe_search.html', recipes = dbData, type_search = tree_filter2)
            elif len(dbData) > 1 :
                for doc in dbData:
                    doc['_id'] = str(doc['_id'])
                return Response(
                    response = json.dumps({"message": "query made successfuly, returning array of recipes"f"{dbData}"}),
                        status = 200,
                        mimetype='application/json'
                ) and render_template('read_recipe_search.html', recipes = dbData, type_search = tree_filter2)
        except Exception as ex:
            return Response(
                    response = json.dumps(
                        {"message": "no Recipes Found"}),
                        status = 401,
                        mimetype='application/json'
                )

@app.route('/recipe/search_simple',  methods = ['GET', 'POST'])
def read_recipe_search2():
    form = request.form
    if request.method == 'GET':
        try:
            all_recipes = list(db.recipes.find({}))
            return Response(
                    response = json.dumps(
                            {"message": "here are all the ingredients"
                            }),
                        status = 200,
                        mimetype='application/json'
                ) and render_template('read_recipe_search2.html', recipes = all_recipes)
        except  Exception as ex:
            return('Unable to return all recipes')
    if request.method == 'POST':
        try:
            print(form.keys())
            hold = form.to_dict()
            searcher = hold['recipes']
            dbAction = db.recipes.find_one({"title": searcher})
            recipe_id = dbAction["_id"]
            return redirect("/recipe/"f"{recipe_id}")
            # return list(dbAction)
        except Exception as ex:
            return ("that shit didn't work")

#*****Note forcing U&D routes access via the front end (unless you want to remember ids)

##########################################Update Routes 🚅
@app.route('/recipe/update/<id>', methods = ['GET', 'POST'])
@login_required
def update_recipe(id):
    form = Recipe(request.form)
    #Pulling Data from DB so we can show it
    user_db = create_user_NoSQLdatabases()
    user_dbcollection = user_db['recipes']
    dbAction_findrecord = user_dbcollection.find_one({"_id": ObjectId(id)})
    if request.method == 'GET':
        #Data already in the object
        form.title.data = dbAction_findrecord['title']
        form.description.data = dbAction_findrecord['description']
        form.cuisine.data = dbAction_findrecord['cuisine']
        form.img_URI = dbAction_findrecord['img_URI']
        #Display Current Ingredients
        ingredients = list(db.ingredients.find({}))
        current_ingredients = dbAction_findrecord['ingredients']
        types = [target['type'] for target in ingredients]
        types2 = []
        for item in types:
            if (item != ""):
                types2.append(item)
        types2 = list(set(types2))
        titles = [item['ingredient']['title'] for item in current_ingredients ]
        #Display Current Instructions
        prep_array = [item for item in dbAction_findrecord['instructions']['prep']]
        # print(prep_array)
        execution_array = [item for item in dbAction_findrecord['instructions']['execution']]
        num_prep = len(prep_array)
        num_exec = len(execution_array)
        return render_template('/update_recipe.html', form=form, ingredients = ingredients, types = types2, 
                    titles = titles, prep = prep_array, execution = execution_array, 
                        current_ingredients=current_ingredients, num_prep=num_prep, num_exec=num_exec)
    if request.method == 'POST':
        newURI = uploadfile(id, 'Recipe')
        if newURI == "":
            newURI = form.img_URI
        form_dict = request.form.to_dict() #Parse The Form, convert request.form to dictionary then to list of Tuples
        all_ingredients = db.ingredients.find({})
        all_ingredients = list(all_ingredients)
        ingredient_array = []
        rest_of_paylod = []
        formmatted_data =[]
        quantity_array = []
        unit_array=[]
        try:
            #create variable placeholders to take any changes you make to the request.form object
            title = request.form['title']
            description = request.form['description']
            state = request.form['cuisine']
            form_dict = request.form.to_dict() #Parse The Form, convert request.form to dictionary then to list of Tuples
            all_ingredients = db.ingredients.find({})
            all_ingredients = list(all_ingredients)
            ingredient_array = []
            rest_of_paylod = []
            final_recipe_ingredients = []
            #Get raw ingredient, quantity and unit information from the request
            for key in form_dict.keys():
                true_value = form_dict[key]
                for ingredient in all_ingredients:
                    if true_value == ingredient["title"]:
                        ingredient_array.append(ingredient)
                    if key.find(ingredient["title"]) >=1 and true_value != "" :
                        rest_of_paylod.append(key + "-" + true_value)
            titles = [stuff['title'] for stuff in ingredient_array]
            #Format raw ingredient information store ingredient, quantity and unit in seperate arrays
            holder_ingredients_array=[]
            for stuff in rest_of_paylod:
                parser = stuff[stuff.find("_")+1: stuff.find("-")]
                if parser in titles:
                    if db.ingredients.find_one({"title":parser}) not in holder_ingredients_array:
                        holder_ingredients_array.append(db.ingredients.find_one({"title":parser}))
                    quantity = stuff[stuff.find("quantity_")+len(parser)+10: len(stuff)]
                    if quantity.isdigit():
                        quantity2 = int(quantity)
                        quantity_array.append(quantity2)
                    unit = stuff[stuff.find("unit_")+len(parser)+6: len(stuff)]
                    if unit[-1].isdigit() == False:
                        unit = str(unit)
                        unit_array.append(unit)
            #Consolidate these arrays to full recipe ingredient objects and append to recipe_ingredients final array
            for x in range(0,len(holder_ingredients_array)):
                final_recipe_ingredients.append({"ingredient": holder_ingredients_array[x], "quantity":quantity_array[x], "unit": unit_array[x]})
            #Handle Instructions
            recipe_prep = []
            recipe_execution = []
            for key,value in form_dict.items():
                if value !='':
                    if key.find("prep")>=0:
                        recipe_prep.append({key:value})
                    elif key.find("execution")>=0:
                        recipe_execution.append({key:value})
            instructions = {'prep': recipe_prep, 'execution': recipe_execution}
            dbAction = user_dbcollection.update_one(
                {"_id": ObjectId(id)},
                {"$set": 
                    {
                    "title": title,
                    "description": description,
                    "cuisine": state,
                    "img_URI": newURI,
                    "ingredients": final_recipe_ingredients,
                    "instructions": instructions
                    }
                }
            )
            flash('Recipe Updated', 'success')
            return Response(
                response = json.dumps({"message": "query made successfuly, updated recipe"}),
                status = 200,
                mimetype='application/json'
            ) and redirect('/recipe/'f"{id}")
        except Exception as ex:
            return ("Couldn't Update Document")
    
############################################Delete Route 🚮
#User Delete
@app.route('/recipe/delete/<id>', methods = ['GET', 'POST'])
@login_required
def delete_recipe(id):
    if request.method == 'GET':
        user_db = create_user_NoSQLdatabases()
        user_dbcollection = user_db['recipes']
        print("Ammount of recipees BEFORE deletion:" f"{user_dbcollection.count_documents({})}")
        try:
            dbAction = user_dbcollection.delete_one({"_id": ObjectId(id)})
            print("Ammount of recipes AFTER deletion:" f"{user_dbcollection.count_documents({})}")
            #Delete Picture file as well
            #Get file path from the folder
            if os.getcwd().find("static") < 0:
                os.chdir(os.getcwd()+ '/static')
            flash('Recipe Deleted', 'success')
            for file in os.listdir(os.getcwd()):
                img_search = file[file.find("_"): file.find("-")]
                if (img_search == id):
                    os.remove(file)
            flash('Recipe and image Deleted', 'success')
            return Response(
                response = json.dumps(
                            {"message": "ingredient Delete", 
                            "id": f"{id}"
                            }),
                        status = 200,
                        mimetype='application/json'
            ) and redirect('/recipe/mine')
        except Exception as ex:
            return("Delete Operation didn't Work")
    return render_template("home.html")

#Admin Delete controlled by DB Admin


#############********************************************************************Grocceries 🛒
from Models_Plan import Grocerries
##########################################Create Routes 🦾
#👽Create Grocerries 
@app.route("/groceries", methods = ["GET", "POST"])
def create_grocerries():
    dbAction = db.recipes.find({})
    dbAction2 = db.ingredients.find({})
    form = Grocerries(request.form)
    #Connect to User NoSQL
    user_db = create_user_NoSQLdatabases()
    user_dbcollection = user_db['groceries']
    if request.method =="GET":
        try:
            recipes = list(dbAction)
            ingrdients = list(dbAction2)
            types = [target['type'] for target in ingrdients]
            types2 = []
            for item in types:
                if (item != ""):
                    types2.append(item)
            types2 = list(set(types2))
        except Exception as ex:
            return("That shit didn't work")
    if request.method == "POST":
        types = []
        nonrecipe_ingredient_titles = []
        nonrecipe_ingredients = []
        quantity_array = []
        unit_array = []
        recipes_ingredients2D = []
        recipes_ingredients = []
        recipe_titles = []
        form_dict = request.form.to_dict()
        try:
            for key in form_dict.keys():
                if key.find("title")>=0:
                    title = form_dict[key]
                if key.find("notes")>=0:
                    notes = form_dict[key]
                if key.find("recipe")>=0:
                    searcher = ObjectId(form_dict[key])
                    dbAction = db.recipes.find_one({"_id": searcher})
                    recipes_ingredients2D.append(dbAction['ingredients']) 
                    recipe_titles.append(dbAction['title'])
                if key.find('ingredient')>=0:
                    nonrecipe_ingredient_titles.append(form_dict[key])
                elif key.find("quantity")>=0 and form_dict[key] !='':
                    quantity_array.append(form_dict[key])
                elif key.find("unit")>=0 and form_dict[key] !='':
                    unit_array.append(form_dict[key])
            for x in range(0, len(recipes_ingredients2D)):
                for target in recipes_ingredients2D[x]:
                    if target['ingredient']['title'] not in nonrecipe_ingredient_titles:
                        recipes_ingredients.append(target)
            #Put Ingredients Data from Ingredients form
            for x in range(0, len(nonrecipe_ingredient_titles)):
                ingredient = db.ingredients.find_one({"title": nonrecipe_ingredient_titles[x]})
                quantity = quantity_array[x]
                unit = unit_array[x]
                ingredient_holder = {"ingredient": ingredient, "quantity": quantity, "unit": unit }
                nonrecipe_ingredients.append(ingredient_holder)
            groceries_list = {
                "title": title, 
                "notes": notes,
                "ingredients": recipes_ingredients + nonrecipe_ingredients,
                "recipes": recipe_titles,
                "date_created": str(date.today()).replace("-","")
            }
            dbAction = db.groceries.insert_one(groceries_list) #💨Write to Master DB
            user_dbAction = user_dbcollection.insert_one(groceries_list) #💦Write to User DB
            ugh_this_again = recipes_ingredients + nonrecipe_ingredients
            types = [target['ingredient']['type'] for target in ugh_this_again]
            types2 = []
            for item in types:
                if (item != ""):
                    types2.append(item)
            types2 = list(set(types2))
            return (render_template("create_groceries_price.html", grocery_list_NoSQL = user_dbAction, recipes_ingredients = recipes_ingredients, adhoc = nonrecipe_ingredients, types = types2, id=user_dbAction.inserted_id))
        except Exception as ex:
            return Response(
                    response = json.dumps(
                            {"message": "Unable to Create Groccery List"
                            }),
                        status = 400,
                        mimetype='application/json'
                )
    return render_template('create_groceries.html', recipes = recipes, ingredients = ingrdients, form=form, types = types2)

###########################################Read Routes 👀
#Singe Read ✅ [FE finish]
@app.route('/groceries/<id>', methods = ["GET", "POST"])
def read_groceries(id):
    types = []
    #ButFirstConnect to User NoSQL
    user_db = create_user_NoSQLdatabases()
    user_dbcollection = user_db['groceries']
    if request.method == "GET":
        try:
            dbAction = user_dbcollection.find_one({"_id": ObjectId(id)})
            recipe_date = str(dbAction['date_created'])
            list_date = recipe_date.replace("-","")
            desired_user = session['user']
            table_name = f"{desired_user['OKTAid']}_date{list_date}_{id}"
            mycursor = mysqldb.cursor()
            mycursor.execute(f"SELECT * FROM {table_name}")
            myresult = mycursor.fetchall()
            mycursor.close()
            ingredients = []
            types2 = []
            for item in types:
                if (item != ""):
                    types2.append(item)
            types2 = list(set(types2))
            for row in myresult:
                price = str(row[4])
                price = price[price.find("(")+1: price.find(")")]
                dbAction_ingr = db.ingredients.find_one({"_id": ObjectId(row[0])})
                ingredient = {
                    "ingredient": dbAction_ingr,
                    "quantity": row[2],
                    "unit": row[3],
                    "price": price,
                    "total":float(price)*row[2]
                }
                ingredients.append(ingredient)
            types = [target['ingredient']['type'] for target in ingredients]
            for item in types:
                if (item != ""):
                    types2.append(item)
            types2 = list(set(types2))
        except Exception as ex:
           return("That shit dind't work, can't see all ingredeints")
    if request.method == "POST":
        form_dict = request.form.to_dict()
        #Now pull out price and format the data
        types = []
        quantity_array = []
        unit_array = []
        ingredients_array = []
        price_array = []
        recipe_titles = []
        for key in form_dict.keys():
            if key.find('ingredient')>=0:
                ingredient_id = key[key.find("_")+1: len(key)]
                dbAction_findIngredeint = db.ingredients.find_one({"_id":ObjectId(ingredient_id) })
                ingredients_array.append(dbAction_findIngredeint)
            elif key.find("quantity")>=0 and form_dict[key] !='':
                quantity_array.append(form_dict[key])
            elif key.find("unit")>=0 and form_dict[key] !='':
                unit_array.append(form_dict[key])
            elif key.find("price")>=0 and form_dict[key] !='':
                price_array.append(form_dict[key])
            elif key.find("price")>=0 and form_dict[key] =='':
                price_array.append(0)
        #SQL DB Write!
        dbgro_find = user_dbcollection.find_one({"_id": ObjectId(id)})
        list_date = dbgro_find["date_created"]
        desired_user = session['user']
        SQL_Grocerrylist = f"{desired_user['OKTAid']}_date{list_date}_{id}"
        mycursor = mysqldb.cursor()
        mycursor.execute(f"CREATE TABLE {SQL_Grocerrylist} (Ingredient_id VARCHAR(255) PRIMARY KEY, Ingredient_title VARCHAR(255), quantity INT, unit VARCHAR(255), price decimal (5,2))")
        sql = f"INSERT INTO {SQL_Grocerrylist} (Ingredient_id, Ingredient_title, quantity, unit, price) VALUES (%s, %s, %s, %s, %s)"
        for x in range(0,len(ingredients_array)):
            val = (str(ingredients_array[x]['_id']), ingredients_array[x]['title'], quantity_array[x], unit_array[x], price_array[x])
            mycursor.execute(sql, val)
        mysqldb.commit()
        mycursor.close()
        return redirect(f"/groceries/{str(id)}")
    return render_template("read_grocery.html", ingredients = ingredients, types = types2)
    
#Read All ✅ [FE finish]
#Should Deprecate
@app.route("/groceries/all", methods = ["GET"])
def all_groceries():
    if request.method == "GET":
        try:
            #Do some SQL stuff
            #Find all tables with given username 
            dbAction = db.groceries.find({})
            groceries = list(dbAction)
        except Exception as ex:
            return Response(
                    response = json.dumps(
                            {"message": "Unable to Retrieve All Lists"
                            }),
                        status = 400,
                        mimetype='application/json'
                )
    return render_template("read_all_groceries.html", groceries = groceries)
    
###########################################Update Routes 🚅
#Standard update Route ✅ [FE finish]
@app.route("/groceries/update/<id>",  methods = ["GET", "POST"])
@login_required
def update_groceries(id):
    form = Grocerries(request.form)
    #Set up NoSQL to save updates
    user_db = create_user_NoSQLdatabases()
    user_dbcollection = user_db['groceries']
    if request.method == 'GET':
        #NoSQL Data Calling
        dbAction = db.recipes.find({})
        all_ingre = db.ingredients.find({})
        dbGrocery_search = user_dbcollection.find_one({"_id": ObjectId(id)})
        form.title.data = dbGrocery_search['title']
        form.date_created = str(dbGrocery_search['date_created'])
        #SQL Data Calling
        list_date = form.date_created.replace("-","")
        desired_user = session['user']
        table_name = f"{desired_user['OKTAid']}_date{list_date}_{id}"
        mycursor = mysqldb.cursor()
        mycursor.execute(f"SELECT * FROM {table_name}")
        myresult = mycursor.fetchall()
        mycursor.close()
        ingredients = []
        types2 = []
        for row in myresult:
            price = str(row[4])
            price = price[price.find("(")+1: price.find(")")]
            dbAction_ingr = db.ingredients.find_one({"_id": ObjectId(row[0])})
            ingredient = {
                "ingredient": dbAction_ingr,
                "quantity": row[2],
                "unit": row[3],
                "price": price,
                "total":float(price)*row[2]
            }
            ingredients.append(ingredient)
        types = [target['ingredient']['type'] for target in ingredients]
        
        types2 = list(set(types))
        checker = [target['ingredient']['title'] for target in ingredients]
        remainder =[]
        all_ingredients=list(all_ingre)
        for ingredient in all_ingredients:
            if ingredient['title'] not in checker:
                remainder.append(ingredient)
        return render_template("update_groceries.html", form = form, types = types2, remaining_ingredients = remainder, recipes = dbAction, current_ingredients=ingredients )
    if request.method == 'POST':
        form_dict = request.form.to_dict()
        types = []
        quantity_array = []
        unit_array = []
        ingredients_array = []
        price_array = []
        rawform_ingredient_id_checker = []
        rawform_ingredient_titles = []
        try:
            for key in form_dict.keys():
                if key.find('ingredient')>=0:
                    ingredient_id = key[key.find("_")+1: len(key)]
                    dbAction_findIngredeint = db.ingredients.find_one({"_id":ObjectId(ingredient_id) })
                    rawform_ingredient_title = dbAction_findIngredeint['title']
                    ingredients_array.append(dbAction_findIngredeint)
                    rawform_ingredient_titles.append(rawform_ingredient_title)
                elif key.find("quantity")>=0 and form_dict[key] !='':
                    quantity_array.append(form_dict[key])
                elif key.find("unit")>=0 and form_dict[key] !='':
                    unit_array.append(form_dict[key])
                elif key.find("price")>=0 and form_dict[key] !='':
                    price_array.append(form_dict[key])     
            final_ingredients = []
            # #SQL DB Write!
            dbGrocery_search = user_dbcollection.find_one({"_id": ObjectId(id)})
            list_date = dbGrocery_search["date_created"]
            desired_user = session['user']
            SQL_Grocerrylist = f"{desired_user['OKTAid']}_date{list_date}_{id}"
            mycursor = mysqldb.cursor()
            mycursor.execute(f"select * from {SQL_Grocerrylist}")
            current_table = mycursor.fetchall()
            mycursor.close()
            for x in range(0,len(ingredients_array)):
                if int(quantity_array[x]) > 0:
                    rawform_ingredient_id_checker.append(str(ingredients_array[x]["_id"]))
                    ingredient = {
                        "ingredient": ingredients_array[x],
                        "unit": unit_array[x],
                        "quantity": quantity_array[x],
                        "price": price_array[x]
                    }
                    final_ingredients.append(ingredient)
            current_ingredient_titles = []
            rest_ingredients = []
            # Check for Ingredients already in the SQL table
            mycursor2 = mysqldb.cursor()
            for item in current_table:
                current_ingredient_title = str(item[1])
                current_ingredient_id = str(item[0])
                current_ingredient_titles.append(current_ingredient_title)
                for stuff in final_ingredients:
                    if current_ingredient_id in rawform_ingredient_id_checker:
                        sql_query = "UPDATE {} SET Ingredient_title = %s, quantity = %s, unit = %s, price = %s WHERE Ingredient_id = %s".format(SQL_Grocerrylist)
                        val = (stuff['ingredient']['title'], stuff['quantity'],stuff['unit'],stuff['price'],str(stuff['ingredient']['_id']))
                        mycursor2.execute(sql_query, val)
            mycursor2.close()
            #check if new ingredients is in current ingredients id if not insert
            cursor_insert_remaining_ingredients = mysqldb.cursor()
            for title in rawform_ingredient_titles:
                if title not in current_ingredient_titles:
                    for stuff in final_ingredients:
                        if stuff['ingredient']['title'] == title:
                            rest_ingredients.append(stuff)
            sql_insert_remaining_ingredients = f"INSERT INTO {SQL_Grocerrylist} (Ingredient_id, Ingredient_title, quantity, unit, price) VALUES (%s, %s, %s, %s, %s)"    
            #SQL Insert New Ingredients
            for x in range(0,len(rest_ingredients)):
                val = (str(rest_ingredients[x]['ingredient']['_id']), rest_ingredients[x]['ingredient']['title'], rest_ingredients[x]['quantity'], rest_ingredients[x]['unit'], rest_ingredients[x]['price'])
                cursor_insert_remaining_ingredients.execute(sql_insert_remaining_ingredients, val)
            mysqldb.commit()
            cursor_insert_remaining_ingredients.close()
            #NoSQL Set the data modified and title values
            for key in form_dict.keys():
                if key =='title':
                    updated_title = form_dict[key]
            todaysdate = str(date.today())
            dbAction = user_dbcollection.update_one({"_id": ObjectId(id)},{"$set": { "title": updated_title, "recently_modified": todaysdate}})
            return(redirect(f"/groceries/{id}")) 
        except Exception as ex:
            return Response(
                    response = json.dumps(
                            {"message": "Unable to Update Groccery List"
                            }),
                        status = 400,
                        mimetype='application/json'
                )
    

###########################################Delete Routes 🚮
@app.route("/groceries/delete/<id>", methods =  ['POST', 'GET'])
@login_required
def delete_groceries(id): 
    user_db = create_user_NoSQLdatabases()
    user_dbcollection = user_db['groceries']
    if request.method == "GET":
        try:
            print("Ammount of recipes BEFPRE deletion:" f"{user_dbcollection.count_documents({})}")
            dbAction = user_dbcollection.delete_one({"_id": ObjectId(id)})
            print("Ammount of recipes AFTER deletion:" f"{user_dbcollection.count_documents({})}")
            flash("Deleted grocery list: " f"{id}", "success")
            return Response(
                    response = json.dumps(
                            {"message": "just did deleted the Groccery list"
                            }),
                        status = 200,
                        mimetype='application/json'
                ) and redirect('/groceries/all')
        except Exception as ex:
            return Response(
                    response = json.dumps(
                            {"message": "unable to delete Groccery List"
                            }),
                        status = 400,
                        mimetype='application/json'
                )
    
    return redirect("/")

@app.route("/test", methods = ["GET"])
def test():
    return render_template("test.html")
#Testing Area
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
if __name__ == "__main__":
    app.run(port = 5000, debug=True)