"""
Umumiy sozlamalar: niche konfiguratsiyasi va yordamchi funksiyalar.
Barcha sahifalar (app.py, pages/*.py) shu fayldan import qiladi.
"""

import os
import json

NICHES = {
    "horror_stories": {
        "name": "Horror Stories",
        "language": "en",
        "voice": "en-US-GuyNeural",
        "topic_prompt": (
            "Come up with 5 original, scary, mysterious, shocking story ideas in the style "
            "of the Mr. Nightmare YouTube channel. Each should be a short, catchy title."
        ),
        "script_prompt": (
            "Based on the topic above, write a 60-90 second horror story script IN ENGLISH. "
            "Style: first-person, tense, with an unexpected ending. "
            "Write each sentence on its own line."
        ),
        "title_prompt": (
            "Write a YouTube video title for this story in the style of the Mr. Nightmare "
            "channel, catchy and attention-grabbing."
        ),
        "image_style": "dark, cinematic, horror atmosphere, moody lighting, realistic",
        "sfx_options": ["door_creak", "scream", "heartbeat", "whoosh", "jumpscare", "none"],
    },
    "horror_stories_es": {
        "name": "Horror Stories (Español)",
        "language": "es",
        "voice": "es-ES-AlvaroNeural",
        "topic_prompt": (
            "Crea 5 ideas originales de historias de terror, misteriosas e impactantes, "
            "al estilo del canal de YouTube Mr. Nightmare. Cada una debe ser un titulo corto y llamativo."
        ),
        "script_prompt": (
            "Basandote en el tema anterior, escribe un guion de historia de terror de 60-90 "
            "segundos EN ESPANOL. Estilo: primera persona, tenso, con un final inesperado. "
            "Escribe cada frase en su propia linea."
        ),
        "title_prompt": (
            "Escribe un titulo de video de YouTube para esta historia al estilo del canal "
            "Mr. Nightmare, llamativo y atractivo."
        ),
        "image_style": "dark, cinematic, horror atmosphere, moody lighting, realistic",
        "sfx_options": ["door_creak", "scream", "heartbeat", "whoosh", "jumpscare", "none"],
    },
    "smersh_stories": {
        "name": "SMERSH / War Stories",
        "language": "ru",
        "voice": "ru-RU-DmitryNeural",
        "topic_prompt": (
            "Придумай 5 драматичных сюжетов в стиле канала Холодный взгляд: контрразведка "
            "СМЕРШ, шпионаж, предательство, тайны Второй мировой войны."
        ),
        "script_prompt": (
            "На основе этой темы напиши драматичный сценарий на 60-90 секунд НА РУССКОМ "
            "ЯЗЫКЕ, с неожиданным поворотом в конце. Каждое предложение на отдельной строке."
        ),
        "title_prompt": (
            "Напиши заголовок для YouTube видео в стиле канала Холодный взгляд, интригующий."
        ),
        "image_style": "WWII era, dramatic cinematic lighting, soviet military uniforms, gritty realistic",
        "sfx_options": ["gunshot", "footsteps", "paper_rustle", "tension_hit", "whoosh", "none"],
    },
    "uncover_history": {
        "name": "Uncover History",
        "language": "en",
        "voice": "en-US-ChristopherNeural",
        "topic_prompt": (
            "Come up with 5 documentary-style video ideas in the style of the 'Uncover History' "
            "YouTube channel: hidden geopolitical history, colonialism, secret deals, oil, empires "
            "and how powerful nations covertly controlled events (e.g. 'How Britain and the CIA "
            "Overthrew a Country to Keep Its Oil'). Each should be a short, dramatic title revealing "
            "a hidden historical fact."
        ),
        "script_prompt": (
            "Based on the topic above, write a 60-90 second documentary narration script IN ENGLISH. "
            "Style: serious, authoritative documentary narrator, revealing a hidden or shocking "
            "historical truth, building tension, ending with an ironic or thought-provoking line. "
            "Write each sentence on its own line."
        ),
        "title_prompt": (
            "Write a YouTube video title for this story in the style of the 'Uncover History' "
            "channel (e.g. 'X: How [power] Did [action] To Keep [outcome]'), dramatic and revealing."
        ),
        "image_style": (
            "sepia vintage historical photograph, old map with arrows, archival documentary style, "
            "aged paper texture, black and white or sepia tone, dramatic historical lighting"
        ),
        "sfx_options": ["paper_rustle", "tension_hit", "whoosh", "clock_tick", "none"],
    },
}

# SFX fayllari shu papkada saqlanadi (siz GitHub'ga yuklaysiz): sfx/<nomi>.mp3
# Masalan: sfx/door_creak.mp3, sfx/scream.mp3, sfx/heartbeat.mp3 va h.k.
SFX_DIR = "sfx"

# Fon musiqa fayllari (siz yuklaysiz): music/<niche_key>.mp3
MUSIC_DIR = "music"

# YouTube token bu faylda saqlanadi (personal, bitta foydalanuvchi uchun)
TOKEN_PATH = "youtube_token.json"

YOUTUBE_SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
]


def youtube_is_connected() -> bool:
    return os.path.exists(TOKEN_PATH)


def save_youtube_token(credentials):
    data = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }
    with open(TOKEN_PATH, "w") as f:
        json.dump(data, f)


def load_youtube_credentials():
    from google.oauth2.credentials import Credentials

    if not youtube_is_connected():
        return None
    with open(TOKEN_PATH) as f:
        data = json.load(f)
    return Credentials(
        token=data["token"],
        refresh_token=data["refresh_token"],
        token_uri=data["token_uri"],
        client_id=data["client_id"],
        client_secret=data["client_secret"],
        scopes=data["scopes"],
    )


def disconnect_youtube():
    if os.path.exists(TOKEN_PATH):
        os.remove(TOKEN_PATH)
