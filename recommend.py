import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
import os
import glob

# 📌 Automatically find the latest CSV file from folder
def get_latest_csv(folder_path):
    list_of_files = glob.glob(os.path.join(folder_path, '*.csv'))
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file

# 📌 Replace 'scraped_data_folder' with your folder path containing scraped CSVs
folder_path = r'\\ANMOL\Users\SANDWICH\Desktop\Recommendation System'
latest_csv = get_latest_csv(folder_path)
print(f"📦 Using latest scraped file: {os.path.basename(latest_csv)}")

# 📌 Load the latest scraped CSV
df = pd.read_csv(latest_csv)

# 📌 Clean numeric columns
df['Price (₹)'] = df['Price (₹)'].replace('N/A', np.nan).str.replace(',', '').astype(float)
df['Rating'] = df['Rating'].replace('N/A', np.nan).str.extract(r'([0-9.]+)').astype(float)
df['Reviews'] = df['Reviews'].replace('N/A', '0').str.replace(',', '').astype(float)

# 📌 Fill missing product features
df['Product Features'] = df['Product Features'].fillna('')

# 📌 Vectorize product features using TF-IDF
vectorizer = TfidfVectorizer(stop_words='english')
features_tfidf = vectorizer.fit_transform(df['Product Features'])

# 📌 Compute cosine similarity matrix (text-based similarity)
cos_sim = cosine_similarity(features_tfidf)

# 📌 Normalize numeric columns (Price, Rating, Reviews)
scaler = MinMaxScaler()
df[['Price_norm', 'Rating_norm', 'Reviews_norm']] = scaler.fit_transform(
    df[['Price (₹)', 'Rating', 'Reviews']].fillna(0)
)

# 📌 Calculate final recommendation score
final_score = (0.6 * cos_sim) + (0.2 * df['Rating_norm'].values[:, None]) + \
              (0.1 * df['Reviews_norm'].values[:, None]) - (0.1 * df['Price_norm'].values[:, None])

# 📌 Product recommendation function
def recommend_products(product_index, top_n=5):
    scores = final_score[product_index]
    recommended_indices = scores.argsort()[-top_n-1:-1][::-1]  # Exclude self
    recommended_df = df.iloc[recommended_indices][['Product Name', 'Product Features', 'Price (₹)', 'Rating', 'Reviews']]
    recommended_df['Similarity Score'] = scores[recommended_indices]
    return recommended_df

# 📌 Example usage: recommend products similar to product at index 0
print(f"\nRecommendations similar to: {df.iloc[0]['Product Name']}\n")
recommendations = recommend_products(0, 5)
print(recommendations)

# 📌 Optionally save recommendations to CSV
output_csv = os.path.join(folder_path, "recommended_products.csv")
recommendations.to_csv(output_csv, index=False)
print(f"\n✅ Top recommendations saved to '{output_csv}'")
