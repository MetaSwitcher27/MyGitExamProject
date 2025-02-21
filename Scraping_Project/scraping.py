import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

def scrape_books_to_scrape(pages=2):
    base_url = "http://books.toscrape.com/"
    all_books = []

    for page_num in range(1, pages + 1):
        url = base_url.format(page_num)
        response = requests.get(url)
        if response.status_code == 200:
            # Option 1 : force l'encodage
            response.encoding = "utf-8"
            soup = BeautifulSoup(response.text, "html.parser")

            articles = soup.find_all("article", class_="product_pod")
            for article in articles:
                title = article.h3.a["title"]
                price_str = article.find("p", class_="price_color").text

                clean_price_str = re.sub(r'[^0-9\.,]+', '', price_str)
                # Convertit la virgule éventuelle en point
                clean_price_str = clean_price_str.replace(',', '.')
                price = float(clean_price_str)

                availability = article.find("p", class_="instock availability").text.strip()

                rating_str = article.find("p", class_="star-rating")["class"]
                rating_map = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}
                rating_word = rating_str[1]
                rating = rating_map.get(rating_word, 0)

                all_books.append({
                    "title": title,
                    "price": price,
                    "availability": availability,
                    "rating": rating
                })
        else:
            print(f"Erreur: impossible d'accéder à la page {page_num}")

    df = pd.DataFrame(all_books)
    return df

if __name__ == "__main__":
    df_books = scrape_books_to_scrape(pages=2)
    df_books.to_csv("books.csv", index=False, encoding="utf-8")
    print("Scraping terminé. Fichier 'books.csv' créé.")
