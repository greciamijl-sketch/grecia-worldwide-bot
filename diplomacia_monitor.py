import json
import os
import re
import html
import feedparser
import requests

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
STATE_FILE = "last_seen_diplomacy.json"

# ================= DIRECTORIO DIPLOMÁTICO GLOBAL =================
SOURCES = [
    # América del Norte
    {"region": "EE.UU.", "role": "Presidente", "author": "POTUS (@POTUS)", "url": "https://nitter.privacydev.net/POTUS/rss"},
    {"region": "EE.UU.", "role": "Casa Blanca", "author": "White House (@WhiteHouse)", "url": "https://nitter.privacydev.net/WhiteHouse/rss"},
    {"region": "EE.UU.", "role": "Secretario de Estado", "author": "Marco Rubio (@marcorubio)", "url": "https://nitter.privacydev.net/marcorubio/rss"},
    {"region": "CANADÁ", "role": "Primer Ministro", "author": "Mark Carney (@MarkJCarney)", "url": "https://nitter.privacydev.net/MarkJCarney/rss"},
    {"region": "CANADÁ", "role": "Canciller", "author": "Anita Anand (@AnitaAnandMP)", "url": "https://nitter.privacydev.net/AnitaAnandMP/rss"},

    # América Latina y el Caribe
    {"region": "ARGENTINA", "role": "Presidente", "author": "Javier Milei (@JMilei)", "url": "https://nitter.privacydev.net/JMilei/rss"},
    {"region": "BRASIL", "role": "Presidente", "author": "Lula da Silva (@LulaOficial)", "url": "https://nitter.privacydev.net/LulaOficial/rss"},
    {"region": "COLOMBIA", "role": "Presidente", "author": "Abelardo de la Espriella (@DELAESPRIELLAE)", "url": "https://nitter.privacydev.net/DELAESPRIELLAE/rss"},
    {"region": "PERÚ", "role": "Presidenta", "author": "Keiko Fujimori (@KeikoFujimori)", "url": "https://nitter.privacydev.net/KeikoFujimori/rss"},
    {"region": "CHILE", "role": "Presidente", "author": "José Antonio Kast (@joseantoniokast)", "url": "https://nitter.privacydev.net/joseantoniokast/rss"},
    {"region": "BOLIVIA", "role": "Presidente", "author": "Rodrigo Paz (@Rodrigo_PazP)", "url": "https://nitter.privacydev.net/Rodrigo_PazP/rss"},
    {"region": "ECUADOR", "role": "Presidente", "author": "Daniel Noboa (@DanielNoboaOk)", "url": "https://nitter.privacydev.net/DanielNoboaOk/rss"},
    {"region": "URUGUAY", "role": "Presidente", "author": "Yamandú Orsi (@OrsiYamandu)", "url": "https://nitter.privacydev.net/OrsiYamandu/rss"},
    {"region": "PANAMÁ", "role": "Presidente", "author": "José Raúl Mulino (@JoseRaulMulino)", "url": "https://nitter.privacydev.net/JoseRaulMulino/rss"},
    {"region": "PARAGUAY", "role": "Presidente", "author": "Santiago Peña (@SantiPenap)", "url": "https://nitter.privacydev.net/SantiPenap/rss"},
    {"region": "REP. DOMINICANA", "role": "Presidente", "author": "Luis Abinader (@luisabinader)", "url": "https://nitter.privacydev.net/luisabinader/rss"},
    {"region": "COSTA RICA", "role": "Presidenta", "author": "Laura Fernández (@laurapresi2026)", "url": "https://nitter.privacydev.net/laurapresi2026/rss"},
    {"region": "HONDURAS", "role": "Presidente", "author": "Nasry Asfura (@titoasfura)", "url": "https://nitter.privacydev.net/titoasfura/rss"},
    {"region": "EL SALVADOR", "role": "Presidente", "author": "Nayib Bukele (@nayibbukele)", "url": "https://nitter.privacydev.net/nayibbukele/rss"},
    {"region": "GUATEMALA", "role": "Presidente", "author": "Bernardo Arévalo (@BArevalodeLeon)", "url": "https://nitter.privacydev.net/BArevalodeLeon/rss"},

    # Europa
    {"region": "ITALIA", "role": "Presidenta del Consejo", "author": "Giorgia Meloni (@GiorgiaMeloni)", "url": "https://nitter.privacydev.net/GiorgiaMeloni/rss"},
    {"region": "UNIÓN EUROPEA", "role": "Presidenta Comisión", "author": "Ursula von der Leyen (@vonderleyen)", "url": "https://nitter.privacydev.net/vonderleyen/rss"},
    {"region": "ESPAÑA", "role": "Presidente del Gobierno", "author": "Pedro Sánchez (@sanchezcastejon)", "url": "https://nitter.privacydev.net/sanchezcastejon/rss"},
    {"region": "FRANCIA", "role": "Presidente", "author": "Emmanuel Macron (@EmmanuelMacron)", "url": "https://nitter.privacydev.net/EmmanuelMacron/rss"},
    {"region": "ALEMANIA", "role": "Canciller Federal", "author": "Friedrich Merz (@_FriedrichMerz)", "url": "https://nitter.privacydev.net/_FriedrichMerz/rss"},
    {"region": "REINO UNIDO", "role": "Primer Ministro", "author": "Andy Burnham (@AndyBurnhamGM)", "url": "https://nitter.privacydev.net/AndyBurnhamGM/rss"},
    {"region": "UCRANIA", "role": "Presidente", "author": "Volodymyr Zelenskyy (@ZelenskyyUa)", "url": "https://nitter.privacydev.net/ZelenskyyUa/rss"},
    {"region": "RUSIA", "role": "Presidencia", "author": "Kremlin (@KremlinRussia_E)", "url": "https://nitter.privacydev.net/KremlinRussia_E/rss"},
    {"region": "RUSIA", "role": "Cancillería en Español", "author": "Cancillería Rusia (@mae_rusia)", "url": "https://nitter.privacydev.net/mae_rusia/rss"},

    # Asia y Potencias
    {"region": "CHINA", "role": "Cancillería / Portavocía", "author": "MFA China (@MFA_China)", "url": "https://nitter.privacydev.net/MFA_China/rss"},
    {"region": "JAPÓN", "role": "Primera Ministra", "author": "Sanae Takaichi (@takaichi_sanae)", "url": "https://nitter.privacydev.net/takaichi_sanae/rss"},
    {"region": "COREA DEL SUR", "role": "Presidente", "author": "Lee Jae-myung (@Jaemyung_Lee)", "url": "https://nitter.privacydev.net/Jaemyung_Lee/rss"},
    {"region": "INDIA", "role": "Primer Ministro", "author": "Narendra Modi (@narendramodi)", "url": "https://nitter.privacydev.net/narendramodi/rss"},

    # Organismos Multilaterales
    {"region": "ONU", "role": "Secretario General", "author": "António Guterres (@antonioguterres)", "url": "https://nitter.privacydev.net/antonioguterres/rss"},
    {"region": "OEA", "role": "Secretario General", "author": "Albert Ramdin (@AlbertRamdin)", "url": "https://nitter.privacydev.net/AlbertRamdin/rss"},

    # Embajadas Extranjeras en México
    {"region": "EMBAJADA EE.UU. EN MÉXICO", "role": "Misión Diplomática", "author": "Embajada EE.UU. en México (@USEmbassyMEX)", "url": "https://nitter.privacydev.net/USEmbassyMEX/rss"},
    {"region": "EMBAJADA CANADÁ EN MÉXICO", "role": "Misión Diplomática", "author": "Canadá en México (@EmbCanMexico)", "url": "https://nitter.privacydev.net/EmbCanMexico/rss"},
    {"region": "EMBAJADA ESPAÑA EN MÉXICO", "role": "Misión Diplomática", "author": "Embajada España en México (@EmbEspMex)", "url": "https://nitter.privacydev.net/EmbEspMex/rss"},
    {"region": "EMBAJADA FRANCIA EN MÉXICO", "role": "Misión Diplomática", "author": "Francia en México (@FranciaenMexico)", "url": "https://nitter.privacydev.net/FranciaenMexico/rss"},
    {"region": "EMBAJADA ALEMANIA EN MÉXICO", "role": "Misión Diplomática", "author": "Alemania en México (@AlemaniaenMex)", "url": "https://nitter.privacydev.net/AlemaniaenMex/rss"},
    {"region": "EMBAJADA REINO UNIDO EN MÉXICO", "role": "Misión Diplomática", "author": "UK in Mexico (@UKinMexico)", "url": "https://nitter.privacydev.net/UKinMexico/rss"},
    {"region": "DELEGACIÓN UE EN MÉXICO", "role": "Misión Diplomática", "author": "Unión Europea en México (@UEenMexico)", "url": "https://nitter.privacydev.net/UEenMexico/rss"},
    {"region": "EMBAJADA CHINA EN MÉXICO", "role": "Misión Diplomática", "author": "Embajada de China en México (@EmbChinaMex)", "url": "https://nitter.privacydev.net/EmbChinaMex/rss"},
    {"region": "EMBAJADA RUSIA EN MÉXICO", "role": "Misión Diplomática", "author": "Embajada de Rusia en México (@EmbRusiaMexico)", "url": "https://nitter.privacydev.net/EmbRusiaMexico/rss"}
]

