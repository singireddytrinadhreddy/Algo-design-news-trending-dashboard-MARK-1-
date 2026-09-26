import json
import re
from pathlib import Path

MOCK_AI_FILE = Path(__file__).resolve().parent.parent / "mock" / "mock_ai_summaries.json"

INDIAN_LOCATIONS = [
    ("Bengaluru", "Bengaluru, Karnataka"),
    ("Bangalore", "Bengaluru, Karnataka"),
    ("Karnataka", "Karnataka"),
    ("Mysuru", "Mysuru, Karnataka"),
    ("Mumbai", "Mumbai, Maharashtra"),
    ("Bombay", "Mumbai, Maharashtra"),
    ("Pune", "Pune, Maharashtra"),
    ("Nagpur", "Nagpur, Maharashtra"),
    ("Maharashtra", "Maharashtra"),
    ("New Delhi", "New Delhi"),
    ("Delhi", "New Delhi"),
    ("Noida", "Noida, Uttar Pradesh"),
    ("Gurugram", "Gurugram, Haryana"),
    ("Gurgaon", "Gurugram, Haryana"),
    ("Hyderabad", "Hyderabad, Telangana"),
    ("Telangana", "Telangana"),
    ("Chennai", "Chennai, Tamil Nadu"),
    ("Madras", "Chennai, Tamil Nadu"),
    ("Tamil Nadu", "Tamil Nadu"),
    ("Coimbatore", "Coimbatore, Tamil Nadu"),
    ("Kolkata", "Kolkata, West Bengal"),
    ("Calcutta", "Kolkata, West Bengal"),
    ("West Bengal", "West Bengal"),
    ("Ahmedabad", "Ahmedabad, Gujarat"),
    ("Gujarat", "Gujarat"),
    ("Surat", "Surat, Gujarat"),
    ("Vadodara", "Vadodara, Gujarat"),
    ("Kerala", "Kerala"),
    ("Kochi", "Kochi, Kerala"),
    ("Thiruvananthapuram", "Thiruvananthapuram, Kerala"),
    ("Wayanad", "Wayanad, Kerala"),
    ("Kozhikode", "Kozhikode, Kerala"),
    ("Jaipur", "Jaipur, Rajasthan"),
    ("Rajasthan", "Rajasthan"),
    ("Ajmer", "Ajmer, Rajasthan"),
    ("Udaipur", "Udaipur, Rajasthan"),
    ("Jodhpur", "Jodhpur, Rajasthan"),
    ("Lucknow", "Lucknow, Uttar Pradesh"),
    ("Varanasi", "Varanasi, Uttar Pradesh"),
    ("Kanpur", "Kanpur, Uttar Pradesh"),
    ("Agra", "Agra, Uttar Pradesh"),
    ("Ayodhya", "Ayodhya, Uttar Pradesh"),
    ("Uttar Pradesh", "Uttar Pradesh"),
    ("Chandigarh", "Chandigarh"),
    ("Punjab", "Punjab"),
    ("Amritsar", "Amritsar, Punjab"),
    ("Ludhiana", "Ludhiana, Punjab"),
    ("Jalandhar", "Jalandhar, Punjab"),
    ("Patna", "Patna, Bihar"),
    ("Bihar", "Bihar"),
    ("Bhopal", "Bhopal, Madhya Pradesh"),
    ("Indore", "Indore, Madhya Pradesh"),
    ("Madhya Pradesh", "Madhya Pradesh"),
    ("Bhubaneswar", "Bhubaneswar, Odisha"),
    ("Odisha", "Odisha"),
    ("Goa", "Goa"),
    ("Panaji", "Panaji, Goa"),
    ("Assam", "Assam"),
    ("Guwahati", "Guwahati, Assam"),
    ("Kashmir", "Jammu & Kashmir"),
    ("Srinagar", "Srinagar, Jammu & Kashmir"),
    ("Jammu", "Jammu, Jammu & Kashmir"),
    ("Dehradun", "Dehradun, Uttarakhand"),
    ("Uttarakhand", "Uttarakhand"),
    ("Rishikesh", "Rishikesh, Uttarakhand"),
    ("Shimla", "Shimla, Himachal Pradesh"),
    ("Himachal", "Himachal Pradesh"),
    ("Ranchi", "Ranchi, Jharkhand"),
    ("Jharkhand", "Jharkhand"),
    ("Raipur", "Raipur, Chhattisgarh"),
    ("Chhattisgarh", "Chhattisgarh"),
    ("Visakhapatnam", "Visakhapatnam, Andhra Pradesh"),
    ("Vizag", "Visakhapatnam, Andhra Pradesh"),
    ("Vijayawada", "Vijayawada, Andhra Pradesh"),
    ("Andhra Pradesh", "Andhra Pradesh"),
    ("Malabar", "Malabar, Kerala"),
    ("India", "India"),
]

