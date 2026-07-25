# NurAuto — YouTube AI Video Studio (Streamlit)

## Tuzilishi
```
app.py                        — bosh sahifa, Google login
pages/1_Sozlamalar.py         — YouTube kanalni ulash
pages/2_Video_Yaratish.py     — AI video generatsiya pipeline
common.py                     — niche sozlamalari, yordamchi funksiyalar
requirements.txt               — Python kutubxonalari
packages.txt                   — tizim paketlari (ffmpeg)
.streamlit/secrets_template.toml — Secrets namunasi (GitHub'ga yuklamang!)
```

## Professional xususiyatlar
- **4 ta niche**: Horror Stories (ingliz), Horror Stories Español (ispan), SMERSH/War Stories
  (rus), Uncover History (ingliz, yashirin tarix/geosiyosat uslubida)
- **Subtitr**: har bir jumla video pastida avtomatik chiqadi (ImageMagick shart emas, PIL orqali)
- **Turli animatsiya**: zoom-in, zoom-out, pan-left, pan-right — sahnalar orasida almashib turadi
- **Tovush effektlari (SFX)**: AI har bir sahna uchun mos effektni tanlaydi (masalan eshik
  g'ichirlashi, yurak urishi) — buning uchun **siz o'zingiz bepul SFX fayllarni topib,
  repo'ga qo'yishingiz kerak**:
  ```
  sfx/door_creak.mp3
  sfx/scream.mp3
  sfx/heartbeat.mp3
  sfx/whoosh.mp3
  sfx/jumpscare.mp3
  sfx/gunshot.mp3
  sfx/footsteps.mp3
  sfx/paper_rustle.mp3
  sfx/tension_hit.mp3
  sfx/clock_tick.mp3
  ```
  Bepul manbalar: pixabay.com/sound-effects (mualliflik huquqisiz, ro'yxatdan o'tib yuklab olinadi)
- **Fon musiqa**: har bir niche uchun alohida, ixtiyoriy:
  ```
  music/horror_stories.mp3
  music/horror_stories_es.mp3
  music/smersh_stories.mp3
  music/uncover_history.mp3
  ```
  Agar fayl bo'lmasa, video shunchaki musiqasiz yig'iladi (xato bermaydi).


Shu papkadagi barcha fayllarni yangi GitHub repozitoriysiga yuklang.
**`.streamlit/secrets_template.toml` faylini repo'ga qo'ymang** — bu faqat namuna,
haqiqiy kalitlar Streamlit Cloud panelida saqlanadi (pastga qarang).

## 2-qadam: Google Cloud sozlash

### a) Loyiha va API'larni yoqish
1. console.cloud.google.com → yangi loyiha yarating (yoki mavjudini tanlang)
2. **APIs & Services → Library** → qidiring va yoqing:
   - **YouTube Data API v3**
   - **YouTube Analytics API** (agar statistikani ko'rsatmoqchi bo'lsangiz)

### b) OAuth Consent Screen
1. **APIs & Services → OAuth consent screen**
2. **Test users** bo'limiga o'zingizning va sinovchi hisoblarning email manzilini qo'shing
3. **Data Access → Add or remove scopes** — quyidagilarni qidirib belgilang:
   - `.../auth/youtube.readonly`
   - `.../auth/youtube.upload`
   - `.../auth/yt-analytics.readonly`
4. Saqlang

### c) OAuth Client ID yaratish
1. **APIs & Services → Credentials → Create Credentials → OAuth client ID**
2. Turi: **Web application**
3. **Authorized redirect URIs** bo'limiga **ikkalasini ham** qo'shing (ilovangiz deploy
   bo'lgandan keyingi **aniq** manzil bilan, oxirida qiyshiq chiziq YO'Q):
   - `https://SIZNING-ILOVA.streamlit.app/oauth2callback` (login uchun)
   - `https://SIZNING-ILOVA.streamlit.app/Sozlamalar` (YouTube ulash uchun)
4. Client ID va Client Secret'ni nusxalab oling

**MUHIM:** Streamlit ilovasini birinchi marta deploy qilganingizda unga tasodifiy
subdomen beriladi (masalan `nurauto-jyfnpbk9rh2....streamlit.app`). Shu **aniq** manzilni
yuqoridagi Authorized redirect URIs'ga va pastdagi Secrets'ga yozishingiz kerak — ular
harf-baharf bir xil bo'lishi shart, aks holda xatolik chiqadi.

## 3-qadam: Streamlit Cloud'ga deploy qilish
1. share.streamlit.io → **"New app"**
2. GitHub repozitoriyingizni, branch'ni va `app.py` faylini tanlang
3. Deploy qiling — ilova manzili (URL) beriladi

## 4-qadam: Secrets kiritish
1. Ilova sahifasida **⋮ → Settings → Secrets**
2. `.streamlit/secrets_template.toml` dagi shablonni nusxalab, **haqiqiy qiymatlar** bilan
   to'ldirib joylang (redirect_uri'larni 2-qadamdagi **aniq** manzilingiz bilan almashtiring)
3. Saqlang — ilova avtomatik qayta ishga tushadi

## 5-qadam: Sinab ko'rish
1. Ilova manzilini oching
2. "Google orqali kirish" tugmasini bosing — login ishlashi kerak
3. Sozlamalar sahifasiga o'ting, "YouTube Bilan Ulash" ni bosing
4. Video Yaratish sahifasida niche tanlab, "Video Yaratish" tugmasini bosing

## Muhim eslatmalar
- YouTube token `youtube_token.json` faylida saqlanadi — bu ilova qayta ishga
  tushirilganda (redeploy) o'chib ketishi mumkin, shunda qayta ulash kerak bo'ladi.
- Kunlik kvotalar: Gemini ~500 rasm/kun, YouTube upload ~6 video/kun (standart kvota).
- Agar ilova manzili keyinchalik o'zgarsa (masalan qayta nomlansangiz), yuqoridagi
  barcha redirect_uri qiymatlarini (Google Console + Secrets) yangi manzilga moslab
  qayta yangilashni unutmang.
