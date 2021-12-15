##########################################SET UP 🙏🏾#################################################
#Import Key Libraries: os, flask(response, request), pymango, json, bson.objectid objectid
import os, sys, stat
from flask import Flask, Response, request, render_template, flash, redirect, url_for
from werkzeug.utils import secure_filename
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
import pymongo
import json
from bson.objectid import ObjectId
#Instantiate app
app = Flask(__name__)

#Rules of the road
#**** forcing U&D routes access via the front end only (unless you want to remember ids)

#****************DB Connection 🌍**************
connection_string = 'mongodb+srv://default_test:yYDiCDe9AJmEXkrF@cluster0.oxeo8.mongodb.net/Adulting_Food?retryWrites=true&w=majority'
client = pymongo.MongoClient(connection_string, serverSelectionTimeoutMS=15000)
##Check if the connection was made to the DB
try:
    # This code will show the client info, use to test connectivity
    db = client.Adulting_Food
    print("Connected to Mongo Database  😁: ", "availible data collections are - ", db.list_collection_names() )
except Exception:
    print("Unable to connect to the server.")
    # print(client)

#****************Configuration for File Uploads 📂**************
upload_folder = "static/"
if not os.path.exists(upload_folder):
   os.mkdir(upload_folder)
app.config['UPLOAD_FOLDER'] = upload_folder
app.secret_key = 'whatitiscuhwhatisup'
#######################Handles File Uploads
#Ingredients
def uploadfile(id):
    if request.method == 'POST':
        f = request.files['file'] # get the file from the files object
        if os.getcwd().find("static") < 0:
            os.chdir(os.getcwd()+ '/static')
        if f.filename =="":
            for file in os.listdir(os.getcwd()):
            #👁‍🗨Edit string slicing
                img_search = file[file.find("_")+1: file.find("-")]
                handle = file[0: file.find("_")]
                if (img_search == id and handle == "Ingredient"):
                    flash('Picture was not updated', 'info')
                    return file
                else:
                     return f
        else:
            for file in os.listdir(os.getcwd()):
                #👁‍🗨Edit string slicing
                img_search = file[file.find("_")+1: file.find("-")]
                handle = file[0: file.find("_")]
                if (img_search == id and handle == "Ingredient"):
                    os.remove(file)
                    flash('Old Picture Deleted upload new picture', 'success')
        if os.getcwd().find("static") < 0:
            os.chdir(os.getcwd()+ '/static')
        # Saving the file in the required destination
        #👁‍🗨Edit string slicing
        f.save(secure_filename("Ingredient_"+ id + "-" + f.filename))
      #Get file path from the folder
        if os.getcwd().find("static") < 0:
            os.chdir(os.getcwd()+ '/static')
        for file in os.listdir(os.getcwd()):
            handle = file[0: file.find("_")]
            img_search = file[file.find("_")+1: file.find("-")]
            if (img_search == id and handle == 'Ingredient'):
                img_file = file
        return img_file

#Recipes
def upload_recipe_file(id):
    if request.method == 'GET':
        if os.getcwd().find("static") < 0:
            os.chdir(os.getcwd()+ '/static')
        for file in os.listdir(os.getcwd()):
            #👁‍🗨Edit string slicing
            img_search = file[file.find("_")+1: file.find("-")]
            handle = file[0: file.find("_")]
            if (img_search == id and handle == 'Recipe'):
                os.remove(file)
                flash('Old Picture Deleted upload new picture', 'success')
                return ''
    if request.method == 'POST':
        f = request.files['file'] # get the file from the files object
        if os.getcwd().find("static") < 0:
            os.chdir(os.getcwd()+ '/static')
        # Saving the file in the required destination
        #👁‍🗨Edit string slicing
        f.save(secure_filename("Recipe_"+ id + "-" + f.filename))
      #Get file path from the folder
        if os.getcwd().find("static") < 0:
            os.chdir(os.getcwd()+ '/static')
        
        for file in os.listdir(os.getcwd()):
            handle = file[0: file.find("_")]
            img_search = file[file.find("_")+1: file.find("-")]
            if (img_search == id and handle == 'Recipe'):
                img_file = file
        return img_file
    
