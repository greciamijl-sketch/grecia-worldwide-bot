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
    {"region": "EE.UU.", "role": "Secretario de Estado", "author": "SecBlinken (@SecBlinken)", "url": "https://nitter.privacydev.net/SecBlinken/rss"},
    {"region": "CANADÁ", "role": "Primer Ministro", "author": "Justin Trudeau (@JustinTrudeau)", "url": "https://nitter.privacydev.net/JustinTrudeau/rss"},
    {"region": "CANADÁ", "role": "Canciller", "author": "Mélanie Joly (@melaniejoly)", "url": "https://nitter.privacydev.net/melaniejoly/rss"},

    # América Latina
    {"region": "ARGENTINA", "role": "Presidente", "author": "Javier Milei (@JMilei)", "url": "https://nitter.privacydev.net/JMilei/rss"},
    {"region": "BRASIL", "role": "Presidente", "author": "Lula da Silva (@LulaOficial)", "url": "https://nitter.privacydev.net/LulaOficial/rss"},
    {"region": "COLOMBIA", "role": "Presidente", "author": "Abelardo de la Espriella (@DELAESPRIELLAE)", "url": "https://nitter.privacydev.net/DELAESPRIELLAE/rss"},
    {"region": "PERÚ", "role": "Presidenta", "author": "Keiko Fujimori (@KeikoFujimori)", "url": "https://nitter.privacydev.net/KeikoFujimori/rss"},
    {"region": "CHILE", "role": "Presidente", "author": "Gabriel Boric (@GabrielBoric)", "url": "https://nitter.privacydev.net/GabrielBoric/rss"},
    {"region": "EL SALVADOR", "role": "Presidente", "author": "Nayib Bukele (@nayibbukele)", "url": "https://nitter.privacydev.net/nayibbukele/rss"},
    {"region": "GUATEMALA", "role": "Presidente", "author": "Bernardo Arévalo (@BArevalodeLeon)", "url": "https://nitter.privacydev.net/BArevalodeLeon/rss"},

    # Europa y Potencias
    {"region": "ESPAÑA", "role": "Presidente del Gobierno", "author": "Pedro Sánchez (@sanchezcastejon)", "url": "https://nitter.privacydev.net/sanchezcastejon/rss"},
    {"region": "FRANCIA", "role": "Presidente", "author": "Emmanuel Macron (@EmmanuelMacron)", "url": "https://nitter.privacydev.net/EmmanuelMacron/rss"},
    {"region": "ALEMANIA", "role": "Canciller Federal", "author": "Olaf Scholz (@Bundeskanzler)", "url": "https://nitter.privacydev.net/Bundeskanzler/rss"},
    {"region": "REINO UNIDO", "role": "Primer Ministro", "author": "Keir Starmer (@Keir_Starmer)", "url": "https://nitter.privacydev.net/Keir_Starmer/rss"},
    {"region": "UCRANIA", "role": "Presidente", "author": "Volodymyr Zelenskyy (@ZelenskyyUa)", "url": "https://nitter.privacydev.net/ZelenskyyUa/rss"},
    {"region": "INDIA", "role": "Primer Ministro", "author": "Narendra Modi (@narendramodi)", "url": "https://nitter.privacydev.net/narendramodi/rss"},

    # Organismos Multilaterales
    {"region": "ONU", "role": "Secretario General", "author": "António Guterres (@antonioguterres)", "url": "https://nitter.privacydev.net/antonioguterres/rss"},
    {"region": "OEA", "role": "Secretario General", "author": "Luis Almagro (@Almagro_OEA2015)", "url": "https://nitter.privacydev.net/Almagro_OEA2015/rss"}
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
    r"secretar[ií]a\s*de\s*relaciones\s*exteriores|@SRE_mx"
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
    message = (
