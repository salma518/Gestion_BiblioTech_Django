import requests
from .models import Livre

class GutendexAPI:
    BASE_URL = "https://gutendex.com/books/"
    
    @classmethod
    def search_books(cls, query=None, page=1):
        params = {}
        if query:
            params['search'] = query
        params['page'] = page
        
        try:
            response = requests.get(cls.BASE_URL, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching from Gutendex: {e}")
            return None
    
    @classmethod
    def get_book_details(cls, book_id):
        try:
            response = requests.get(f"{cls.BASE_URL}{book_id}/")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching book details: {e}")
            return None