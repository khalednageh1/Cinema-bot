import requests, json, os, sys
from urllib.parse import urljoin, urldefrag
from bs4 import BeautifulSoup

URL = "https://egy.voxcinemas.com/movies/whatson"
TOKEN = os.environ["TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
FILE = "seen_vox.json"  # ملف جديد عشان ميتلخبطش مع seen.json بتاع سينس

html = requests.get(URL, timeout=20, headers={"User-Agent": "Mozilla/5.0"}).text
soup = BeautifulSoup(html, "html.parser")

movies = {}
# اسم الفيلم موجود في العنوان (h3) جوه لينك صفحة الفيلم
for a in soup.select('h3 a[href*="/movies/"]'):
    href, _ = urldefrag(urljoin(URL, a["href"]))  # نشيل #showtimes
    name = a.get_text(strip=True)
    if name and not href.rstrip("/").endswith(("/whatson", "/comingsoon")):
        movies[href] = name

print("لقيت", len(movies), "فيلم")

if not movies:
    sys.exit("مفيش أفلام اتقرأت")

# أول مرة تشتغل: بنحفظ الأفلام من غير ما نبعت إشعارات
seen = set(json.load(open(FILE, encoding="utf-8"))) if os.path.exists(FILE) else None

if seen is not None:
    for href in movies.keys() - seen:
        requests.get(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            params={
                "chat_id": CHAT_ID,
                "text": f"فيلم جديد نزل: {movies[href]}\n{href}",
            },
            timeout=20,
        )

json.dump(
    sorted((seen or set()) | set(movies)),
    open(FILE, "w", encoding="utf-8"),
    ensure_ascii=False,
)
