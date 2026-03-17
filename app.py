import streamlit as st
import requests

st.set_page_config(page_title="Ice's Library", page_icon="📚")

st.title("📚 Ice's Multilingual Library")
st.markdown("Σάρωση βιβλίων σε Ελληνικά, Αγγλικά, Ισπανικά & Γαλλικά")

def get_book_info(isbn):
    # Πηγή 1: Google Books (Πολύ καλό για ελληνικά & αγγλικά)
    google_url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
    
    # Πηγή 2: Open Library (Καλό για ευρωπαϊκές εκδόσεις & παλαιότερα βιβλία)
    openlib_url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
    
    res = {"title": None, "authors": None, "lang": None, "cover": None, "source": ""}

    # Δοκιμή Google
    try:
        g_resp = requests.get(google_url).json()
        if "items" in g_resp:
            b = g_resp["items"][0]["volumeInfo"]
            res["title"] = b.get("title")
            res["authors"] = ", ".join(b.get("authors", []))
            res["lang"] = b.get("language", "").upper()
            res["cover"] = b.get("imageLinks", {}).get("thumbnail")
            res["source"] = "Google Books"
            return res
    except: pass

    # Δοκιμή Open Library (αν αποτύχει η Google)
    try:
        o_resp = requests.get(openlib_url).json()
        key = f"ISBN:{isbn}"
        if key in o_resp:
            b = o_resp[key]
            res["title"] = b.get("title")
            res["authors"] = ", ".join([a['name'] for a in b.get("authors", [])])
            res["cover"] = b.get("cover", {}).get("large")
            res["source"] = "Open Library"
            return res
    except: pass
    
    return None

isbn_input = st.text_input("Σκανάρτε ή πληκτρολογήστε το ISBN:")

if isbn_input:
    isbn_clean = isbn_input.replace("-", "").replace(" ", "")
    data = get_book_info(isbn_clean)
    
    if data:
        col1, col2 = st.columns([1, 2])
        with col1:
            if data["cover"]: st.image(data["cover"])
        with col2:
            st.header(data["title"])
            st.subheader(data["authors"])
            st.write(f"🌐 Γλώσσα: {data.get('lang', 'N/A')}")
            st.caption(f"Πηγή δεδομένων: {data['source']}")
        
        if st.button("✅ Προσθήκη στη Συλλογή"):
            st.balloons()
            st.success("Αποθηκεύτηκε!")
    else:
        st.error("Δεν βρέθηκε! Δοκιμάστε να γράψετε τον τίτλο.")
        manual_t = st.text_input("Τίτλος (χειροκίνητα)")
        if st.button("Αποθήκευση"):
            st.write("Οκ, το κράτησα!")
