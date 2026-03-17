import streamlit as st
import requests
import pandas as pd
import os

# Καθαρή εμφάνιση
st.set_page_config(page_title="Ice's Master Library", layout="centered")
st.markdown("""
    <style>
    .stApp { background-color: white; }
    h1, h2, h3, p, label { color: #1a1a1a !important; }
    .book-card { 
        padding: 20px; border: 2px solid #333; border-radius: 10px; 
        background-color: #fdfdfd; margin-bottom: 10px; 
    }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "ice_library.csv"

def save_book(title, author, cover):
    df = pd.DataFrame([{"Title": title, "Author": author, "Cover": cover}])
    if not os.path.isfile(DB_FILE):
        df.to_csv(DB_FILE, index=False)
    else:
        df.to_csv(DB_FILE, mode='a', header=False, index=False)

def search_books(query):
    # Ψάχνουμε γενικά (όχι μόνο ISBN) για να βρίσκουμε τα πάντα
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}"
    try:
        r = requests.get(url, timeout=10).json()
        if "items" in r:
            results = []
            for item in r["items"][:3]: # Παίρνουμε τα 3 πρώτα αποτελέσματα
                b = item["volumeInfo"]
                results.append({
                    "title": b.get("title", "Unknown"),
                    "author": ", ".join(b.get("authors", ["Unknown"])),
                    "cover": b.get("imageLinks", {}).get("thumbnail", "")
                })
            return results
    except: return []
    return []

st.title("📚 Ice's Library: Final Edition")

tab1, tab2 = st.tabs(["✨ Προσθήκη", "🗄️ Η Συλλογή μου"])

with tab1:
    search_q = st.text_input("Γράψε ISBN ή απλά τον Τίτλο (π.χ. Τσουκούρου Ταζάκι):")
    
    if search_q:
        results = search_books(search_q)
        if results:
            st.write("### Βρέθηκαν τα παρακάτω:")
            for res in results:
                with st.container():
                    st.markdown('<div class="book-card">', unsafe_allow_html=True)
                    c1, c2 = st.columns([1, 3])
                    with c1:
                        if res["cover"]: st.image(res["cover"])
                    with c2:
                        st.subheader(res["title"])
                        st.write(f"**Συγγραφέας:** {res['author']}")
                        if st.button(f"Προσθήκη: {res['title'][:20]}...", key=res['title']):
                            save_book(res['title'], res['author'], res['cover'])
                            st.toast("📖 Μπήκε στο ράφι!")
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.error("Δεν βρέθηκε τίποτα. Μήπως να το γράψεις χειροκίνητα;")

with tab2:
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE).drop_duplicates()
        authors = sorted(df["Author"].unique())
        for auth in authors:
            with st.expander(f"👤 {auth}"):
                books = df[df["Author"] == auth]
                for _, row in books.iterrows():
                    col_a, col_b = st.columns([1, 4])
                    with col_a:
                        if row['Cover']: st.image(row['Cover'], width=50)
                    with col_b:
                        st.write(f"**{row['Title']}**")
    else:
        st.info("Το ράφι είναι άδειο.")
        
