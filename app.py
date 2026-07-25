"""
NurAuto — Asosiy sahifa.
Bu yerda faqat Google orqali "kim ekaningizni" aniqlash (login) bo'ladi.
"""

import streamlit as st

st.set_page_config(page_title="NurAuto", page_icon="🎬", layout="centered")

st.title("🎬 NurAuto — AI YouTube Video Studio")
st.write("Sun'iy intellekt yordamida YouTube uchun professional videolarni avtomatik yarating!")

st.divider()

# st.user xavfsizligini tekshirish uchun try-except
is_logged_in = False
user_name = ""
user_email = ""

try:
    if hasattr(st, "user") and st.user.is_logged_in:
        is_logged_in = True
        user_name = getattr(st.user, "name", "Foydalanuvchi")
        user_email = getattr(st.user, "email", "")
except Exception:
    is_logged_in = False

if not is_logged_in:
    st.subheader("🔐 Tizimga kirish")
    st.write("Davom etish uchun Google hisobingiz orqali kiring.")
    if st.button("Google orqali kirish", type="primary"):
        st.login()
else:
    st.success(f"Xush kelibsiz, {user_name}! ({user_email})")
    st.write("Chap tomondagi menyudan davom eting:")
    st.page_link("pages/1_Sozlamalar.py", label="⚙️ Sozlamalar (YouTube kanalni ulash)")
    st.page_link("pages/2_Video_Yaratish.py", label="🎬 Video Yaratish")
    if st.button("Chiqish"):
        st.logout()
      
