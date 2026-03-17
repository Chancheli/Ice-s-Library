import streamlit as st
import requests
import time

# Ρυθμίσεις Σελίδας
st.set_page_config(page_title="Ice's Library Expert", page_icon="📚", layout="centered")

# Custom CSS για πιο "βιβλιοφιλική" εμφάνιση
st.markdown("""
    <style>
    .stApp {
        background-color: #fcfaf5;
    }
    .book-card {
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #5d4037;
        background-color: white;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📚 Ice's Multilingual Library")
st.subheader("Εξειδικευμένη Οργάνωση: Ελληνικά, Αγγλικά, Ισπανικά")

def get_book_info(isbn):
    # Καθαρισμός ISBN
    isbn = isbn.replace("-", "").replace(" ", "")
    
    # Πηγή 1: Google Books
    google_url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
    
    try:
        response = requests.get(google_url, timeout=5)
        data = response.json()
        
        if "items" in data:
            b = data["items"][0]["volumeInfo"]
            return {
                "title": b.get("title", "Άγνωστος Τίτλος"),
                "authors": ", ".join(b.get("authors", ["Άγνωστος Συγγραφέας"])),
                "lang": b.get("language", "??").upper(),
                "cover": b.get("imageLinks", {}).get("thumbnail", None),
                "description": b.get("description", "Δεν υπάρχει περιγραφή."),
                "found": True
            }
    except:
        pass
    return None

# Interface
isbn_input = st.text_input("Εισάγετε το ISBN του βιβλίου σας:", placeholder="π.χ. 9786180107562")

if isbn_input:
    with st.spinner('Αναζήτηση στις διεθνείς βάσεις...'):
        book = get_book_info(isbn_input)
    
    if book:
        st.markdown(f'<div class="book-card">', unsafe_allow_html=True)
        col1, col2 = st.columns([1, 2])
        
        with col1:
            if book["cover"]:
                st.image(book["cover"], use_container_width=True)
            else:
                st.info("📷 Χωρίς Εξώφυλλο")
        
        with col2:
            st.header(book["title"])
            st.write(f"**Συγγραφέας:** {book['authors']}")
            st.write(f"**Γλώσσα:** {book['lang']}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Το "Αγκάθι": Έλεγχος ορθότητας
        st.write("---")
        correct = st.radio("Είναι τα στοιχεία σωστά;", ("Ναι, είναι σωστά", "Όχι, είναι λάθος (Ελληνικό ISBN)"))
        
        if correct == "Όχι, είναι λάθος (Ελληνικό ISBN)":
            st.warning("⚠️ Οι διεθνείς βάσεις συχνά μπερδεύουν τα ελληνικά βιβλία.")
            new_title = st.text_input("Γράψτε τον σωστό Τίτλο & Συγγραφέα (π.χ. Murakami - Ο Άχρωμος Τσουκούρου):")
            if st.button("Αποθήκευση με Διόρθωση"):
                # Εφέ με βιβλιαράκια αντί για μπαλόνια
                st.toast("📖 Προστέθηκε στη συλλογή!")
                time.sleep(0.5)
                st.write("✨ Αποθηκεύτηκε: " + new_title + " 📚📚📚")
        else:
            if st.button("✅ Προσθήκη στη Συλλογή"):
                st.toast("📖 Το βιβλίο μπήκε στο ράφι!")
                st.write("📘📕📗📙") # Τα χαριτωμένα βιβλιαράκια σου
                
    else:
        st.error("Το ISBN δεν βρέθηκε αυτόματα.")
        with st.expander("Χειροκίνητη Προσθήκη"):
            manual_title = st.text_input("Τίτλος & Συγγραφέας")
            if st.button("Αποθήκευση Χειροκίνητα"):
                st.toast("📖 Αποθηκεύτηκε!")
                st.write("📚")

# Footer
st.markdown("---")
st.caption("Ice's Library Project 2026 - Powered by AI")
