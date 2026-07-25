"""
Video Yaratish (Professional) — to'liq avtomatik pipeline:
mavzu -> ssenariy -> audio -> rasm+SFX tanlash -> subtitr -> animatsiyali video -> YouTube
"""

import os
import json
import random
import asyncio
import numpy as np
import streamlit as st
import anthropic
import edge_tts
from PIL import Image, ImageDraw, ImageFont
from google import genai
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from moviepy.editor import (
    ImageClip, AudioFileClip, CompositeVideoClip, CompositeAudioClip,
    concatenate_videoclips, vfx, afx,
)

from common import NICHES, SFX_DIR, MUSIC_DIR, youtube_is_connected, load_youtube_credentials

st.set_page_config(page_title="Video Yaratish - NurAuto", page_icon="🎬", layout="centered")
st.title("🎬 Video Yaratish")

if not st.user.is_logged_in:
    st.warning("Avval bosh sahifada Google orqali kiring.")
    st.page_link("app.py", label="⬅️ Bosh sahifaga qaytish")
    st.stop()

WORK_DIR = "work"
os.makedirs(f"{WORK_DIR}/audio", exist_ok=True)
os.makedirs(f"{WORK_DIR}/images", exist_ok=True)

VIDEO_W, VIDEO_H = 1080, 1920
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

claude_client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
gemini_client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])


def ask_claude(prompt, max_tokens=2000):
    resp = claude_client.messages.create(
        model="claude-sonnet-4-6", max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.content[0].text


def generate_image(prompt, out_path, style):
    full_prompt = f"{prompt}. Style: {style}"
    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash-image", contents=full_prompt
    )
    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            with open(out_path, "wb") as f:
                f.write(part.inline_data.data)
            return out_path
    raise RuntimeError(f"Rasm yaratilmadi: {prompt}")


async def _tts(text, voice, path):
    await edge_tts.Communicate(text, voice).save(path)