##############********************************Routes 🧳****************#####################
#Home Route ✅[FE finish]
@app.route("/", methods = ["GET", "POST"])
def landing():
    return render_template("home.html")

#############********************************************************************Ingridients 🍍
from Models_Plan import Ingredient

##########################################Create Routes 🦾
#Create  an Ingredient ✅[FE finish]
@app.route("/ingredient", methods=["GET","POST"])
def create_ingredient():
    #this binds form entries to the object class, it's like saying all the 
    #let the data entered in the form or postman map to the attributes defined in the class
    ###👁‍🗨so does 2 things, sends form entries to class attributes and let's you use class methods!!!!
    form = Ingredient(request.form)
    if request.method == "POST" and form.validate():
        try:    
            dbAction = db.ingredients.insert_one(form.export())
            form.img_URI = uploadfile(str(dbAction.inserted_id))
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
            return ("unable to create new ingridient")
    return render_template('/create_ingredient.html', form=form)
 
######################################Read/Search Routes 📚
#Standard Read by ID route ✅[FE finish]
@app.route('/ingredient/<id>', methods = ['GET'])
def read_ingredient_standard(id):
    if request.method == 'GET':
        try:
            dbConfirm = db.ingredients.find_one({"_id": ObjectId(id)})
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
            return("Unable to retrieve Ingredient")
    return redirect("/")

#Search against MongoDB✅   [FE finish]
@app.route('/ingredient/search',  methods = ['GET', 'POST'])
def read_ingredient_search():
    form = request.form
    if request.method == 'GET':
        try:
            all_ingredients = db.ingredients.find({})
            return Response(
                    response = json.dumps(
                            {"message": "here are all the ingredients"
                            }),
                        status = 200,
                        mimetype='application/json'
                ) and render_template('read_ingredient_search.html', ingredients = all_ingredients)
        except  Exception as ex:
            return('Unable to return all ingredients')
    if request.method == 'POST':
        tree_filter = form['diselecta']
        tree_filter2 = tree_filter[tree_filter.find("by")+3: len(tree_filter)]
        search = form['dasearch']
        if tree_filter2 == '_id':
            search = ObjectId(search)
        try:   
            dbConfirm = db.ingredients.find({tree_filter2: search})
            dbData = list(dbConfirm)
            #To Do: 👩🏾‍💻This whole logic tree might go away with a better html element
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
                ) and render_template('read_ingredient_search_display.html', ingredients = dbData, type_search = tree_filter2)
            elif len(dbData) >1 :
                for doc in dbData:
                    doc['_id'] = str(doc['_id'])
                return Response(
                    response = json.dumps({"message": "query made successfuly, returning array of ingredients"f"{dbData}"}),
                        status = 200,
                        mimetype='application/json'
                ) and render_template('read_ingredient_search_display.html', ingredients = dbData, type_search = tree_filter2)
        except Exception as ex:
            return ("that shit didn't work")
    return render_template('read_ingredient_search.html')

