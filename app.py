import streamlit as st
from streamlit_webrtc import webrtc_streamer
import pandas as pd
import os
import requests

# Ρυθμίσεις για καθαρή εμφάνιση (Μαύρα γράμματα - Λευκό φόντο)
st.set_page_config(page_title="Ice's Master Library", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: white; }
    h1, h2, h3, p, label, .stMarkdown { color: #000000 !important; font-weight: 500; }
    .book-card { 
        padding: 20px; border: 2px solid #000; border-radius: 10px; 
        background-color: #f9f9f9; margin-bottom: 15px; 
    }
    .stButton>button { background-color: #000; color: white; border-radius: 5px; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "my_library_db.csv"

def save_to_db(title, author, source="Scan"):
    df = pd.DataFrame([{"Title": title, "Author": author, "Source": source}])
    if not os.path.isfile(DB_FILE):
        df.to_csv(DB_FILE, index=False)
    else:
        df.to_csv(DB_FILE, mode='a', header=False, index=False)

def fetch_book_info(query):
    # Αυτή η συνάρτηση βοηθάει το scanner να βρει τις λεπτομέρειες
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}"
    try:
        r = requests.get(url, timeout=5).json()
        if "items" in r:
            b = r["items"][0]["volumeInfo"]
            return b.get("title", ""), ", ".join(b.get("authors", ["Άγνωστος"]))
    except: return None, None
    return None, None

st.title("📚 Ice's Smart Library")

tab1, tab2 = st.tabs(["📸 LIVE SCANNER", "📂 Η ΒΙΒΛΙΟΘΗΚΗ ΜΟΥ"])

with tab1:
    st.subheader("Σκανάρισμα σε πραγματικό χρόνο")
    st.write("Στρέψε την κάμερα στο εξώφυλλο του βιβλίου.")
    
    # Ζωντανή ροή κάμερας
    webrtc_streamer(key="ice-scanner")
    
    st.divider()
    
    # Πεδία αυτόματης συμπλήρωσης μετά το σκανάρισμα
    st.write("### Στοιχεία Βιβλίου")
    col1, col2 = st.columns(2)
    with col1:
        scanned_title = st.text_input("Τίτλος (από Scanner):", key="t_in")
    with col2:
        scanned_author = st.text_input("Συγγραφέας (από Scanner):", key="a_in")
    
    if st.button("💾 ΑΠΟΘΗΚΕΥΣΗ ΣΤΗ ΣΥΛΛΟΓΗ"):
        if scanned_title:
            save_to_db(scanned_title, scanned_author)
            st.success(f"Το βιβλίο '{scanned_title}' προστέθηκε!")
            st.balloons()
        else:
            st.error("Πρέπει να υπάρχει ένας τίτλος για να γίνει η αποθήκευση.")

with tab2:
    if os.path.exists(DB_FILE):
        library_df = pd.read_csv(DB_FILE).drop_duplicates()
        library_df = library_df.sort_values(by="Author")
        
        st.write(f"Σύνολο βιβλίων: **{len(library_df)}**")
        
        # Ομαδοποίηση ανά Συγγραφέα
        authors = library_df["Author"].unique()
        for auth in authors:
            with st.expander(f"👤 {auth}"):
                books = library_df[library_df["Author"] == auth]
                for idx, row in books.iterrows():
                    st.write(f"📖 {row['Title']}")
    else:
        st.info("Η βιβλιοθήκη σου είναι ακόμα άδεια. Ξεκίνα το σκανάρισμα!")
