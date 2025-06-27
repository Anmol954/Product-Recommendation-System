import streamlit as st
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
from scraper import scrape_amazon_products  # your scraper function

# Set page config
st.set_page_config(page_title="🛍️ Live Product Recommender", layout="wide")

st.title("🛍️ Live Amazon Product Recommendation System")

# User inputs
product_input = st.text_input("🔍 Enter product keyword (e.g. 'Wireless Earphones')")
max_pages = st.slider("📄 How many Amazon pages to scrape?", 1, 5, 2)

if st.button("🔎 Scrape and Recommend"):
    if not product_input:
        st.warning("Please enter a product keyword.")
        st.stop()

    with st.spinner("Scraping products from Amazon live..."):
        df = scrape_amazon_products(product_input, max_pages=max_pages)

    if df.empty:
        st.error("No products found. Try a different search term.")
        st.stop()

    st.success(f"Scraped {len(df)} products.")

    # Clean data
    df['Price (₹)'] = df['Price (₹)'].replace('N/A', np.nan).astype(str).str.replace(',', '').astype(float)
    df['Rating'] = df['Rating'].replace('N/A', np.nan).astype(str).str.extract(r'([0-9.]+)').astype(float)
    df['Reviews'] = df['Reviews'].replace('N/A', '0').astype(str).str.replace(',', '').astype(float)
    df['Product Features'] = df['Product Features'].fillna('')

    # Vectorize product features
    vectorizer = TfidfVectorizer(stop_words='english')
    features_tfidf = vectorizer.fit_transform(df['Product Features'])
    cos_sim = cosine_similarity(features_tfidf)

    # Normalize numerical columns
    scaler = MinMaxScaler()
    df[['Price_norm', 'Rating_norm', 'Reviews_norm']] = scaler.fit_transform(
        df[['Price (₹)', 'Rating', 'Reviews']].fillna(0)
    )

    # Final weighted score
    final_score = (0.6 * cos_sim) + \
                  (0.2 * df['Rating_norm'].values[:, None]) + \
                  (0.1 * df['Reviews_norm'].values[:, None]) - \
                  (0.1 * df['Price_norm'].values[:, None])

    # Product list for dropdown
    product_list = df['Product Name'].tolist()
    selected_product = st.selectbox("Select a product to get recommendations:", product_list)

    if selected_product:
        product_index = df[df['Product Name'] == selected_product].index[0]

        # Recommendations
        scores = final_score[product_index]
        recommended_indices = scores.argsort()[-6:-1][::-1]

        recommendations = df.iloc[recommended_indices][
            ['Product Name', 'Product Features', 'Price (₹)', 'Rating', 'Reviews']
        ].copy()

        recommendations['Similarity Score'] = scores[recommended_indices]
        recommendations['Price (₹)'] = recommendations['Price (₹)'].apply(
            lambda x: f"₹{int(x):,}" if pd.notnull(x) and x != 0 else "N/A"
        )

        st.subheader(f"📊 Top 5 similar recommendations for: {selected_product}")
        st.dataframe(recommendations)

        # Download button
        csv = recommendations.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Download Recommendations CSV",
            csv,
            f"recommendations_for_{selected_product}.csv",
            "text/csv"
        )

    st.markdown("---")
    st.markdown("Made by Anmol 👌")
