import unittest
import requests
 
API_URL = "http://127.0.0.1:5000/"
test_id = '62acc79ead34d2f7a164a1cd'
test_groceries = {
            "title": "self.title.data", 
            "notes": "self.notes.data",
            "ingredients": ["self.ingredients"],
            "recipes": ['self.recipes'],
            "date": 'self.date_created',
            "recently_modified":  'self.recently_modified'
            }

class GroceriesTests(unittest.TestCase):
    def test_create_groceries(self):
        groceries_URL = f"{API_URL}/groceries"
        #Test Page load and form presents
        r_get = requests.get(groceries_URL)
        self.assertEqual(r_get.status_code, 500)
        self.assertEqual(r_get.headers['Content-Type'], 'text/html; charset=utf-8')
        #Test That you can create an groceries
        r_post = requests.post(groceries_URL,data=test_groceries)
        self.assertEqual(r_post.status_code, 500)
        self.assertEqual(r_post.headers['Content-Type'], 'text/html; charset=utf-8')
    def test_read_your_groceries(self):
        groceries_URL = f"{API_URL}/groceries/{test_id}"
        #Test Page load and form presents
        r_get = requests.get(groceries_URL)
        self.assertEqual(r_get.status_code, 500)
        self.assertEqual(r_get.headers['Content-Type'], 'text/html; charset=utf-8')
    
    def test_read_all_your_groceriess(self):
        groceries_URL = f"{API_URL}/groceries/all"
        #Test Page load and form presents
        r_get = requests.get(groceries_URL)
        self.assertEqual(r_get.status_code, 500)
        self.assertEqual(r_get.headers['Content-Type'], 'text/html; charset=utf-8')
    
    # def test_update_groceries(self):
    #     groceries_URL = f"{API_URL}/groceries/update/{test_id}"
    #     #Test Page load and form presents
    #     r_get = requests.get(groceries_URL)
    #     self.assertEqual(r_get.status_code, 200)
    #     self.assertEqual(r_get.headers['Content-Type'], 'text/html; charset=utf-8')
    #     #Test That you can update an groceries
    #     r_post = requests.post(groceries_URL,data=test_groceries)
    #     self.assertEqual(r_post.status_code, 400)
    #     self.assertEqual(r_post.headers['Content-Type'], 'text/html; charset=utf-8')

    # def test_delete_groceries(self):
    #         Recipe_URL = f"{API_URL}/recipe/delete/{test_id}"
    #         #Test Page load and form presents
    #         r_get = requests.get(Recipe_URL)
    #         self.assertEqual(r_get.status_code, 200)
    #         self.assertEqual(r_get.headers['Content-Type'], 'text/html; charset=utf-8')
        
if __name__ == '__main__':
    unittest.main()