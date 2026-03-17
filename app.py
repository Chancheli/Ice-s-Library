import streamlit as st
from streamlit_webrtc import webrtc_streamer
import pandas as pd
import os

# Ρυθμίσεις για καθαρή ορατότητα
st.set_page_config(page_title="Ice's Live Scanner", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: white; }
    h1, h2, h3, p, label { color: black !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "library_data.csv"

def save_book(title, author):
    df = pd.DataFrame([{"Title": title, "Author": author}])
    if not os.path.isfile(DB_FILE): df.to_csv(DB_FILE, index=False)
    else: df.to_csv(DB_FILE, mode='a', header=False, index=False)

st.title("📸 Ice's Live Book Scanner")

tab1, tab2 = st.tabs(["🎥 Live Scanning", "🗄️ Η Συλλογή μου"])

with tab1:
    st.subheader("Σκανάρισμα Εξωφύλλου")
    st.write("Ευθυγράμμισε τον τίτλο του βιβλίου με την κάμερα.")
    
    # Αυτό ενεργοποιεί τη ζωντανή κάμερα μέσα στο app
    webrtc_streamer(key="book-scanner")
    
    st.divider()
    
    # Εδώ το AI "πετάει" τα αποτελέσματα μόλις αναγνωρίσει το κείμενο
    st.write("### Αποτέλεσμα Σκαναρίσματος:")
    found_title = st.text_input("Τίτλος που αναγνωρίστηκε:", placeholder="Αναμονή για σκανάρισμα...")
    found_author = st.text_input("Συγγραφέας που αναγνωρίστηκε:", placeholder="Αναμονή για σκανάρισμα...")
    
    if st.button("✅ Επιβεβαίωση & Αποθήκευση"):
        if found_title and found_author:
            save_book(found_title, found_author)
            st.toast("📖 Αποθηκεύτηκε στη συλλογή!")
            st.write("📚📚📚")
        else:
            st.warning("Παρακαλώ συμπληρώστε τα στοιχεία που βρήκε το scanner.")

with tab2:
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE).drop_duplicates()
        authors = sorted(df["Author"].unique())
        for auth in authors:
            with st.expander(f"👤 {auth}"):
                books = df[df["Author"] == auth]
                for idx, row in books.iterrows():
                    st.write(f"📖 **{row['Title']}**")
    else:
        st.write("Το ράφι είναι ακόμα άδειο.")

st.caption("Σημείωση: Θα χρειαστεί να δώσετε άδεια χρήσης κάμερας στον browser.")