def make_subtitle_clip(text, duration, width=VIDEO_W):
    """PIL orqali subtitr rasmini chizadi (ImageMagick shart emas)."""
    font_size = 58
    try:
        font = ImageFont.truetype(FONT_PATH, font_size)
    except Exception:
        font = ImageFont.load_default()

    words = text.split()
    lines, cur = [], ""
    dummy = Image.new("RGBA", (10, 10))
    draw = ImageDraw.Draw(dummy)
    max_w = width - 80
    for w in words:
        test = (cur + " " + w).strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] > max_w and cur:
            lines.append(cur)
            cur = w
        else:
            cur = test
    if cur:
        lines.append(cur)

    line_h = font_size + 18
    img_h = line_h * len(lines) + 40
    img = Image.new("RGBA", (width, img_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        x = (width - tw) / 2
        y = 20 + i * line_h
        draw.text((x, y), line, font=font, fill="white", stroke_width=4, stroke_fill="black")

    arr = np.array(img)
    clip = ImageClip(arr).set_duration(duration)
    clip = clip.set_position(("center", VIDEO_H - img_h - 160))
    return clip


ANIMATIONS = ["zoom_in", "zoom_out", "pan_left", "pan_right"]


def animated_clip(image_path, duration, animation):
    """Har xil animatsiya turlari — professional ko'rinish uchun xilma-xillik."""
    clip = ImageClip(image_path).set_duration(duration)
    clip = clip.resize(height=int(VIDEO_H * 1.25))

    if animation == "zoom_in":
        clip = clip.resize(lambda t: 1.0 + 0.15 * (t / duration))
        clip = clip.set_position("center")
    elif animation == "zoom_out":
        clip = clip.resize(lambda t: 1.15 - 0.15 * (t / duration))
        clip = clip.set_position("center")
    elif animation == "pan_left":
        w = clip.w
        clip = clip.set_position(lambda t: (-0.08 * w * (t / duration), "center"))
    elif animation == "pan_right":
        w = clip.w
        clip = clip.set_position(lambda t: (-0.08 * w * (1 - t / duration), "center"))

    base = ImageClip(np.zeros((VIDEO_H, VIDEO_W, 3), dtype="uint8")).set_duration(duration)
    composite = CompositeVideoClip([base, clip], size=(VIDEO_W, VIDEO_H))
    return composite


niche_key = st.selectbox(
    "Niche tanlang", options=list(NICHES.keys()), format_func=lambda k: NICHES[k]["name"]
)
niche = NICHES[niche_key]

col1, col2 = st.columns(2)
with col1:
    add_subtitles = st.checkbox("Subtitr qo'shish", value=True)
with col2:
    add_sfx = st.checkbox("Tovush effektlari (SFX)", value=os.path.isdir(SFX_DIR))

if not os.path.isdir(SFX_DIR) and add_sfx:
    st.warning(
        f"⚠️ `{SFX_DIR}/` papkasi topilmadi — SFX o'chirib qo'yiladi. "
        f"SFX ishlashi uchun repo'ga `{SFX_DIR}/door_creak.mp3` kabi fayllar qo'shing."
    )
    add_sfx = False

music_path = f"{MUSIC_DIR}/{niche_key}.mp3"
has_music = os.path.exists(music_path)
if not has_music:
    st.caption(f"💡 Fon musiqa yo'q ({music_path}) — video musiqasiz yig'iladi.")

if youtube_is_connected():
    auto_upload = st.checkbox("Tayyor bo'lgach YouTube'ga avtomatik yuklash", value=False)
else:
    auto_upload = False
    st.caption("💡 YouTube ulanmagan — video faqat yuklab olish uchun tayyorlanadi.")

if st.button("🚀 Video Yaratish", type="primary"):
    progress = st.progress(0, text="Boshlanmoqda...")

    progress.progress(8, text="Mavzu tanlanmoqda...")
    topics_text = ask_claude(niche["topic_prompt"])
    topics = [l.strip("- 0123456789.").strip() for l in topics_text.split("\n") if l.strip()][:5]
    topic = topics[0]
    st.write(f"**Mavzu:** {topic}")

    progress.progress(20, text="Ssenariy yozilmoqda...")
    script_text = ask_claude(f"Topic: {topic}\n\n{niche['script_prompt']}")
    script_lines = [l.strip() for l in script_text.split("\n") if l.strip()]
    st.write(f"**{len(script_lines)} qator yaratildi**")

    title_text = ask_claude(
        f"{niche['title_prompt']}\n\nStory:\n{chr(10).join(script_lines)}", max_tokens=100
    )
    video_title = title_text.strip().strip('"')
    st.write(f"**Sarlavha:** {video_title}")

    progress.progress(32, text="Rasm va SFX rejalashtirilmoqda...")
    joined = "\n".join(f"{i+1}. {l}" for i, l in enumerate(script_lines))
    sfx_list = ", ".join(niche["sfx_options"])
    plan_prompt = (
        f"For each numbered script line below, respond with a JSON array. Each item must have:\n"
        f'- "image_prompt": a short (10-15 word) English visual prompt, style: {niche["image_style"]}\n'
        f'- "sfx": pick exactly one from this list that best fits the line: {sfx_list}\n\n'
        f"Reply with ONLY the JSON array, no other text.\n\nLines:\n{joined}"
    )
    plan_text = ask_claude(plan_prompt, max_tokens=3000)
    plan_text = plan_text.strip()
    if plan_text.startswith("```"):
        plan_text = plan_text.strip("`")
        plan_text = plan_text.replace("json\n", "", 1)
    plan = json.loads(plan_text)

    progress.progress(45, text="Audio yaratilmoqda...")
    audio_paths = []
    for i, line in enumerate(script_lines):
        path = f"{WORK_DIR}/audio/line_{i:03d}.mp3"
        asyncio.run(_tts(line, niche["voice"], path))
        audio_paths.append(path)

    progress.progress(55, text="Rasmlar generatsiya qilinmoqda...")
    image_paths = []
    for i, item in enumerate(plan):
        path = f"{WORK_DIR}/images/scene_{i:03d}.png"
        generate_image(item["image_prompt"], path, niche["image_style"])
        image_paths.append(path)
        progress.progress(55 + int(20 * (i + 1) / len(plan)), text=f"Rasm {i+1}/{len(plan)}")

    progress.progress(78, text="Video yig'ilmoqda (animatsiya, subtitr, SFX)...")
    n = min(len(image_paths), len(audio_paths), len(plan))
    scene_clips = []
    sfx_events = []
    t_cursor = 0.0

    for i in range(n):
        audio_clip = AudioFileClip(audio_paths[i])
        duration = audio_clip.duration + 0.3
        animation = ANIMATIONS[i % len(ANIMATIONS)]

        visual = animated_clip(image_paths[i], duration, animation)
        layers = [visual]

        if add_subtitles:
            sub = make_subtitle_clip(script_lines[i], duration)
            layers.append(sub)

        scene = CompositeVideoClip(layers, size=(VIDEO_W, VIDEO_H)).set_duration(duration)
        scene = scene.set_audio(audio_clip)
        scene_clips.append(scene)

        sfx_tag = plan[i].get("sfx", "none")
        if add_sfx and sfx_tag and sfx_tag != "none":
            sfx_file = f"{SFX_DIR}/{sfx_tag}.mp3"
            if os.path.exists(sfx_file):
                sfx_events.append((t_cursor, sfx_file))
        t_cursor += duration

    final = concatenate_videoclips(scene_clips, method="compose")

    audio_layers = [final.audio]
    for start, sfx_file in sfx_events:
        try:
            sfx_clip = AudioFileClip(sfx_file).set_start(start)
            audio_layers.append(sfx_clip)
        except Exception:
            pass
    if has_music:
        bg = AudioFileClip(music_path).fx(afx.audio_loop, duration=final.duration)
        bg = bg.fx(afx.volumex, 0.12)
        audio_layers.append(bg)

    if len(audio_layers) > 1:
        final = final.set_audio(CompositeAudioClip(audio_layers))

    out_path = f"{WORK_DIR}/final_video.mp4"
    final.write_videofile(out_path, fps=30, codec="libx264", audio_codec="aac")

    progress.progress(100, text="Tayyor!")
    st.success("✅ Video tayyor!")
    st.video(out_path)
    with open(out_path, "rb") as f:
        st.download_button("⬇️ Videoni yuklab olish", f, file_name="video.mp4", mime="video/mp4")

    if auto_upload:
        with st.spinner("YouTube'ga yuklanmoqda..."):
            creds = load_youtube_credentials()
            youtube = build("youtube", "v3", credentials=creds)
            body = {
                "snippet": {
                    "title": video_title,
                    "description": f"{niche['name']} | AI generated",
                    "tags": [niche_key, "shorts"],
                    "categoryId": "24",
                },
                "status": {"privacyStatus": "public"},
            }
            media = MediaFileUpload(out_path, resumable=True)
            request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
            response = None
            while response is None:
                status, response = request.next_chunk()
            video_id = response["id"]
            st.success(f"✅ YouTube'ga yuklandi: https://youtube.com/watch?v={video_id}")
          