# ================= FILTRO DIPLOMÁTICO MULTILINGÜE =================
KEYWORDS_REGEX = re.compile(
    r"\b("
    # México y gentilicios (ES / EN / FR)
    r"m[eé]xic\w*|mexican\w*|"
    # Presidencia de México
    r"claudia\s*sheinbaum|sheinbaum|"
    # Canciller Roberto Velasco y referencias diplomáticas
    r"roberto\s*velasco|velasco\s*[aá]lvarez|@r_velascoa|"
    r"canciller\s*mexican\w*|canciller[ií]a\s*mexican\w*|"
    r"mexican\s*foreign\s*minister|foreign\s*secretary\s*of\s*mexico|"
    r"secretar[ií]a\s*de\s*relaciones\s*exteriores|@SRE_mx|"
    # Cárteles y crimen organizado
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
    message = f"""🌐 <b>[GreciaWorldwide - {region}]</b>
🏛 <b>Cargo:</b> {role}
👤 <b>Emisor:</b> {author}

{safe_text}

🔗 <a href="{link}">Ver declaración original</a>"""

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
        print(f"Error al enviar a Telegram: {e}")

def main():
    state = load_state()
    is_initial_run = (len(state) == 0)

    for source in SOURCES:
        region = source["region"]
        role = source["role"]
        name = source["author"]
        url = source["url"]
        last_id = state.get(name)

        try:
            feed = feedparser.parse(url, request_headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        except Exception:
            continue

        if not feed.entries:
            continue

        if is_initial_run or last_id is None:
            state[name] = feed.entries[0].get("id", feed.entries[0].link)
            continue

        new_entries = []
        for entry in feed.entries:
            entry_id = entry.get("id", entry.link)
            if entry_id == last_id:
                break
            new_entries.append(entry)

        for entry in reversed(new_entries):
            raw_title = entry.get("title", "")
            raw_summary = entry.get("summary", "")
            full_text = clean_html(f"{raw_title} {raw_summary}")

            if KEYWORDS_REGEX.search(full_text):
                preview = full_text[:400] + ("..." if len(full_text) > 400 else "")
                send_telegram(region, role, name, preview, entry.link)

        if new_entries:
            state[name] = new_entries[0].get("id", new_entries[0].link)

    save_state(state)

if __name__ == "__main__":
    main()
