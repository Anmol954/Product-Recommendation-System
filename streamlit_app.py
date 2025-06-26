import streamlit as st
import pandas as pd
import numpy as np
import os
import glob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler

def get_latest_csv(folder_path):
    list_of_files = glob.glob(os.path.join(folder_path, '*.csv'))
    list_of_files = [f for f in list_of_files if os.path.getsize(f) > 0]
    if not list_of_files:
        return None
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file

def load_and_prepare_data(file):
    df = pd.read_csv(file)
    df.rename(columns={"Price (â‚¹)": "Price", "Price (₹)": "Price"}, inplace=True)

    required_columns = ['Product Name', 'Product Features', 'Price', 'Rating', 'Reviews']
    for col in required_columns:
        if col not in df.columns:
            st.error(f"Missing required column: '{col}'")
            st.stop()

    df['Price'] = df['Price'].replace('N/A', np.nan).astype(str).str.replace(',', '').astype(float)
    df['Rating'] = df['Rating'].replace('N/A', np.nan).astype(str).str.extract(r'([0-9.]+)').astype(float)
    df['Reviews'] = df['Reviews'].replace('N/A', '0').astype(str).str.replace(',', '').astype(float)
    df['Product Features'] = df['Product Features'].fillna('')

    return df

def generate_recommendations(df):
    vectorizer = TfidfVectorizer(stop_words='english')
    features_tfidf = vectorizer.fit_transform(df['Product Features'])
    cos_sim = cosine_similarity(features_tfidf)

    scaler = MinMaxScaler()
    df[['Price_norm', 'Rating_norm', 'Reviews_norm']] = scaler.fit_transform(
        df[['Price', 'Rating', 'Reviews']].fillna(0)
    )

    final_score = (0.6 * cos_sim) + (0.2 * df['Rating_norm'].values[:, None]) + \
                  (0.1 * df['Reviews_norm'].values[:, None]) - (0.1 * df['Price_norm'].values[:, None])

    return final_score

def recommend_products(df, final_score, product_index, top_n=5):
    scores = final_score[product_index]
    recommended_indices = scores.argsort()[-top_n-1:-1][::-1]
    recommended_df = df.iloc[recommended_indices][['Product Name', 'Product Features', 'Price', 'Rating', 'Reviews']]
    recommended_df['Similarity Score'] = scores[recommended_indices]
    return recommended_df

st.title("🛍️ Product Recommendation System")

uploaded_file = st.file_uploader("Upload your product CSV file", type="csv")

if uploaded_file:
    df = load_and_prepare_data(uploaded_file)
    filename = uploaded_file.name
else:
    st.info("No file uploaded. Trying to use the latest CSV from local folder.")
    folder_path = '.'
    latest_csv = get_latest_csv(folder_path)
    if latest_csv:
        df = load_and_prepare_data(latest_csv)
        filename = os.path.basename(latest_csv)
        st.success(f"Loaded local file: `{filename}`")
    else:
        st.error("No valid CSV found in local folder. Please upload a file.")
        st.stop()

if df.empty:
    st.error("The loaded file has no data.")
    st.stop()

final_score = generate_recommendations(df)

product_list = df['Product Name'].tolist()
selected_product = st.selectbox("Select a product to get recommendations:", product_list)

product_index = df[df['Product Name'] == selected_product].index[0]

st.subheader(f"Top 5 similar recommendations for: {selected_product}")
recommendations = recommend_products(df, final_score, product_index, 5)

recommendations['Price'] = recommendations['Price'].apply(lambda x: f"₹{int(x):,}" if pd.notnull(x) else "N/A")

st.dataframe(recommendations)

csv = recommendations.to_csv(index=False).encode('utf-8')
st.download_button(
    "Download Recommendations CSV",
    csv,
    f"recommendations_for_{selected_product}.csv",
    "text/csv"
)

st.markdown("---")
st.markdown("Made by Anmol")
