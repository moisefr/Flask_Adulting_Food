from wtforms import Form, StringField, TextAreaField, PasswordField, validators, FileField
from datetime import date

class User(Form):
    username = StringField('Name', [validators.Length(min=1, max=50)])
    email = StringField('lastName', [validators.Length(min=4, max=25)])
    #password = PasswordField('password', [v])

    def export(self):
        return (
            {"name": self.name, 
            "lastName": self.lastName
            }
        )

class Ingredient(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    description = TextAreaField('description', [validators.Length(min=4, max=500)])
    img_URI = ''
    state = StringField('State of Matter')
    type =  StringField('Food Group')
    price = 0
    def export(self):
        return (
            {"title": self.name.data, 
            "description": self.description.data,
            "state": self.state.data,
            "type": self.type.data,
            "img_URI": "<Empty URI>"
            }
        )
class Recipe(Form):
    title = StringField('Title', [validators.Length(min=1, max=50)])
    description = TextAreaField('description', [validators.Length(min=4, max=2500)])
    img_URI =''
    cuisine = StringField('Recipee Type')
    instructions =  []
    ingredients = []
    date_created = str(date.today())
    def export(self):
        return (
            {
                "title": self.title.data, 
                "description": self.description.data,
                "img_URI": self.img_URI,
                "cuisine": self.cuisine.data,
                "ingredients": self.ingredients,
                "instructions": self.instructions,
                "date_created": self.date_created
            }
        )

class Grocerries(Form):
    title = StringField('Title', [validators.Length(min=1, max=50)])
    ingredients = {}
    date_created = ''
    def export(self):
        return (
            {"title": self.title.data, 
            "ingredients": self.ingredients,
            "date": self.date_created
            }
        )