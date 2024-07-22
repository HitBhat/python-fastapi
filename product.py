import hashlib
import json

class Product:
    def __init__(self, product_hash: str, product_price: str, rupee_icon, product_title: str, product_image: str):
        self.product_id = self.hash_product_key(product_hash)
        self.product_price = self.split_price_get_int(product_price, rupee_icon)
        self.product_title = product_title
        self.path_to_image = product_image

    @staticmethod
    def split_price_get_int(price_str: str, icon: str):
        if not price_str:
            return -1
        return int(float(price_str.split(icon)[1]))
    
    @staticmethod
    def hash_product_key(input_string: str):
        hash_object = hashlib.sha256()
        hash_object.update(input_string.encode('utf-8'))
        return hash_object.hexdigest()

    def to_dict(self):
        return {
            'product_id': self.product_id,
            'product_price': self.product_price,
            'product_title': self.product_title,
            'path_to_image': self.path_to_image
        }
    
    def check_if_product_exist_and_same_price(self, curr_product):
        try:
            with open("scrapped_data.json", "r") as json_file:
                data = json.load(json_file)
            
            for stored_product in data:
                if stored_product['product_id'] == curr_product['product_id']:
                    old_price = stored_product['product_price']
                    current_price = curr_product['product_price']

                    if old_price != current_price:
                        return True
                    else:
                        return False
        except FileNotFoundError:
            print("scrapped_data.json file not found.")
            return False
        except json.JSONDecodeError:
            print("Error decoding JSON from scrapped_data.json.")
            return False





