"""
Sozlamalar — YouTube kanalni ulash.

MUHIM: bu login emas — bu "ruxsat berish" (authorization) oqimi.
Foydalanuvchi avval bosh sahifada Google orqali login qilgan bo'lishi kerak,
keyin shu yerda YouTube'ga video yuklash/statistika ko'rish ruxsatini beradi.
"""

import streamlit as st
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

from common import (
    YOUTUBE_SCOPES,
    youtube_is_connected,
    save_youtube_token,
    load_youtube_credentials,
    disconnect_youtube,
)

st.set_page_config(page_title="Sozlamalar - NurAuto", page_icon="⚙️")

st.title("⚙️ Sozlamalar")

if not st.user.is_logged_in:
    st.warning("Avval bosh sahifada Google orqali kiring.")
    st.page_link("app.py", label="⬅️ Bosh sahifaga qaytish")
    st.stop()

st.write(f"Kirgan hisob: **{st.user.email}**")
st.divider()

st.subheader("📺 YouTube Kanal Ulash")


def get_flow():
    return Flow.from_client_config(
        {
            "web": {
                "client_id": st.secrets["youtube_oauth"]["client_id"],
                "client_secret": st.secrets["youtube_oauth"]["client_secret"],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=YOUTUBE_SCOPES,
        redirect_uri=st.secrets["youtube_oauth"]["redirect_uri"],
    )


# Google'dan qaytgandan keyin URL'da "code" parametri bo'ladi
query_params = st.query_params
if "code" in query_params and not youtube_is_connected():
    try:
        flow = get_flow()
        flow.fetch_token(code=query_params["code"])
        save_youtube_token(flow.credentials)
        st.query_params.clear()
        st.rerun()
    except Exception as e:
        st.error(f"Ulanishda xatolik: {e}")

if youtube_is_connected():
    st.success("✅ YouTube kanal ulangan!")
    try:
        creds = load_youtube_credentials()
        youtube = build("youtube", "v3", credentials=creds)
        resp = youtube.channels().list(part="snippet,statistics", mine=True).execute()
        if resp.get("items"):
            channel = resp["items"][0]
            st.write(f"**Kanal:** {channel['snippet']['title']}")
            st.write(f"**Obunachilar:** {channel['statistics'].get('subscriberCount', 'N/A')}")
    except Exception as e:
        st.warning(f"Kanal ma'lumotlarini olishda xatolik: {e}")

    if st.button("🔌 Ulanishni uzish"):
        disconnect_youtube()
        st.rerun()
else:
    st.info("Video yuklash va kanal statistikasini olish uchun YouTube kanalingizni ulang.")
    st.markdown(
        """
        Ulash orqali quyidagilarga ruxsat berasiz:
        - ✅ Kanal statistikasini olish
        - ✅ Video yuklash
        - ✅ Analitika (views, audience)
        """
    )
    flow = get_flow()
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )
    st.link_button("🔗 YouTube Bilan Ulash", auth_url, type="primary")
  
