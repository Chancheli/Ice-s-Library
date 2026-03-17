import streamlit as st
import requests
import pandas as pd
import os

# Ρυθμίσεις για απόλυτη ορατότητα
st.set_page_config(page_title="Ice's Library v3", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: white; }
    h1, h2, h3, p, label, .stMarkdown { color: #000000 !important; }
    .book-box { 
        padding: 20px; 
        border: 2px solid #000000; 
        border-radius: 5px; 
        background-color: #f9f9f9; 
        margin-bottom: 15px; 
    }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "library_data.csv"

def save_book(data):
    df = pd.DataFrame([data])
    if not os.path.isfile(DB_FILE):
        df.to_csv(DB_FILE, index=False)
    else:
        df.to_csv(DB_FILE, mode='a', header=False, index=False)

def fetch_from_open_library(isbn):
    url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
    try:
        r = requests.get(url, timeout=10).json()
        key = f"ISBN:{isbn}"
        if key in r:
            b = r[key]
            return {
                "Title": b.get("title", "Unknown"),
                "Author": ", ".join([a['name'] for a in b.get("authors", [])]),
                "Cover": b.get("cover", {}).get("large", ""),
                "Source": "Open Library"
            }
    except: return None
    return None

st.title("📚 Ice's Private Collection")

tab1, tab2 = st.tabs(["➕ Προσθήκη", "🗄️ Αρχείο ανά Συγγραφέα"])

with tab1:
    isbn_in = st.text_input("Δώστε ISBN (π.χ. 9780552146159):")
    if isbn_in:
        isbn_clean = isbn_in.replace("-", "").strip()
        with st.spinner("Αναζήτηση..."):
            res = fetch_from_open_library(isbn_clean)
        
        if res:
            st.markdown('<div class="book-box">', unsafe_allow_html=True)
            c1, c2 = st.columns([1, 2])
            with c1:
                if res["Cover"]: st.image(res["Cover"])
            with c2:
                st.subheader(res["Title"])
                st.write(f"**Συγγραφέας:** {res['Author']}")
                if st.button("💾 Οριστική Αποθήκευση"):
                    save_book(res)
                    st.success(f"Το βιβλίο '{res['Title']}' μπήκε στο αρχείο!")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.error("Δεν βρέθηκε. Δοκιμάστε να γράψετε τον τίτλο χειροκίνητα στο Tab 'Αρχείο'.")

with tab2:
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE).drop_duplicates()
        df = df.sort_values("Author")
        authors = df["Author"].unique()
        for auth in authors:
            with st.expander(f"👤 {auth}"):
                books = df[df["Author"] == auth]
                for i, row in books.iterrows():
                    st.write(f"📖 {row['Title']}")
    else:
        st.write("Το αρχείο είναι κενό.")
