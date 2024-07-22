import requests
import json
from fastapi import FastAPI, Request, HTTPException
from bs4 import BeautifulSoup
from product import Product

url: str = "https://dentalstall.com/shop/page"
app = FastAPI()
auth_token: str = 'atlys_be_token'
rupee_icon ='\u20b9'


def store_scrapped_data(data: list[Product], storage_type: str):
    if len(data) < 0:
        print("No content to create a json file")
        return
    else:
        if storage_type == 'local':
            print("Content available to write in the json file")
            with open("scrapped_data.json", "w") as json_output:
                json_data = [product.to_dict() for product in data]
                json.dump(json_data, json_output)
        else:
            print("Use a different storage option")

def scrape_page(page_number: int, search: str):
    pages_scrapped = []
    for page in range(1, page_number+1):
        page_url = f"{url}/{page}"
        page_response = requests.get(page_url)
        print(f"{page_url} responded with status {page_response.status_code}")
        if page_response.status_code != 200:
            print(f"Non 200 response found for {page_url} {page_response.status_code}")
            page_response.raise_for_status()
        soup = BeautifulSoup(page_response.content, 'html.parser')
        pages_scrapped = [*pages_scrapped, *extract_product_info(soup, search, page)]
    store_scrapped_data(pages_scrapped, 'local')
    return pages_scrapped
        
def extract_product_info(htmlPageResponseSoup, search: str, page: int):
    products = htmlPageResponseSoup.select('li.type-product')
    scrapped_items = []
    for index, product in products:
        product_image:str = product.find('img', class_='attachment-woocommerce_thumbnail').attrs['data-lazy-src'].strip()
        product_title:str = product.find('h2', class_='woo-loop-product__title').text.strip()
        product_price:str = product.find('bdi').text.strip()
        product_hash: str = f"page_{page}_index_{index}"
        if not search or search.trim().lower() in product_title.trim().lower():
            create_product = Product(product_hash, product_price, rupee_icon, product_title, product_image)
            if not create_product.check_if_product_exist_and_same_price(curr_product=create_product):
                scrapped_items.append(create_product)

    return scrapped_items

@app.get("/scrape")
def scrape_pages(request: Request, page: int = 1, search: str = ''):
    try:
        if page <= 0:
            raise HTTPException(status_code=400, detail='Page number cannot be less than or equal to zero')
        token = request.headers.get('token') or 'default'
        if token != auth_token:
            print("Authentication Failed")
            raise HTTPException(status_code=401, detail="Authentication Failed")
        scrapped = scrape_page(page, search)
        if len(scrapped) <= 0:
            raise HTTPException(status_code=40, detail="No items found for scrapping")
        print(f"The number of items scrapped {len(scrapped)}. Scrapping status: success")
        return {"total_items": len(scrapped), "scrapping_status": "success"}
    except requests.HTTPError as err:
        print(f"HTTPError Caught {err}")
        return err
    except requests.ConnectionError as conn_err:
        print(f"ConnectionError Caught {conn_err}")
        raise HTTPException(status_code=500, detail="Failed to connect to the external service")
    
