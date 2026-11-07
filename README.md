# PokéRadar UK — GitHub live-stock tracker

This is a GitHub Pages dashboard plus a scheduled Python checker. The dashboard refreshes its published JSON every minute; GitHub Actions attempts retailer checks every 5 minutes.

## What it does
- Tracks any Pokémon TCG product you add, with no buying-budget filter.
- Checks configured public retailer product pages for price and stock.
- Displays confirmed in-stock, out-of-stock, or unknown (never treats a failed check as out of stock).
- Displays retailer restock dates only when supplied in the watchlist. A future restock date cannot be reliably predicted from a normal product page.
- Keeps product-specific retailer links and check timestamps.

## Important limitations
This is a working framework, not a pre-populated feed of every Pokémon product at every UK retailer. Retailers do not provide one universal UK Pokémon stock API. Each product/retailer combination needs a direct product URL and working CSS selectors, or a retailer-approved API/feed integration. Some sites use JavaScript, bot protection, or terms that prohibit automated checking; those pages will show unknown until a permitted integration is configured. Do not bypass CAPTCHAs, queues, logins, rate limits or access controls.

GitHub scheduled jobs are not guaranteed to start at the exact minute. The five-minute schedule is a best-effort cadence, not a real-time guarantee. GitHub Pages is static; the Python workflow performs the checks and publishes the latest data.

## Add products
Edit `watchlist.json` in the GitHub repository. Add a product object under `products`, and one retailer object per listing. Example:

```json
{
  "name": "Scarlet & Violet — Example Booster Bundle",
  "set": "Scarlet & Violet",
  "type": "Booster Bundle",
  "official_rrp_gbp": 24.99,
  "rrp_source_url": "https://official-source.example/rrp",
  "retailers": [
    {
      "retailer": "Example UK retailer",
      "url": "https://retailer.example/product",
      "availability_selector": ".stock-message",
      "price_selector": ".product-price",
      "in_stock_text": ["in stock", "available"],
      "out_of_stock_text": ["out of stock", "sold out"],
      "restock_status": "unknown",
      "restock_date": null,
      "note": ""
    }
  ]
}
```

Selectors can be found by inspecting the public product page HTML. If the site renders its price/stock only in JavaScript, this simple checker may not see it; use an approved API/feed or a permitted integration instead.

## Restock dates
- `restock_status`: use `confirmed`, `estimated`, or `unknown`.
- `restock_date`: ISO date/time or a retailer's stated wording.
- Only mark a date `confirmed` when the retailer itself has announced it.
- Use `estimated` only when there is evidence, and explain that evidence in `note`. Never present estimates as guaranteed.

## Publish on GitHub
1. Create a repository, e.g. `pokemon-live-tracker`.
2. Upload the contents of this folder to the repository root (including hidden `.github` folder).
3. In **Settings → Pages**, choose **Deploy from a branch**, `main`, and `/ (root)`.
4. In **Settings → Actions → General**, allow GitHub Actions to read and write repository contents.
5. Open **Actions → Check Pokémon stock → Run workflow** once to test.
6. Add actual product URLs and selectors to `watchlist.json`. The sample is deliberately not a real product.
7. Keep the repository public if using the free GitHub Pages offering.

## Data freshness
The workflow is scheduled every five minutes. GitHub may delay scheduled jobs, especially during busy periods. The dashboard polls the JSON file every 60 seconds, but it can only display the latest successful checker run.
