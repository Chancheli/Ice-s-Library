 import streamlit as st
import pandas as pd
import os
import easyocr
import numpy as np
import cv2
from PIL import Image

# Ρυθμίσεις για καθαρή εμφάνιση
st.set_page_config(page_title="Ice's Greek Library", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: white; }
    h1, h2, h3, p, label { color: black !important; font-weight: 500; }
    .stButton>button { background-color: #000; color: white; width: 100%; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "library_data.csv"

# Φόρτωση του OCR με πρόβλεψη για σφάλματα
@st.cache_resource
def load_ocr():
    try:
        # Δοκιμάζουμε να φορτώσουμε Ελληνικά και Αγγλικά
        return easyocr.Reader(['el', 'en'], gpu=False)
    except:
        # Αν αποτύχει το cloud, φορτώνει μόνο Αγγλικά για να μην κρασάρει το app
        return easyocr.Reader(['en'], gpu=False)

reader = load_ocr()

def save_to_db(title, author):
    df = pd.DataFrame([{"Title": title, "Author": author}])
    if not os.path.isfile(DB_FILE): df.to_csv(DB_FILE, index=False)
    else: df.to_csv(DB_FILE, mode='a', header=False, index=False)

st.title("📚 Ice's Greek Library Scanner")

tab1, tab2 = st.tabs(["📷 ΣΚΑΝΑΡΙΣΜΑ", "📂 Η ΣΥΛΛΟΓΗ ΜΟΥ"])

with tab1:
    st.subheader("Σκανάρισμα Εξωφύλλου")
    
    # Χρήση της κάμερας του κινητού/PC
    img_file = st.camera_input("Βάλε το βιβλίο στο πλαίσιο")
    
    if img_file:
        # Μετατροπή εικόνας για το AI
        file_bytes = np.asarray(bytearray(img_file.read()), dtype=np.uint8)
        opencv_image = cv2.imdecode(file_bytes, 1)
        
        with st.spinner("Το AI διαβάζει τα Ελληνικά..."):
            result = reader.readtext(opencv_image)
            # Ενώνουμε όλα τα κείμενα που βρήκε σε μια λίστα
            detected_text = [res[1] for res in result if res[2] > 0.2]
            full_text = " ".join(detected_text)
        
        st.success("Ανάγνωση ολοκληρώθηκε!")
        
        # Πεδία για επιβεβαίωση
        st.write("### Επιβεβαίωση Στοιχείων")
        final_title = st.text_input("Τίτλος:", value=full_text)
        final_author = st.text_input("Συγγραφέας:", placeholder="Γράψε τον συγγραφέα αν δεν βρέθηκε")
        
        if st.button("💾 ΑΠΟΘΗΚΕΥΣΗ ΣΤΗ ΣΥΛΛΟΓΗ"):
            if final_title:
                save_to_db(final_title, final_author)
                st.toast("📘 Αποθηκεύτηκε!")
                st.balloons()

with tab2:
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE).drop_duplicates()
        st.write(f"Έχεις **{len(df)}** βιβλία.")
        
        # Ταξινόμηση και προβολή
        for idx, row in df.iterrows():
            with st.container():
                st.markdown(f"**{row['Title']}**")
                st.caption(f"Συγγραφέας: {row['Author']}")
                st.divider()
    else:
        st.info("Το ράφι είναι άδειο.")


