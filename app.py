import streamlit as st
import requests
import pandas as pd
import os

# Ρυθμίσεις για απόλυτη ορατότητα και καθαρότητα
st.set_page_config(page_title="Ice's Multilingual Library", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: white; }
    h1, h2, h3, p, label, .stMarkdown { color: #000000 !important; }
    .book-box { 
        padding: 20px; 
        border: 2px solid #000000; 
        border-radius: 8px; 
        background-color: #fcfcfc; 
        margin-bottom: 15px; 
    }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "library_data.csv"

def save_book(data):
    df = pd.DataFrame([data])
    if not os.path.isfile(DB_FILE):
        df.to_csv(DB_FILE, index=False)
    else:
        df.to_csv(DB_FILE, mode='a', header=False, index=False)

def fetch_book(query, mode="ISBN"):
    # Αν είναι ISBN, δοκιμάζουμε πρώτα Open Library (για ακρίβεια) και μετά Google
    if mode == "ISBN":
        isbn = query.replace("-", "").strip()
        # Open Library
        try:
            r = requests.get(f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data", timeout=5).json()
            key = f"ISBN:{isbn}"
            if key in r:
                b = r[key]
                return {"Title": b.get("title"), "Author": ", ".join([a['name'] for a in b.get("authors", [])]), "Cover": b.get("cover", {}).get("large", "")}
        except: pass
    
    # Αν αποτύχει ή αν ψάχνουμε με τίτλο, πάμε στην Google (που έχει τα ελληνικά)
    g_url = f"https://www.googleapis.com/books/v1/volumes?q={query}"
    try:
        g_res = requests.get(g_url, timeout=5).json()
        if "items" in g_res:
            b = g_res["items"][0]["volumeInfo"]
            return {
                "Title": b.get("title", "Unknown"),
                "Author": ", ".join(b.get("authors", ["Unknown"])),
                "Cover": b.get("imageLinks", {}).get("thumbnail", "")
            }
    except: return None
    return None

st.title("📚 Ice's Library")

tab1, tab2 = st.tabs(["➕ Προσθήκη Βιβλίου", "📂 Η Συλλογή μου"])

with tab1:
    mode = st.radio("Αναζήτηση με:", ["ISBN", "Τίτλο ή Συγγραφέα (για Ελληνικά)"])
    user_input = st.text_input("Γράψτε εδώ (ISBN ή π.χ. 'Τσουκούρου Μουρακάμι'):")
    
    if user_input:
        res = fetch_book(user_input, mode="ISBN" if "ISBN" in mode else "Title")
        
        if res:
            st.markdown('<div class="book-box">', unsafe_allow_html=True)
            c1, c2 = st.columns([1, 2])
            with c1:
                if res["Cover"]: st.image(res["Cover"])
                else: st.write("📷 Χωρίς εξώφυλλο")
            with c2:
                st.subheader(res["Title"])
                st.write(f"**Συγγραφέας:** {res['Author']}")
                if st.button("💾 Αποθήκευση"):
                    save_book(res)
                    st.toast("📘 Αποθηκεύτηκε!")
                    st.write("📚📚📚")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.error("Δεν βρέθηκε. Δοκιμάστε να γράψετε τον τίτλο στα ελληνικά.")

with tab2:
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE).drop_duplicates()
        df = df.sort_values("Author")
        
        # Φίλτρο αναζήτησης μέσα στη συλλογή
        search_my = st.text_input("🔍 Αναζήτηση στη λίστα μου:")
        if search_my:
            df = df[df['Title'].str.contains(search_my, case=False) | df['Author'].str.contains(search_my, case=False)]

        authors = df["Author"].unique()
        for auth in authors:
            with st.expander(f"👤 {auth}"):
                books = df[df["Author"] == auth]
                for i, row in books.iterrows():
                    st.write(f"📖 {row['Title']}")
    else:
        st.write("Το ράφι είναι άδειο.")
