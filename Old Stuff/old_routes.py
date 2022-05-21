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


#Search Against your specifed Recipe Database
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