CATEGORY_KEYWORDS = [
    ("Politics", [
        "minister", "bjp", "congress", "election", "vote", "parliament", "lok sabha",
        "rajya sabha", "supreme court", "government", "policy", "modi", "rahul",
        "kejriwal", "chief minister", "cm", "mla", "mp", "bill", "constitution",
        "assembly", "judiciary", "cabinet", "protest", "strike", "rally", "court",
        "verdict", "aatmanirbhar", "sanatan", "neet"
    ]),
    ("Health", [
        "covid", "virus", "health", "hospital", "doctor", "medicine", "vaccine",
        "cancer", "disease", "aiims", "mental health", "diet", "surgery", "outbreak",
        "medical", "dengue", "nipah", "epidemic", "clinic", "patient", "wellness",
        "fitness", "w.h.o.", "world health organization", "nutrition", "pharma"
    ]),
    ("Sports", [
        "cricket", "match", "tournament", "ipl", "bcci", "virat", "rohit", "dhoni",
        "football", "goal", "player", "athlete", "olympics", "medal", "trophy",
        "championship", "tennis", "badminton", "chess", "stadium", "world cup",
        "league", "wicket", "sixer", "score", "batsman", "bowler", "fifa", "isl"
    ]),
    ("Entertainment", [
        "movie", "film", "trailer", "teaser", "actor", "actress", "bollywood",
        "tollywood", "kollywood", "song", "music", "concert", "box office", "netflix",
        "ott", "cinema", "star", "episode", "season", "album", "comedy", "theatrical",
        "premiere", "shah rukh", "salman", "vijay", "prabhas", "deepika", "oscars"
    ]),
    ("Gaming", [
        "game", "gameplay", "streamer", "streaming", "stream", "twitch", "esports", "gta", "playstation",
        "xbox", "valve", "steam", "nintendo", "discord", "rpg", "fps", "gamer",
        "dota", "counter-strike", "bgmi", "pubg", "roblox", "minecraft"
    ]),
    ("Business", [
        "stock", "market", "sensex", "nifty", "rbi", "sebi", "economy", "bank",
        "startup", "funding", "investor", "earnings", "inflation", "finance",
        "valuation", "acquisition", "rupee", "crypto", "revenue", "fiscal", "gdp",
        "trade", "hdfc", "tcs", "reliance", "adani", "shares", "ipo"
    ]),
    ("Science", [
        "space", "isro", "nasa", "satellite", "rocket", "physics", "quantum",
        "biology", "research", "scientist", "telescope", "climate", "astronomy",
        "chemistry", "laboratory", "mission", "chandrayaan", "gaganyaan", "aditya"
    ]),
    ("Breaking News", [
        "alert", "breaking", "urgent", "accident", "blast", "crash", "disaster",
        "cyclone", "earthquake", "flood", "rescue", "collapse", "emergency", "warning",
        "death", "fire", "casualty", "landslide"
    ]),
    ("Culture", [
        "festival", "diwali", "holi", "eid", "puja", "ganesh", "chaturthi", "heritage",
        "temple", "tradition", "history", "art", "museum", "classical", "culture",
        "ritual", "spiritual", "navratri", "kumbh"
    ]),
    ("Lifestyle", [
        "fashion", "food", "travel", "recipe", "wedding", "tourism", "trend",
        "vlog", "style", "culinary", "destination", "luxury", "beauty", "outfit"
    ]),
    ("Technology", [
        "ai", "software", "code", "app", "python", "developer", "chip", "linux",
        "algorithm", "cybersecurity", "gadget", "cloud", "smartphone", "open source",
        "google", "apple", "microsoft", "meta", "nvidia", "github", "hardware"
    ])
]

def detect_indian_location_heuristic(text: str) -> str | None:
    """Detect if title or description mentions a genuine Indian city, state, or key institution."""
    if not text:
        return None
    for keyword, loc_label in INDIAN_LOCATIONS:
        if re.search(rf"\b{re.escape(keyword)}\b", text, re.IGNORECASE):
            return loc_label
    return None

def classify_category_heuristic(text: str, default_source: str = "") -> str:
    """Classify text into one of the 12 taxonomy categories based on keywords."""
    if not text:
        text = ""
    lower_text = text.lower()

    for cat_name, keywords in CATEGORY_KEYWORDS:
        for kw in keywords:
            if re.search(rf"\b{re.escape(kw)}\b", lower_text):
                return cat_name

    # Source-based defaults if no keyword match
    source_lower = default_source.lower()
    if "twitch" in source_lower:
        return "Gaming"
    if "youtube" in source_lower:
        return "Entertainment"
    if "google_trends" in source_lower:
        return "Breaking News"
    if any(s in source_lower for s in ["hackernews", "devto", "lemmy"]):
        return "Technology"
    if any(s in source_lower for s in ["twitter", "facebook", "reddit", "instagram"]):
        return "Culture"

    return "Other"

def get_mock_ai_summary(platform_slug: str, title: str = "", description: str = "") -> tuple[str, str, str | None, bool]:
    """
    Return heuristic/template summary, category tag, location_india, and is_platform_trend.
    Returns: (summary_text, category_name, location_india, is_platform_trend)
    """
    full_text = f"{title} {description}".strip()
    loc = detect_indian_location_heuristic(full_text)
    cat = classify_category_heuristic(full_text, default_source=platform_slug)

    summary = f"Trending on {platform_slug.replace('_', ' ').title()} with active community engagement and viral discussions across India."
    if loc:
        summary = f"Major trending story centered in {loc} sparking widespread conversational reach and public discussion."

    return (summary, cat, loc, True)
