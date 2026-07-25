"""
NurAuto — Asosiy sahifa.
Bu yerda faqat Google orqali "kim ekaningizni" aniqlash (login) bo'ladi.
YouTube'ga video yuklash ruxsati BU YERDA SO'RALMAYDI — u alohida,
"Sozlamalar" sahifasida so'raladi (chunki bu boshqa turdagi ruxsat).
"""

import streamlit as st

st.set_page_config(page_title="NurAuto", page_icon="🎬", layout="centered")

st.title("🎬 NurAuto — AI YouTube Video Studio")
st.write("Sun'iy intellekt yordamida YouTube uchun professional videolarni avtomatik yarating!")

st.divider()

if not st.user.is_logged_in:
    st.subheader("🔐 Tizimga kirish")
    st.write("Davom etish uchun Google hisobingiz orqali kiring.")
    if st.button("Google orqali kirish", type="primary"):
        st.login()
else:
    st.success(f"Xush kelibsiz, {st.user.name}! ({st.user.email})")
    st.write("Chap tomondagi menyudan davom eting:")
    st.page_link("pages/1_Sozlamalar.py", label="⚙️ Sozlamalar (YouTube kanalni ulash)")
    st.page_link("pages/2_Video_Yaratish.py", label="🎬 Video Yaratish")
    if st.button("Chiqish"):
        st.logout()
