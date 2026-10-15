import json, os, re
from typing import Optional
from dotenv import load_dotenv
load_dotenv()

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

def _fallback(planner, budget, currency, preferences, location, details):
    """Transparent demo recommendations. These are examples, not live prices or verified listings."""
    symbol = "₹" if currency.upper() == "INR" else f"{currency.upper()} "
    if planner == "home":
        categories = [
            ("Lighting", .15, "Compare LED ceiling lights and warm bedside lamps"),
            ("Fans / ventilation", .20, "Prioritize energy rating, room size, and warranty"),
            ("Furniture", .40, "Measure the room before choosing compact, multi-use furniture"),
            ("Decor & essentials", .15, "Use textiles, plants, and storage to finish the room"),
            ("Contingency", .10, "Keep this amount unspent for delivery or installation"),
        ]
        note = "Home budget split"
    elif planner == "party":
        categories = [
            ("Food & drinks", .40, "Compare per-person menus and delivery / service charges"),
            ("Venue", .20, "Check capacity, timing, and any cleaning deposit"),
            ("Decor", .15, "Reuse a theme backdrop and simple table decorations"),
            ("Entertainment", .10, "Choose a playlist or a small activity within budget"),
            ("Logistics & contingency", .15, "Reserve funds for transport, taxes, and last-minute needs"),
        ]
        note = "Party budget split"
    else:
        categories = [
            ("Main jewelry piece", .45, "Compare material, dimensions, seller reviews, and return policy"),
            ("Matching earrings", .20, "Match the metal tone and occasion"),
            ("Optional bracelet / ring", .15, "Add only if the main piece is within budget"),
            ("Care / packaging", .05, "Check whether a storage pouch or gift box is included"),
            ("Reserve", .15, "Keep a buffer; verify authenticity and total checkout price"),
        ]
        note = "Jewelry budget split"
    allocations = [
        {"category": name, "amount": round(budget * share, 2),
         "formatted_amount": f"{symbol}{budget * share:,.2f}",
         "share_percent": round(share * 100), "suggestion": suggestion}
        for name, share, suggestion in categories
    ]
    return {
        "planner": planner, "budget": budget, "currency": currency.upper(),
        "summary": f"{note} for a total budget of {symbol}{budget:,.2f}.",
        "allocations": allocations,
        "recommendations": [
            {"title": "Compare before buying", "platform": "Amazon / Flipkart / IKEA (examples)",
             "estimated_price": None, "reason": "Search the category and compare current price, delivery, warranty, and returns.",
             "search_query": preferences or f"{planner} budget ideas", "url": None}
        ],
        "tips": [
            "These are planning estimates, not live product listings or confirmed prices.",
            "Check current prices, delivery charges, taxes, seller reputation, and return terms before purchasing.",
            f"Location context: {location}. Preferences: {preferences or 'not specified'}."
        ],
        "image_observation": "Image analysis is available when a compatible Gemini API key/model is configured." if planner == "jewelry" else None,
        "source": "demo_fallback"
    }

def _extract_json(text):
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.I)
    text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start >= 0 and end > start:
            return json.loads(text[start:end+1])
        raise

async def generate_recommendations(planner: str, budget: float, currency: str,
    preferences: str, location: str, details: dict,
    image_bytes: Optional[bytes] = None, image_mime: Optional[str] = None):
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        return _fallback(planner, budget, currency, preferences, location, details)
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=api_key)
        context = {
            "planner": planner, "budget": budget, "currency": currency,
            "preferences": preferences, "location": location, "details": details,
        }
        prompt = f"""
You are PocketSmart AI, a cautious budget planner. Use this user request:
{json.dumps(context, ensure_ascii=False)}
The budget is a hard maximum. Create an allocation whose category amounts add up to no more than the total budget.
Give practical recommendations and search terms for relevant platforms such as Amazon, Flipkart, IKEA, Swiggy, Zomato, or OYO only where relevant.
Do not claim to have queried live catalogs or verified current prices. If you provide estimates, label them as estimates and advise users to verify prices.
For jewelry image input, describe visible colors/style cautiously; do not identify a person.
Return ONLY valid JSON with this schema:
{{
 "planner": "{planner}", "budget": {budget}, "currency": "{currency}",
 "summary": "short summary",
 "allocations": [{{"category":"", "amount":0, "share_percent":0, "suggestion":""}}],
 "recommendations": [{{"title":"", "platform":"", "estimated_price":null, "reason":"", "search_query":"", "url":null}}],
 "tips": ["..."],
 "image_observation": null
}}
Use 3-6 allocations. Amounts must be numeric and sum to <= {budget}. Never fabricate direct product URLs. Keep recommendations suitable for the stated location and preferences.
"""
        contents = [prompt]
        if image_bytes and image_mime:
            contents.append(types.Part.from_bytes(data=image_bytes, mime_type=image_mime))
        response = client.models.generate_content(model=MODEL_NAME, contents=contents)
        data = _extract_json(response.text or "")
        data["source"] = "gemini"
        # Normalize totals if the model overspends.
        allocations = data.get("allocations", [])
        total = sum(float(a.get("amount", 0) or 0) for a in allocations)
        if total > budget and total > 0:
            factor = budget / total
            for a in allocations:
                a["amount"] = round(float(a.get("amount", 0) or 0) * factor, 2)
            data.setdefault("tips", []).append("Allocation was scaled to stay within your budget.")
        data.setdefault("recommendations", [])
        data.setdefault("tips", [])
        data.setdefault("image_observation", None)
        data["budget"], data["currency"], data["planner"] = budget, currency.upper(), planner
        return data
    except Exception:
        # The app remains usable when the model/API is unavailable; avoid exposing secrets or stack traces.
        result = _fallback(planner, budget, currency, preferences, location, details)
        result["source"] = "demo_fallback"
        result["tips"].insert(0, "Gemini could not be reached, so demo recommendations are shown. Check the API key, model name, network, and terminal logs.")
        return result
