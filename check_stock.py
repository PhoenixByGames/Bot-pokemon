import json, re, os
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent
WATCHLIST = json.loads((ROOT / "watchlist.json").read_text(encoding="utf-8"))
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; PokeRadarUK/1.0; stock-check)"}

def parse_price(text):
    if not text: return None
    cleaned = text.replace(",", "")
    match = re.search(r"(?:£|GBP\s*)(\d+(?:\.\d{1,2})?)", cleaned, re.I)
    if not match: return None
    try: return round(float(match.group(1)), 2)
    except ValueError: return None

def check_listing(product, retailer):
    now = datetime.now(timezone.utc).isoformat()
    result = {
        "retailer": retailer.get("retailer", "Retailer"),
        "url": retailer.get("url", ""),
        "rrp": product.get("official_rrp_gbp"),
        "price": None,
        "status": "unknown",
        "checked_at": now,
        "restock_status": retailer.get("restock_status", "unknown"),
        "restock_date": retailer.get("restock_date"),
        "note": retailer.get("note", "")
    }
    url = retailer.get("url", "")
    # Only public HTTP(S) product pages; no login, queue, CAPTCHA or access-control bypass.
    if urlparse(url).scheme not in ("http", "https") or not urlparse(url).netloc:
        result["note"] = "Invalid product URL; update watchlist.json."
        return result
    try:
        response = requests.get(url, headers=HEADERS, timeout=18)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        price_el = soup.select_one(retailer.get("price_selector", "")) if retailer.get("price_selector") else None
        stock_el = soup.select_one(retailer.get("availability_selector", "")) if retailer.get("availability_selector") else None
        if price_el:
            result["price"] = parse_price(price_el.get_text(" ", strip=True))
        stock_text = stock_el.get_text(" ", strip=True).lower() if stock_el else ""
        page_text = soup.get_text(" ", strip=True).lower()
        in_words = [x.lower() for x in retailer.get("in_stock_text", [])]
        out_words = [x.lower() for x in retailer.get("out_of_stock_text", [])]
        # Prefer the configured availability element; fall back to whole page only when configured.
        haystack = stock_text if stock_text else page_text
        if any(x in haystack for x in out_words):
            result["status"] = "out_of_stock"
        elif any(x in haystack for x in in_words):
            result["status"] = "in_stock"
        else:
            result["note"] = (result["note"] + " | " if result["note"] else "") + "Could not confidently identify stock status."
    except Exception as exc:
        result["note"] = (result["note"] + " | " if result["note"] else "") + f"Check failed: {type(exc).__name__}"
    return result

products = []
for product in WATCHLIST.get("products", []):
    if not product.get("name") or product["name"].startswith("Add a real"):
        continue
    listings = [check_listing(product, retailer) for retailer in product.get("retailers", [])]
    products.append({
        "name": product["name"],
        "set": product.get("set", ""),
        "type": product.get("type", "Pokémon TCG"),
        "retailers": listings
    })

payload = {"updated_at": datetime.now(timezone.utc).isoformat(), "products": products}
(ROOT / "data" / "live-data.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
print(f"Updated {len(products)} products / {sum(len(p['retailers']) for p in products)} retailer listings.")