##Search against USGov DB (file)
##########################################Update Routes 🚅
#Standard update Route ✅ [FE finish]
@app.route('/ingredient/update/<id>', methods = ['GET', 'POST'])
def update_ingredient(id):
    form = Ingredient(request.form)
    #Form Binding -Sets data in the form oject attributes to what's already in the database so when html template presents you see the previous data
    dbAction_findrecord = db.ingredients.find_one({"_id": ObjectId(id)})
    form.name.data = dbAction_findrecord['title']
    form.description.data = dbAction_findrecord['description']
    form.state.data = dbAction_findrecord['state']
    form.type.data = dbAction_findrecord['type']  
    old_IMG_URI = dbAction_findrecord['img_URI']

    if request.method == 'POST':
        # print(request.form.keys())
        try:
            #create variable placeholders to take any changes you make to the request.form object
            title = request.form['name']
            description = request.form['description']
            state = request.form['state']
            type_ingredient = request.form['type']
            f = request.files['file'] # get the file from the files object
            form.img_URI = uploadfile(str(id))
            dbAction = db.ingredients.update_one(
                {"_id": ObjectId(id)},
                {"$set": 
                    {
                    "title": title,
                    "description": description,
                    "state": state,
                    "type": type_ingredient,
                    "img_URI": form.img_URI
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
            return ("Couldn't Update Document")
    return render_template('/update_ingredient.html', form=form, current_state = form.state.data, current_type = dbAction_findrecord['type'])

###########################################Delete Route 🚮
@app.route('/ingredient/delete/<id>', methods = ['GET', 'POST'])
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
            return("Delete Operation didn't Work")
    return render_template("home.html")

#############********************************************************************Recipes 🧾
from Models_Plan import Recipe
##############Create Routes 🦾
#Create Recipee => ✅ [FE finish]
@app.route("/add_recipe", methods = ["GET", "POST"])
def create_recipe():
    form = Recipe(request.form)
    ingredients = list(db.ingredients.find({}))
    selected_ingredients = []
    instructions = []
    if request.method =="POST" and form.validate():
        try:
            #Create Recipe Shell
            dbAction = db.recipes.insert_one(form.export())
            form_array = list(request.form.values())
            for item in form_array:
                for ingre in ingredients:
                    if (item ==ingre['title']):
                        selected_ingredients.append(ingre)
            instructions = [request.form[stuff] for stuff in request.form.keys() if(stuff.__contains__('instruct'))]
            instructions = [instruction for instruction in instructions if(instruction != "")]
            dbAction_ingredients = db.recipes.update_one(
            {"_id": dbAction.inserted_id},
            {"$set": {
                "ingredients": selected_ingredients,
                "instructions": instructions,
                "img_URI": uploadfile(str(dbAction.inserted_id))
                }}
            )
            redirector = "/recipe/"f"{dbAction.inserted_id}"
            flash('Recipe Created', 'sucess') 
            return Response(
                response = json.dumps(
                        {"message": "Recipee created", 
                        "id": "hi"
                        }),
                    status = 200,
                    mimetype='application/json'
            )  and redirect(redirector)
        except Exception as ex:
            return("Couldn't create recipee")
    return render_template('create_recipe.html', form=form, ingredients=ingredients)

##############Read/Search Routes 📚
#Standard Read by ID route ✅[FE finish]
@app.route('/recipe/<id>', methods = ['GET'])
def read_recipe_standard(id):
    if request.method == 'GET':
        flash("Recipe Added!", 'success')
        try:
            dbConfirm = db.recipes.find_one({"_id": ObjectId(id)})
            for target in dbConfirm:
                if target == 'ingredients':
                    ingredients = dbConfirm[target]
                    # 
            types = [target['type'] for target in ingredients]
            print(types)
            types2 = []
            for item in types:
                if (item not in types2):
                    types2.append(item)
            return Response(
                        response = json.dumps(
                                {"message": "Recipee found", 
                                "id": f"{dbConfirm['_id']}",
                                "name": f"{dbConfirm['title']}",
                                }),
                            status = 200,
                            mimetype='application/json'
                    ) and render_template('read_recipe_standard.html', recipe = dbConfirm, ingredient_type= types2)
        except Exception as ex:
            return("Unable to retrieve Recipe")
    return "/"
    # return "In standard read route for recipee id: "f"{id}"

##Search against MongoDB✅ [FE finish]
@app.route('/recipe/search',  methods = ['GET', 'POST'])
def read_recipe_search():
    form = request.form
    #Do Get Landing Request that sends back the table of all posible recipes?
    if request.method == 'GET':
        dbConfirm = db.recipes.find()
        dbData = list(dbConfirm)
        return Response(
            response = json.dumps(
                    {"message": "recipe found", 
                    "id": f"{dbData[0]['_id']}",
                    "name": f"{dbData[0]['title']}",
                    }),
                status = 200,
                mimetype='application/json'
        ) and render_template('read_recipe_search.html', recipes = dbData)
    if request.method == 'POST':
        tree_filter = form['diselecta']
        tree_filter2 = tree_filter[tree_filter.find("by")+3: len(tree_filter)]
        search = form['dasearch']
        if tree_filter2 == '_id':
               search = ObjectId(search)
        print("FIlter is:", tree_filter2, " paylod is:", search)
        try:   
            dbConfirm =  db.recipes.find({tree_filter2: search})
            dbData = list(dbConfirm)
            #Search by Ingredient
            if len(dbData) == 0:
                stringer = tree_filter2+".title"
                new_cur = db.recipes.find({stringer: search})
                new_list = list(new_cur)
                for doc in new_list:
                    doc['_id'] = str(doc['_id'])
                print(new_list)
                return Response(
                    response = json.dumps(
                            {"message": "recipe found", 
                            "id": f"{new_list[0]['_id']}",
                            "name": f"{new_list[0]['title']}",
                            }),
                        status = 200,
                        mimetype='application/json'
                ) and render_template('read_recipe_search_display.html', recipes = new_list, type_search = tree_filter2)        
            elif len(dbData) == 1:
                for doc in dbData:
                    doc['_id'] = str(doc['_id'])
                print (dbData)
                return Response(
                    response = json.dumps(
                            {"message": "recipe found", 
                            "id": f"{dbData[0]['_id']}",
                            "name": f"{dbData[0]['title']}",
                            }),
                        status = 200,
                        mimetype='application/json'
                ) and render_template('read_ingredient_search_display.html', ingredients = dbData, type_search = tree_filter2)
            elif len(dbData) >1 :
                for doc in dbData:
                    doc['_id'] = str(doc['_id'])
                return Response(
                    response = json.dumps({"message": "query made successfuly, returning array of recipes"f"{dbData}"}),
                        status = 200,
                        mimetype='application/json'
                ) and render_template('read_recipe_search_display.html', recipes = dbData, type_search = tree_filter2)
        except Exception as ex:
            return ("that shit didn't work")
    return render_template('read_recipe_search.html')

#*****Note forcing U&D routes access via the front end (unless you want to remember ids)

##############Update Routes 🚅
#Standard update Route ✅ [FE finish]
@app.route('/recipe/update/<id>', methods = ['GET', 'POST'])
def update_recipe(id):
    form = Recipe(request.form)
    dbAction_findrecord = db.recipes.find_one({"_id": ObjectId(id)})
    form.title.data = dbAction_findrecord['title']
    form.description.data = dbAction_findrecord['description']
    form.cuisine.data = dbAction_findrecord['cuisine']
    form.img_URI = dbAction_findrecord['img_URI']
    form.ingredients = dbAction_findrecord['ingredients']
    form.instructions = dbAction_findrecord['instructions']
    if request.method == 'POST':
        try:
            #create variable placeholders to take any changes you make to the request.form object
            title = request.form['title']
            description = request.form['description']
            state = request.form['cuisine']
            dbAction = db.recipes.update_one(
                {"_id": ObjectId(id)},
                {"$set": 
                    {
                    "title": title,
                    "description": description,
                    "cuisine": state,
                    "img_URI": uploadfile(id)
                    }
                }
            )
            flash('Recipe Updated', 'success')
            return Response(
                response = json.dumps({"message": "query made successfuly, updated ingredient"}),
                status = 200,
                mimetype='application/json'
            ) and redirect('/recipe/update/ingredients/'f"{id}")
        except Exception as ex:
            return ("Couldn't Update Document")
    return render_template('/update_recipe.html', form=form)

#Update Recipee => Add Ingredients ✅ [FE finish]
@app.route("/recipe/update/ingredients/<id>", methods = ["PUT", "POST", "GET"])
def update_recipee_ingredients(id):
    form = Recipe(request.form)
    ingredients = list(db.ingredients.find({}))
    current_recipe = db.recipes.find_one({"_id": ObjectId(id)})
    current_ingredients = current_recipe['ingredients']
    if request.method == "POST":
        selected_ingredients = [db.ingredients.find_one({"title": target_ingredient}) for target_ingredient in list(request.form.keys())] 
        try:
            current_ingredients.extend(selected_ingredients)
            dbAction = db.recipes.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"ingredients": current_ingredients}}
            )
            print(current_recipe['ingredients'])
            flash('Ingredients Added', 'success')
            return Response(
                    response = json.dumps(
                        {"message": "Recipee ingridients added"}),
                        status = 200,
                        mimetype='application/json'
                ) and redirect("/recipe/update/instructions/"f"{id}")
        except Exception as ex:
            return ("unable to add the ingredients")   
    return Response(
                response = json.dumps(
                        {"message": "Inside the Create Recipee Add Ingredients psection", 
                        "id": f"{id}"
                        }),
                    status = 200,
                    mimetype='application/json'
            ) and render_template('update_recipee_add_ingredients.html', ingredients = ingredients, id = id, current_ingredients = current_ingredients)

