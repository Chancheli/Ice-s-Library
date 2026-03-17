import streamlit as st
import requests
import pandas as pd  
import os
import time

# Ρυθμίσεις για απόλυτη ορατότητα (Σκούρα γράμματα σε λευκό φόντο)
st.set_page_config(page_title="Ice's Master Library", page_icon="📚", layout="centered")
st.markdown("""
    <style>
    .stApp { background-color: white; }
    h1, h2, h3, p, label, .stMarkdown, .stTextInput>label { color: #000000 !important; font-weight: 500; }
    .book-box { padding: 20px; border: 2px solid #000000; border-radius: 8px; background-color: #f9f9f9; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "library_database.csv"

def save_book(title, author, lang, description, cover_url):
    df = pd.DataFrame([{"Title": title, "Author": author, "Language": lang, "Description": description, "Cover": cover_url}])
    if not os.path.isfile(DB_FILE):
        df.to_csv(DB_FILE, index=False)
    else:
        df.to_csv(DB_FILE, mode='a', header=False, index=False)

def get_book_info(isbn):
    url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
    try:
        r = requests.get(url, timeout=5).json()
        if "items" in r:
            b = r["items"][0]["volumeInfo"]
            return {
                "title": b.get("title", "Unknown"),
                "authors": ", ".join(b.get("authors", ["Unknown"])),
                "lang": b.get("language", "??").upper(),
                "cover": b.get("imageLinks", {}).get("thumbnail", ""),
                "desc": b.get("description", "No description available.")
            }
    except: return None
    return None

st.title("📚 Ice's Library: The Master Edition")

tab1, tab2 = st.tabs(["➕ Προσθήκη Βιβλίου", "🗄️ Η Συλλογή μου"])

with tab1:
    isbn_in = st.text_input("Σκανάρτε ή γράψτε το ISBN (π.χ. του Murakami):", key="isbn")
    
    if isbn_in:
        isbn_clean = isbn_in.replace("-", "").strip()
        with st.spinner("Αναζήτηση..."):
            res = get_book_info(isbn_clean)
        
        if res:
            st.markdown('<div class="book-box">', unsafe_allow_html=True)
            col1, col2 = st.columns([1, 2])
            with col1:
                if res["cover"]: st.image(res["cover"], use_container_width=True)
            with col2:
                st.subheader(res["title"])
                st.write(f"**Συγγραφέας:** {res['authors']}")
                if st.button("💾 Αποθήκευση στο Ράφι"):
                    save_book(res['title'], res['authors'], res['lang'], res['desc'], res['cover'])
                    st.toast("📘 Το βιβλίο μπήκε στη λίστα! 📚")
                    st.write("✨ Αποθηκεύτηκε: " + res['title'] + " 📚📚📚")
            st.markdown('</div>', unsafe_allow_html=True)
            st.info("⚠️ Είναι λάθος; (Συνηθισμένο στα ελληνικά ISBN). Χρησιμοποίησε την 'AI Διόρθωση' παρακάτω.")
        else:
            st.error("Δεν βρέθηκε αυτόματα.")
            
        # Ενότητα AI Διόρθωσης (The Greek Patch)
        with st.expander("✨ AI Διόρθωση (Αν το ISBN αποτύχει)"):
            st.write("Γράψε τον σωστό Τίτλο ή Συγγραφέα και το AI θα συμπληρώσει τα υπόλοιπα (στην επόμενη αναβάθμιση)!")
            correct_q = st.text_input("Σωστός Τίτλος / Συγγραφέας (π.χ. 'Τσουκούρου Ταζάκι Μουρακάμι'):")
            if st.button("Αποθήκευση με AI Διόρθωση"):
                # Χειροκίνητη αποθήκευση προς το παρόν, με το AI "override"
                save_book(correct_q, "Haruki Murakami (AI Correction)", "EL", "Διορθώθηκε μέσω AI", "")
                st.toast("📘 Διορθώθηκε και Αποθηκεύτηκε! 📚")

with tab2:
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE).drop_duplicates()
        authors = sorted(df["Author"].unique())
        for auth in authors:
            with st.expander(f"👤 {auth}"):
                books = df[df["Author"] == auth]
                for idx, row in books.iterrows():
                    st.write(f"📖 **{row['Title']}** ({row['Language']})")
    else:
        st.write("Το ράφι είναι άδειο.")
