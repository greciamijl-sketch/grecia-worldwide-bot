import json
import os
import re
import html
import sys
import time
import requests
from playwright.sync_api import sync_playwright

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
X_AUTH_TOKEN = os.environ.get("X_AUTH_TOKEN", "").strip()
X_CT0 = os.environ.get("X_CT0", "").strip()

STATE_FILE = "last_seen_diplomacy.json"

# ================= DIRECTORIO DIPLOMÁTICO GLOBAL =================
SOURCES = [
    # América del Norte
    {"region": "EE.UU.", "role": "Presidente", "author": "POTUS", "handle": "POTUS"},
    {"region": "EE.UU.", "role": "Casa Blanca", "author": "White House", "handle": "WhiteHouse"},
    {"region": "EE.UU.", "role": "Secretario de Estado", "author": "Marco Rubio", "handle": "marcorubio"},
    {"region": "CANADÁ", "role": "Primer Ministro", "author": "Mark Carney", "handle": "MarkJCarney"},
    {"region": "CANADÁ", "role": "Canciller", "author": "Anita Anand", "handle": "AnitaAnandMP"},

    # América Latina y el Caribe
    {"region": "ARGENTINA", "role": "Presidente", "author": "Javier Milei", "handle": "JMilei"},
    {"region": "BRASIL", "role": "Presidente", "author": "Lula da Silva", "handle": "LulaOficial"},
    {"region": "COLOMBIA", "role": "Presidente", "author": "Abelardo de la Espriella", "handle": "DELAESPRIELLAE"},
    {"region": "PERÚ", "role": "Presidenta", "author": "Keiko Fujimori", "handle": "KeikoFujimori"},
    {"region": "CHILE", "role": "Presidente", "author": "José Antonio Kast", "handle": "joseantoniokast"},
    {"region": "BOLIVIA", "role": "Presidente", "author": "Rodrigo Paz", "handle": "Rodrigo_PazP"},
    {"region": "ECUADOR", "role": "Presidente", "author": "Daniel Noboa", "handle": "DanielNoboaOk"},
    {"region": "URUGUAY", "role": "Presidente", "author": "Yamandú Orsi", "handle": "OrsiYamandu"},
    {"region": "PANAMÁ", "role": "Presidente", "author": "José Raúl Mulino", "handle": "JoseRaulMulino"},
    {"region": "PARAGUAY", "role": "Presidente", "author": "Santiago Peña", "handle": "SantiPenap"},
    {"region": "REP. DOMINICANA", "role": "Presidente", "author": "Luis Abinader", "handle": "luisabinader"},
    {"region": "COSTA RICA", "role": "Presidenta", "author": "Laura Fernández", "handle": "laurapresi2026"},
    {"region": "HONDURAS", "role": "Presidente", "author": "Nasry Asfura", "handle": "titoasfura"},
    {"region": "EL SALVADOR", "role": "Presidente", "author": "Nayib Bukele", "handle": "nayibbukele"},
    {"region": "GUATEMALA", "role": "Presidente", "author": "Bernardo Arévalo", "handle": "BArevalodeLeon"},

    # Europa
    {"region": "ITALIA", "role": "Presidenta del Consejo", "author": "Giorgia Meloni", "handle": "GiorgiaMeloni"},
    {"region": "UNIÓN EUROPEA", "role": "Presidenta Comisión", "author": "Ursula von der Leyen", "handle": "vonderleyen"},
    {"region": "ESPAÑA", "role": "Presidente del Gobierno", "author": "Pedro Sánchez", "handle": "sanchezcastejon"},
    {"region": "FRANCIA", "role": "Presidente", "author": "Emmanuel Macron", "handle": "EmmanuelMacron"},
    {"region": "ALEMANIA", "role": "Canciller Federal", "author": "Friedrich Merz", "handle": "_FriedrichMerz"},
    {"region": "REINO UNIDO", "role": "Primer Ministro", "author": "Andy Burnham", "handle": "AndyBurnhamGM"},
    {"region": "UCRANIA", "role": "Presidente", "author": "Volodymyr Zelenskyy", "handle": "ZelenskyyUa"},
    {"region": "RUSIA", "role": "Presidencia", "author": "Kremlin", "handle": "KremlinRussia_E"},
    {"region": "RUSIA", "role": "Cancillería en Español", "author": "Cancillería Rusia", "handle": "mae_rusia"},

    # Asia y Potencias
    {"region": "CHINA", "role": "Cancillería / Portavocía", "author": "MFA China", "handle": "MFA_China"},
    {"region": "JAPÓN", "role": "Primera Ministra", "author": "Sanae Takaichi", "handle": "takaichi_sanae"},
    {"region": "COREA DEL SUR", "role": "Presidente", "author": "Lee Jae-myung", "handle": "Jaemyung_Lee"},
    {"region": "INDIA", "role": "Primer Ministro", "author": "Narendra Modi", "handle": "narendramodi"},

    # Organismos Multilaterales
    {"region": "ONU", "role": "Secretario General", "author": "António Guterres", "handle": "antonioguterres"},
    {"region": "OEA", "role": "Secretario General", "author": "Albert Ramdin", "handle": "AlbertRamdin"},

    # Embajadas Extranjeras en México
    {"region": "EMBAJADA EE.UU. EN MÉXICO", "role": "Misión Diplomática", "author": "Embajada EE.UU. en México", "handle": "USEmbassyMEX"},
    {"region": "EMBAJADA CANADÁ EN MÉXICO", "role": "Misión Diplomática", "author": "Canadá en México", "handle": "EmbCanMexico"},
    {"region": "EMBAJADA ESPAÑA EN MÉXICO", "role": "Misión Diplomática", "author": "Embajada España en México", "handle": "EmbEspMex"},
    {"region": "EMBAJADA FRANCIA EN MÉXICO", "role": "Misión Diplomática", "author": "Francia en México", "handle": "FranciaenMexico"},
    {"region": "EMBAJADA ALEMANIA EN MÉXICO", "role": "Misión Diplomática", "author": "Alemania en México", "handle": "AlemaniaenMex"},
    {"region": "EMBAJADA REINO UNIDO EN MÉXICO", "role": "Misión Diplomática", "author": "UK in Mexico", "handle": "UKinMexico"},
    {"region": "DELEGACIÓN UE EN MÉXICO", "role": "Misión Diplomática", "author": "Unión Europea en México", "handle": "UEenMexico"},
    {"region": "EMBAJADA CHINA EN MÉXICO", "role": "Misión Diplomática", "author": "Embajada de China en México", "handle": "EmbChinaMex"},
    {"region": "EMBAJADA RUSIA EN MÉXICO", "role": "Misión Diplomática", "author": "Embajada de Rusia en México", "handle": "EmbRusiaMexico"}
]