#Update Recipee => Add Instructions ✅ [FE finish]
@app.route("/recipe/update/instructions/<id>", methods = ["PUT", "POST", "GET"])
def update_recipee_instructions(id):
    # form = Recipe(request.form)
    current_recipe = db.recipes.find_one({"_id": ObjectId(id)})
    current_instructions = current_recipe['instructions']
    # form.instructions.append(request.form.get("instructions"))
    if request.method == 'GET':
        print(current_instructions)
        return Response(
            response = json.dumps(
                    {"message": "Inside the Create Recipee Add Instructions section", 
                    "id": id
                    }),
                status = 200,
                mimetype='application/json'
        ) and render_template('update_recipee_add_instructions.html', current_recipe = current_recipe)

    if request.method == "POST":
        print("Request form: " f"{list(request.form.keys())}" + "id: ", id)
        new_instructions = list(request.form.values())
        current_instructions.extend(new_instructions)
        final_instructions = [item for item in current_instructions if item != '']
        try:
            dbAction = db.recipes.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"instructions": final_instructions}}
            )
            return Response(
                    response = json.dumps(
                            {"message": "Recipee Instructions added", 
                            "id": id
                            }),
                        status = 200,
                        mimetype='application/json'
                ) and redirect("/recipe/"f"{id}")
        except Exception as ex:
            return ("unable to add instructions")

