import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import pandas as pd
import os
import cv2
import numpy as np
import easyocr

# Ρυθμίσεις για καθαρή εμφάνιση (Μαύρα γράμματα - Λευκό φόντο)
st.set_page_config(page_title="Ice's Master Library", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: white; }
    h1, h2, h3, p, label, .stMarkdown { color: #000000 !important; font-weight: 500; }
    .stButton>button { background-color: #000; color: white; border-radius: 5px; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "library_data.csv"

def save_to_db(title, author):
    df = pd.DataFrame([{"Title": title, "Author": author}])
    if not os.path.isfile(DB_FILE): df.to_csv(DB_FILE, index=False)
    else: df.to_csv(DB_FILE, mode='a', header=False, index=False)

# Αρχικοποίηση του EasyOCR (για Ελληνικά και Αγγλικά)
# Σημείωση: Αυτό μπορεί να πάρει λίγο χρόνο την πρώτη φορά που θα τρέξει
@st.cache_resource
def load_reader():
    return easyocr.Reader(['el', 'en'], gpu=False) # gpu=False γιατί το Streamlit Cloud συνήθως δεν έχει GPU

reader = load_reader()

# Ο "εγκέφαλος" που επεξεργάζεται το βίντεο live
class BookTitleReader(VideoTransformerBase):
    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        
        # Επεξεργασία εικόνας για καλύτερο OCR (προαιρετικά)
        # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Προσπάθεια ανάγνωσης κειμένου
        results = reader.readtext(img)
        
        # Σχεδίαση πλαισίων γύρω από το κείμενο που βρέθηκε
        for (bbox, text, prob) in results:
            if prob > 0.5: # Μόνο αν η βεβαιότητα είναι > 50%
                (top_left, top_right, bottom_right, bottom_left) = bbox
                top_left = (int(top_left[0]), int(top_left[1]))
                bottom_right = (int(bottom_right[0]), int(bottom_right[1]))
                cv2.rectangle(img, top_left, bottom_right, (0, 255, 0), 2)
                cv2.putText(img, text, (top_left[0], top_left[1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        return img

st.title("📸 Ice's Smart Library")

tab1, tab2 = st.tabs(["🎥 LIVE SCANNER", "📂 Η Συλλογή μου"])

with tab1:
    st.subheader("Σκανάρισμα σε πραγματικό χρόνο")
    st.write("Στρέψε την κάμερα στο εξώφυλλο του βιβλίου.")
    st.write("⚠️ *Σημείωση: Το live σκανάρισμα σε browser είναι ακόμα πειραματικό και μπορεί να είναι αργό.*")
    
    # Ζωντανή ροή κάμερας με τον "εγκέφαλο" (VideoTransformer)
    webrtc_streamer(key="ice-smart-scanner", video_transformer_factory=BookTitleReader)
    
    st.divider()
    
    # Πεδία αυτόματης συμπλήρωσης μετά το σκανάρισμα
    st.write("### Αποτέλεσμα Σκαναρίσματος")
    st.write("⚠️ *Αυτή η έκδοση δεν 'τραβάει' αυτόματα το κείμενο στα πεδία ακόμα.*")
    
    col1, col2 = st.columns(2)
    with col1:
        found_title = st.text_input("Τίτλος που βρέθηκε:")
    with col2:
        found_author = st.text_input("Συγγραφέας που βρέθηκε:")
    
    if st.button("💾 ΑΠΟΘΗΚΕΥΣΗ ΣΤΗ ΣΥΛΛΟΓΗ"):
        if found_title:
            save_to_db(found_title, found_author)
            st.toast("📖 Το βιβλίο αποθηκεύτηκε!")
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
