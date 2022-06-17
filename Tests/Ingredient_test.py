import unittest
import requests
 
API_URL = "http://127.0.0.1:5000/"
test_id = '61ba21a7b671b767020bbc98'
test_ingredient = {"title": 'tester', 
            "description": 'self.description.data',
            "state": 'self.state.data',
            "type": 'self.type.data',
            "img_URI": "<Empty URI>",
            "date_created": 'self.date_created',
            "date_modified": 'self.date_modified'
            }

class IngredientTests(unittest.TestCase):
    def test_create_ingredient(self):
        Ingredient_URL = f"{API_URL}/ingredient"
        #Test Page load and form presents
        r_get = requests.get(Ingredient_URL)
        self.assertEqual(r_get.status_code, 200)
        self.assertEqual(r_get.headers['Content-Type'], 'text/html; charset=utf-8')
        #Test That you can create an Ingredient
        r_post = requests.post(Ingredient_URL,data=test_ingredient)
        self.assertEqual(r_post.status_code, 200)
        self.assertEqual(r_post.headers['Content-Type'], 'text/html; charset=utf-8')
    def test_read_ingredient(self):
        Ingredient_URL = f"{API_URL}/ingredient/{test_id}"
        #Test Page load and form presents
        r_get = requests.get(Ingredient_URL)
        self.assertEqual(r_get.status_code, 200)
        self.assertEqual(r_get.headers['Content-Type'], 'text/html; charset=utf-8')
        # print(r_get.url)
        # self.assertEqual(r.content, "html/text")
    def test_read_all_ingredients(self):
        Ingredient_URL = f"{API_URL}/ingredient/all"
        #Test Page load and form presents
        r_get = requests.get(Ingredient_URL)
        self.assertEqual(r_get.status_code, 200)
        self.assertEqual(r_get.headers['Content-Type'], 'text/html; charset=utf-8')
        # print(r_get.url)
        # self.assertEqual(r.content, "html/text")
    def test_update_ingredient(self):
        Ingredient_URL = f"{API_URL}/ingredient/update/{test_id}"
        #Test Page load and form presents
        r_get = requests.get(Ingredient_URL)
        print(r_get.json())
        self.assertEqual(r_get.status_code, 200)
        self.assertEqual(r_get.headers['Content-Type'], 'text/html; charset=utf-8')
        #Test That you can update an Ingredient
        r_post = requests.post(Ingredient_URL,data=test_ingredient)
        print(r_post.json())
        self.assertEqual(r_post.status_code, 400)
        self.assertEqual(r_post.headers['Content-Type'], 'application/json')

        # print(r_get.url)
        # self.assertEqual(r.content, "html/text")
    # def test_delete_ingredient(self):
    #         Ingredient_URL = f"{API_URL}/ingredient/delete/{test_id}"
    #         #Test Page load and form presents
    #         r_get = requests.get(Ingredient_URL)
    #         self.assertEqual(r_get.status_code, 200)
    #         self.assertEqual(r_get.headers['Content-Type'], 'text/html; charset=utf-8')
        
if __name__ == '__main__':
    unittest.main()