#Delete Route 🚮
@app.route('/recipe/delete/<id>', methods = ['GET', 'POST'])
def delete_recipe(id):
    if request.method == 'GET':
        print("Ammount of recipees BEFORE deletion:" f"{db.ingredients.count_documents({})}")
        try:
            dbAction = db.recipes.delete_one({"_id": ObjectId(id)})
            print("Ammount of recipes AFTER deletion:" f"{db.recipes.count_documents({})}")
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
            ) and redirect(url_for('read_recipe_search'))
        except Exception as ex:
            return("Delete Operation didn't Work")
    return render_template("home.html")

#############********************************************************************Grocceries 🛒
from Models_Plan import Grocerries
#Create Routes 👀
#👽Create Grocerries 
@app.route("/groceries", methods = ["GET", "POST"])
def create_grocerries():
    dbAction = db.recipes.find({})
    dbAction2 = db.ingredients.find({})
    form = Grocerries(request.form)
    if request.method =="GET":
        try:
            recipes = list(dbAction)
            ingrdients = list(dbAction2)
        except Exception as ex:
            return("That shit didn't work")
    if request.method == "POST":
        final_ingredients = []
        types = []
        for item in request.form.keys():
            if (item.find("title")>0):
                id_for_search = item[item.find("id")+15:item.find("title")-5]
                id_for_search = ObjectId(id_for_search)
                db_pull = db.ingredients.find_one({"_id": id_for_search})
                final_ingredients.append(db_pull)
                types.append(db_pull['type'])
            elif (item.find("title")):
                print("title leaf: " + item)
                id_for_search = item[item.find("id")+15:item.find("title")-5]
                id_for_search = ObjectId(item)
                db_pull_recipe = db.recipes.find_one({"_id": id_for_search})
                db_pull_recipe = dict(db_pull_recipe)
                for ingredient in db_pull_recipe['ingredients']:
                    final_ingredients.append(ingredient)
                    types.append(ingredient['type'])
            else:
                print((form.title.data))
        dbAction_groceries = db.groceries.insert_one({"ingredients": final_ingredients, "title": form.title.data, "date": form.date_created})
        types = list(set(types))     
        # dbCheck = db.groceries.find_one({"_id": dbAction.inserted_id})
        # print(dbCheck) 
        return render_template('read_groceries.html', ingredients = final_ingredients, types = types)
    return render_template('add_groceries.html', recipes = recipes, ingredients = ingrdients, form=form)