# ================= FILTRO DIPLOMÁTICO MULTILINGÜE =================
KEYWORDS_REGEX = re.compile(
    r"\b("
    r"m[eé]xic\w*|mexican\w*|"
    r"claudia\s*sheinbaum|sheinbaum|"
    r"roberto\s*velasco|velasco\s*[aá]lvarez|@r_velascoa|"
    r"canciller\s*mexican\w*|canciller[ií]a\s*mexican\w*|"
    r"mexican\s*foreign\s*minister|foreign\s*secretary\s*of\s*mexico|"
    r"secretar[ií]a\s*de\s*relaciones\s*exteriores|@SRE_mx|"
    r"c[aá]rtel\w*"
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

def send_telegram(region, role, author, text, link):
    safe_text = html.escape(text)
    message = (
        f"🌐 <b>[GreciaWorldwide - {region}]</b>\n"
        f"🏛 <b>Cargo:</b> {role}\n"
        f"👤 <b>Emisor:</b> {author}\n\n"
        f"{safe_text}\n\n"
        f"🔗 <a href='{link}'>Ver declaración original</a>"
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
        print(f"Error al enviar a Telegram: {e}", flush=True)

def scrape_tweets(page, handle):
    url = f"https://x.com/{handle}"
    page.goto(url, wait_until="domcontentloaded", timeout=12000)

    for _ in range(2):
        page.mouse.wheel(0, 800)
        time.sleep(0.8)

    tweet_elements = page.locator("article[data-testid='tweet']").all()[:5]
    if not tweet_elements:
        tweet_elements = page.locator("div[aria-label*='Timeline'] article, section article").all()[:5]

    tweets = []
    for art in tweet_elements:
        try:
            link_elem = art.locator("a[href*='/status/']").first
            href = link_elem.get_attribute("href") if link_elem.count() > 0 else None
            if not href or "/status/" not in href:
                continue

            match_id = re.search(r"/status/(\d+)", href)
            tweet_id = match_id.group(1) if match_id else href

            text_elem = art.locator("[data-testid='tweetText']").first
            text = text_elem.inner_text() if text_elem.count() > 0 else art.inner_text()

            tweets.append({
                "id": str(tweet_id),
                "text": text,
                "link": f"https://x.com{href}" if href.startswith("/") else href
            })
        except Exception:
            continue

    return tweets

def main():
    state = load_state()
    is_initial_run = (len(state) == 0)

    print(f"=== INICIANDO MONITOREO DIPLOMÁTICO: {len(SOURCES)} FUENTES ===", flush=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-blink-features=AutomationControlled"
            ]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            locale="es-ES",
            viewport={"width": 1280, "height": 900}
        )

        context.add_cookies([
            {"name": "auth_token", "value": X_AUTH_TOKEN, "domain": ".x.com", "path": "/"},
            {"name": "ct0", "value": X_CT0, "domain": ".x.com", "path": "/"},
            {"name": "auth_token", "value": X_AUTH_TOKEN, "domain": "x.com", "path": "/"},
            {"name": "ct0", "value": X_CT0, "domain": "x.com", "path": "/"}
        ])

        page = context.new_page()

        for source in SOURCES:
            region = source["region"]
            role = source["role"]
            author = source["author"]
            handle = source["handle"]
            last_id = state.get(handle)

            try:
                tweets = scrape_tweets(page, handle)
            except Exception as e:
                print(f"❌ Error al consultar @{handle}: {e}", flush=True)
                continue

            print(f"✅ @{handle}: {len(tweets)} tuits obtenidos.", flush=True)

            if not tweets:
                continue

            if is_initial_run or last_id is None:
                state[handle] = tweets[0]["id"]
                continue

            new_tweets = []
            for t in tweets:
                if t["id"] == last_id:
                    break
                new_tweets.append(t)

            for t in reversed(new_tweets):
                full_text = clean_html(t["text"])
                if KEYWORDS_REGEX.search(full_text):
                    print(f"🚨 Coincidencia encontrada en @{handle}: {full_text[:60]}", flush=True)
                    preview = full_text[:400] + ("..." if len(full_text) > 400 else "")
                    send_telegram(region, role, author, preview, t["link"])

            if new_tweets:
                state[handle] = new_tweets[0]["id"]

        browser.close()

    save_state(state)
    print("=== FIN DEL MONITOREO DIPLOMÁTICO ===", flush=True)

if __name__ == "__main__":
    main()
