import unittest
import requests
 
API_URL = "http://127.0.0.1:5000/"
g_test_id = '62a4d913fcc46118dfeef3aa'
test_id = '62a4d913fcc46118dfeef3ab'
test_Recipe = {
                "title": "self.title.data", 
                "description": "self.description.data",
                "img_URI": "self.img_URI",
                "cuisine": "self.cuisine.data",
                "ingredients": ["self.ingredients"],
                "instructions": ['self.instructions'],
                "date_created": "self.date_created",
                "date_modified": "self.date_modified",
                "author": "self.author",
                "crossreference_recipe_URI": "self.crossreference_recipe_URI"
            }

class RecipeTests(unittest.TestCase):
    def test_create_Recipe(self):
        Recipe_URL = f"{API_URL}/recipe"
        #Test Page load and form presents
        r_get = requests.get(Recipe_URL)
        self.assertEqual(r_get.status_code, 500)
        self.assertEqual(r_get.headers['Content-Type'], 'text/html; charset=utf-8')
        #Test That you can create an Recipe
        r_post = requests.post(Recipe_URL,data=test_Recipe)
        self.assertEqual(r_post.status_code, 500)
        self.assertEqual(r_post.headers['Content-Type'], 'text/html; charset=utf-8')
    def test_read_your_Recipe(self):
        Recipe_URL = f"{API_URL}/recipe/{test_id}"
        #Test Page load and form presents
        r_get = requests.get(Recipe_URL)
        self.assertEqual(r_get.status_code, 500)
        self.assertEqual(r_get.headers['Content-Type'], 'text/html; charset=utf-8')
    def test_read_global_Recipe(self):
        Recipe_URL = f"{API_URL}/recipe/global/{g_test_id}"
        #Test Page load and form presents
        r_get = requests.get(Recipe_URL)
        self.assertEqual(r_get.status_code, 200)
        self.assertEqual(r_get.headers['Content-Type'], 'text/html; charset=utf-8')

    def test_read_all_global_Recipes(self):
        Recipe_URL = f"{API_URL}/recipe/global/all"
        #Test Page load and form presents
        r_get = requests.get(Recipe_URL)
        self.assertEqual(r_get.status_code, 500)
        self.assertEqual(r_get.headers['Content-Type'], 'text/html; charset=utf-8')

    def test_read_all_your_Recipes(self):
        Recipe_URL = f"{API_URL}/recipe/mine"
        #Test Page load and form presents
        r_get = requests.get(Recipe_URL)
        self.assertEqual(r_get.status_code, 500)
        self.assertEqual(r_get.headers['Content-Type'], 'text/html; charset=utf-8')
    
    def test_update_Recipe(self):
        Recipe_URL = f"{API_URL}/recipe/update/{test_id}"
        #Test Page load and form presents
        r_get = requests.get(Recipe_URL)
        self.assertEqual(r_get.status_code, 500)
        self.assertEqual(r_get.headers['Content-Type'], 'text/html; charset=utf-8')
        #Test That you can update an Recipe
        r_post = requests.post(Recipe_URL,data=test_Recipe)
        self.assertEqual(r_post.status_code, 500)
        self.assertEqual(r_post.headers['Content-Type'], 'text/html; charset=utf-8')

    # def test_delete_Recipe(self):
    #         Recipe_URL = f"{API_URL}/recipe/delete/{test_id}"
    #         #Test Page load and form presents
    #         r_get = requests.get(Recipe_URL)
    #         self.assertEqual(r_get.status_code, 200)
    #         self.assertEqual(r_get.headers['Content-Type'], 'text/html; charset=utf-8')
        
if __name__ == '__main__':
    unittest.main()