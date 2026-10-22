import json
import os
import re
import html
import time
import requests

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
X_AUTH_TOKEN = os.environ.get("X_AUTH_TOKEN")
X_CT0 = os.environ.get("X_CT0")

STATE_FILE = "last_seen_diplomacy.json"

BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"

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
        print(f"Error al enviar a Telegram: {e}")

def get_tweets_by_search(session, handle):
    # Consulta mediante la búsqueda avanzada nativa de X
    endpoint = "https://x.com/i/api/graphql/MJvjTbp00p8U43wGiiM0gw/SearchTimeline"
    
    variables = {
        "rawQuery": f"from:{handle}",
        "count": 5,
        "querySource": "typed_query",
        "product": "Latest"
    }
    features = {
        "responsive_web_graphql_exclude_directive_enabled": True,
        "verified_phone_label_enabled": False,
        "creator_subscriptions_tweet_preview_api_enabled": True,
        "responsive_web_graphql_timeline_navigation_enabled": True,
        "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
        "tweet_awards_web_tipping_enabled": False,
        "responsive_web_twitter_article_tweet_consumption_enabled": True
    }
    params = {
        "variables": json.dumps(variables),
        "features": json.dumps(features)
    }

    res = session.get(endpoint, params=params, timeout=10)
    if res.status_code != 200:
        return None, f"Error {res.status_code}"

    tweets = []
    try:
        data = res.json()
        instructions = data["data"]["search_by_raw_query"]["search_timeline"]["timeline"]["instructions"]
        for inst in instructions:
            if inst.get("type") == "TimelineAddEntries":
                for entry in inst.get("entries", []):
                    content = entry.get("content", {})
                    if content.get("entryType") == "TimelineTimelineItem":
                        result = content.get("itemContent", {}).get("tweet_results", {}).get("result", {})
                        legacy = result.get("legacy") or result.get("tweet", {}).get("legacy")
                        if legacy:
                            tweets.append({
                                "id": str(legacy.get("id_str")),
                                "text": legacy.get("full_text", "")
                            })
    except Exception as e:
        return None, f"Error parsing: {e}"

    return tweets, None

def main():
    state = load_state()
    is_initial_run = (len(state) == 0)

    print(f"=== INICIANDO MONITOREO DIPLOMÁTICO: {len(SOURCES)} FUENTES ===")
    
    session = requests.Session()
    session.headers.update({
        "authorization": f"Bearer {BEARER_TOKEN}",
        "x-csrf-token": X_CT0,
        "x-twitter-active-user": "yes",
        "x-twitter-auth-type": "OAuth2Session",
        "x-twitter-client-language": "es",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    })
    session.cookies.set("auth_token", X_AUTH_TOKEN, domain=".x.com")
    session.cookies.set("ct0", X_CT0, domain=".x.com")

    for source in SOURCES:
        region = source["region"]
        role = source["role"]
        author = source["author"]
        handle = source["handle"]
        last_id = state.get(handle)

        tweets, err = get_tweets_by_search(session, handle)
        if err:
            print(f"❌ Error al consultar @{handle}: {err}")
            time.sleep(1)
            continue

        print(f"✅ @{handle}: {len(tweets)} tuits obtenidos.")

        if not tweets:
            time.sleep(1)
            continue

        if is_initial_run or last_id is None:
            state[handle] = tweets[0]["id"]
            time.sleep(1)
            continue

        new_tweets = []
        for t in tweets:
            if t["id"] == last_id:
                break
            new_tweets.append(t)

        for t in reversed(new_tweets):
            full_text = clean_html(t["text"])
            if KEYWORDS_REGEX.search(full_text):
                print(f"🚨 Coincidencia encontrada en @{handle}: {full_text[:60]}")
                t_link = f"https://x.com/{handle}/status/{t['id']}"
                preview = full_text[:400] + ("..." if len(full_text) > 400 else "")
                send_telegram(region, role, author, preview, t_link)

        if new_tweets:
            state[handle] = new_tweets[0]["id"]

        time.sleep(1)

    save_state(state)
    print("=== FIN DEL MONITOREO DIPLOMÁTICO ===")

if __name__ == "__main__":
    main()
