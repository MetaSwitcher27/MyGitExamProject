import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

if not os.path.exists("static"):
    os.mkdir("static")

def analyze_books(csv_file="books.csv"):
    df = pd.read_csv(csv_file)

    df_under_20 = df[df['price'] < 20]
    avg_price_under_20 = df_under_20['price'].mean()
    print(f"Prix moyen des livres à moins de 20€ : {avg_price_under_20:.2f}")

    # Graphique 1: Histogramme de la distribution des prix
    plt.figure(figsize=(8,5))
    sns.histplot(df['price'], bins=10, kde=True)
    plt.title("Distribution des prix des livres")
    plt.xlabel("Prix (£)")
    plt.ylabel("Nombre de livres")
    plt.savefig("static/distribution_prix.png")
    plt.close()  
    
    # Graphique 2: Nuage de points rating vs price
    plt.figure(figsize=(8,5))
    sns.scatterplot(data=df, x='rating', y='price')
    plt.title("Rating vs. Price")
    plt.savefig("static/rating_vs_price.png")
    plt.close() 

if __name__ == "__main__":
    analyze_books()
