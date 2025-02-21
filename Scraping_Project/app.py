from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import os
from urllib.parse import urljoin

app = Flask(__name__)
df_books = None  

BASE_URL = "http://books.toscrape.com/"

def scrape_books_to_scrape(pages=2):
    base_page_url = urljoin(BASE_URL, "catalogue/page-{}.html")
    all_books = []
    
    for page_num in range(1, pages + 1):
        url = base_page_url.format(page_num)
        response = requests.get(url)
        if response.status_code == 200:
            response.encoding = "utf-8"
            soup = BeautifulSoup(response.text, "html.parser")
            articles = soup.find_all("article", class_="product_pod")
            
            for article in articles:
                title = article.h3.a["title"]
                price_str = article.find("p", class_="price_color").text
                # Nettoyage de la chaîne de prix
                clean_price_str = re.sub(r'[^0-9\.,]+', '', price_str).replace(',', '.')
                price = float(clean_price_str)
                availability = article.find("p", class_="instock availability").text.strip()
                rating_str = article.find("p", class_="star-rating")["class"]
                rating_map = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}
                rating = rating_map.get(rating_str[1], 0)
                
                image_rel_url = article.find("img")["src"]
                image_url = urljoin(BASE_URL, image_rel_url)
                image_tag = f'<img src="{image_url}" width="100">'
                
                all_books.append({
                    "title": title,
                    "price": price,
                    "availability": availability,
                    "rating": rating,
                    "image": image_tag
                })
        else:
            print(f"Erreur sur la page {page_num}")
    
    return pd.DataFrame(all_books)

@app.route("/", methods=["GET"])
def home():
    return render_template("welcome.html")

@app.route("/scrape", methods=["GET", "POST"])
def scrape():
    global df_books
    if request.method == "POST":
        pages = request.form.get("pages")
        try:
            pages = int(pages)
        except ValueError:
            pages = 2  # Valeur par défaut
        df_books = scrape_books_to_scrape(pages=pages)
        df_books.to_csv("books.csv", index=False, encoding="utf-8")
    else:
        if df_books is None:
            try:
                df_books = pd.read_csv("books.csv")
            except Exception:
                return "Aucune donnée disponible. Veuillez d'abord lancer le scraping depuis la page d'accueil."
        pages = request.args.get("pages", "inconnu")
    
    max_price = request.args.get("max_price", None)
    if max_price:
        try:
            max_price_val = float(max_price)
            df_filtered = df_books[df_books["price"] <= max_price_val]
        except ValueError:
            df_filtered = df_books
    else:
        df_filtered = df_books
    
    sort_order = request.args.get("sort", None)
    if sort_order == "asc":
        df_filtered = df_filtered.sort_values(by="price", ascending=True)
    elif sort_order == "desc":
        df_filtered = df_filtered.sort_values(by="price", ascending=False)
    
    table_html = df_filtered.to_html(classes="table table-striped", index=False, escape=False)
    return render_template("scrape_result.html",
                           table_html=table_html,
                           pages=pages,
                           sort_order=sort_order,
                           max_price=max_price or "")

if __name__ == "__main__":
    app.run(debug=True)
