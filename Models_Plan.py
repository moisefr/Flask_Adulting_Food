from wtforms import Form, StringField, TextAreaField, PasswordField, validators, FileField
from datetime import date
from flask_login import UserMixin

class User(UserMixin):
    
    """Custom User class."""

    def __init__(self, id_, name, email, preferred_username, given_name, family_name):
        self.id = id_
        self.name = name
        self.email = email
        self.displayname = preferred_username
        self.firstName = given_name
        self.lastName = family_name


    def claims(self):
        """Use this method to render all assigned claims on profile page."""
        return {
                'name': self.name,
                'email': self.email}.items()

    # @staticmethod
    # def get(user_id):
    #     return USERS_DB.get(user_id)
    # @staticmethod
    def export(self):
        return (
            {
            'name': self.name,
            'OKTAid': self.id,
            'email': self.email,
            'displayname': self.displayname,
            'firstName': self.firstName,
            'lastName': self.lastName,
            'profile': {},
            'favorite_food': ''
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
    instructions =  {'prep': [], 'execution': []}
    ingredients = []
    date_created = str(date.today())
    author = ''
    def export(self):
        return (
            {
                "title": self.title.data, 
                "description": self.description.data,
                "img_URI": self.img_URI,
                "cuisine": self.cuisine.data,
                "ingredients": self.ingredients,
                "instructions": self.instructions,
                "date_created": self.date_created,
                "author": self.author
            }
        )
class Grocerries(Form):
    title = StringField('Title', [validators.Length(min=1, max=50)])
    ingredients = []
    date_created = str(date.today())
    def export(self):
        return (
            {"title": self.title.data, 
            "ingredients": self.ingredients,
            "date": self.date_created
            }
        )