#Read Routes 👀
#Singe Read ✅ [FE finish]
@app.route('/groceries/<id>', methods = ["GET"])
def groceries(id):
    types = []
    if request.method == "GET":
        try:
            dbAction = db.groceries.find_one({"_id": ObjectId(id)})
            print(dbAction)
        except Exception as ex:
            print("That shit dind't work, can't see all ingredeints")
    return render_template("see_grocery.html", ingredients = dbAction['ingredients'], identifier = dbAction['title'] + "-" + dbAction['date'])
#Read All ✅ [FE finish]
@app.route("/groceries/all", methods = ["GET"])
def all_groceries():
    if request.method == "GET":
        try:
            dbAction = db.groceries.find({})
            groceries = list(dbAction)
        except Exception as ex:
            print("That shit dind't work, can't see all ingredeints")
    return render_template("read_all_groceries.html", groceries = groceries)

#Update Routes 🚅
#Standard update Route ✅ [FE finish]
@app.route("/groceries/update/<id>",  methods = ["GET", "POST"])
def update_groceries(id):
    form = Grocerries(request.form)
    if request.method == 'GET':
        dbAction = db.recipes.find({})
        dbAction2 = db.ingredients.find({})
        dbGrocery_search = db.groceries.find_one({"_id": ObjectId(id)})
        form.ingredients = dbGrocery_search['ingredients']
        form.title.data = dbGrocery_search['title']
        form.date_created = dbGrocery_search['date']
        types =[ingredient['type'] for ingredient in form.ingredients]
        types = list(set(types))
        print(form.ingredients)
    if request.method == 'POST':
        final_ingredients = []
        types = []
        for item in request.form.keys():
            print(item)
            if (item.find("title")>0):
                id_for_search = item[item.find("id")+15:item.find("title")-5]
                id_for_search = ObjectId(id_for_search)
                db_pull = db.ingredients.find_one({"_id": id_for_search})
                final_ingredients.append(db_pull)
                title = request.form['title']
                # types.append(dict(db_pull['type']))
                if db_pull != None:
                   types.append(db_pull['type'])
            else:
                print((form.title.data))
        dbAction_groceries = db.groceries.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"ingredients": final_ingredients, "title": title, "date": form.date_created}}
            )
        types = list(set(types))     
        # dbCheck = db.groceries.find_one({"_id": dbAction.inserted_id})
        # print(dbCheck) 
        # return "Hello"
        return render_template('read_groceries.html', ingredients = final_ingredients, types = types)
    return render_template("update_groceries.html", form = form, types = types, ingredients = dbAction2, recipes = dbAction )

#Delete Routes 🚮
@app.route("/groceries/delete/<id>", methods =  ['POST', 'GET'])
def delete_groceries(id): 
    if request.method == "GET":
        try:
            print("Ammount of recipes BEFPRE deletion:" f"{db.groceries.count_documents({})}")
            dbAction = db.groceries.delete_one({"_id": ObjectId(id)})
            print("Ammount of recipes AFTER deletion:" f"{db.groceries.count_documents({})}")
            flash("Deleted grocery list: " f"{id}", "success")
            return Response(
                    response = json.dumps(
                            {"message": "just did a delete"
                            }),
                        status = 200,
                        mimetype='application/json'
                ) and redirect('/groceries/all')
        except Exception as ex:
            return ("unable to find key grocery for this grocerry list")
    
    return redirect("/")









if __name__ == "__main__":
    app.run(port = 5000, debug=True)