import asyncio
import json
import os
import re
import html
import requests
from twikit import Client

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
X_AUTH_TOKEN = os.environ.get("X_AUTH_TOKEN")
X_CT0 = os.environ.get("X_CT0")

STATE_FILE = "last_seen_us.json"

HANDLES = [
    "GreciMM18",
    "BasedMikeLee", "TrumpWarRoom", "EricLDaugh", "MAGAVoice", "GuntherEagleman",
    "TheSCIF", "RapidResponse47", "bennyjohnson", "nicksortor", "JackPosobiec",
    "Real_RobN", "LauraLoomer", "NathanielSami", "LindseyGrahamSC", "elonmusk",
    "johnnymaga", "mcucolo57", "Interior", "libsoftiktok", "BPUnion",
    "howardlutnick", "SenRandPaul", "realDonaldTrump", "USAmbIndia", "altcap",
    "TheJusticeDept", "MrWhiplash_", "BuzzPatterson", "OneBadDude_", "WallStreetApes",
    "marklevinshow", "VigilantFox", "marcthiessen", "TaraBull", "WhiteHouse",
    "ACTBrigitte", "AbrahamHamadeh", "SteveGuest", "JayTC53", "EYakoby",
    "JDunlap1974", "its_Lexieroy", "irishpatriot91", "glennbeck", "interiorpress47",
    "FoxNews", "GreereMedeea", "FreedomCaucusF", "IngrahamAngle", "IHF_Heritage"
]

KEYWORDS_REGEX = re.compile(
    r"\b("
    r"m[eé]xic\w*|mexican\w*|"
    r"claudia\s*sheinbaum|sheinbaum|"
    r"roberto\s*velasco|velasco\s*[aá]lvarez|@r_velascoa|"
    r"usmca|t-?mec|nafta\s*2\.0"
    r")\b",
    re.IGNORECASE
)

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def clean_html(raw_html):
    clean = re.sub(r"<[^>]+>", " ", raw_html)
    return " ".join(clean.split())

def send_telegram(handle, text, link):
    safe_text = html.escape(text)
    message = (
        f"🦅 <b>[GreciaMiniAlgoritmoMAGA]</b>\n"
        f"👤 <b>Cuenta:</b> @{handle}\n\n"
        f"{safe_text}\n\n"
        f"🔗 <a href='{link}'>Ver publicación</a>"
    )
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Error al enviar mensaje: {e}")

async def main():
    state = load_state()
    is_initial_run = (len(state) == 0)

    client = Client('en-US')

    # Inyección directa de cookies de sesión sin pasar por login
    client.set_cookies({
        'auth_token': X_AUTH_TOKEN,
        'ct0': X_CT0
    })

    print(f"=== Monitoreando {len(HANDLES)} cuentas con sesión autenticada ===")

    for handle in HANDLES:
        last_id = state.get(handle)
        try:
            user = await client.get_user_by_screen_name(handle)
            tweets = await user.get_tweets('Tweets', count=5)
            print(f"✅ @{handle}: {len(tweets)} tuits obtenidos.")
        except Exception as e:
            print(f"❌ Error al consultar @{handle}: {e}")
            continue

        if not tweets:
            continue

        if is_initial_run or last_id is None:
            state[handle] = str(tweets[0].id)
            continue

        new_tweets = []
        for t in tweets:
            t_id = str(t.id)
            if t_id == last_id:
                break
            new_tweets.append(t)

        for t in reversed(new_tweets):
            full_text = clean_html(t.text)
            if KEYWORDS_REGEX.search(full_text):
                print(f"🚨 COINCIDENCIA en @{handle}: {full_text[:60]}")
                t_link = f"https://x.com/{handle}/status/{t.id}"
                preview = full_text[:400] + ("..." if len(full_text) > 400 else "")
                send_telegram(handle, preview, t_link)

        if new_tweets:
            state[handle] = str(new_tweets[0].id)

    save_state(state)
    print("=== Monitoreo finalizado exitosamente ===")

if __name__ == "__main__":
    asyncio.run(main())
