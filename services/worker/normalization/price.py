"""Price extraction from raw strings."""

import re
from typing import Optional

import aiohttp
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    exchangerate_api_key: str = ""


settings = Settings()


PRICE_PATTERNS = [
    r"(?:AED|د\.إ|Dh|Dhs?)\s*([\d,]+(?:\.\d{2})?)",
    r"([\d,]+(?:\.\d{2})?)\s*(?:AED|د\.إ|Dh|Dhs?)",
    r"([\d,]+(?:\.\d{2})?)\s*(?:AED|د\.إ)",
    r"(?:Price|price|Cost|cost|Prix):?\s*[A-Z]?\s*([\d,]+)",
    r"(?:AED|د\.إ)\s*([\d,]+)",
    r"([\d,]{1,3}(?:,\d{3})*(?:\.\d{2})?)",
]

CURRENCY_MAP = {
    "aed": "AED",
    "د.إ": "AED",
    "dh": "AED",
    "dhs": "AED",
    "usd": "USD",
    "$": "USD",
    "eur": "EUR",
    "€": "EUR",
    "gbp": "GBP",
    "£": "GBP",
}


def extract_price(text: str) -> Optional[float]:
    if not text:
        return None

    text = text.strip()

    for pattern in PRICE_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                price_str = match.group(1).replace(",", "")
                price = float(price_str)
                if price > 0 and price < 1000000:
                    return price
            except (ValueError, IndexError):
                continue

    money_match = re.findall(r"[\d,]+(?:\.\d{2})?", text)
    for match_str in money_match:
        try:
            price = float(match_str.replace(",", ""))
            if 1 < price < 100000:
                return price
        except ValueError:
            continue

    return None


def extract_currency(text: str) -> Optional[str]:
    if not text:
        return None

    text_lower = text.lower()

    for keyword, currency in CURRENCY_MAP.items():
        if keyword in text_lower:
            return currency

    return "AED"


async def convert_currency(
    amount: float,
    from_currency: str,
    to_currency: str = "AED",
) -> float:
    if from_currency == to_currency:
        return amount

    if not settings.exchangerate_api_key:
        return amount

    url = f"https://v6.exchangerate-api.com/v6/{settings.exchangerate_api_key}/latest/{from_currency}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    rates = data.get("conversion_rates", {})
                    rate = rates.get(to_currency, 1.0)
                    return round(amount * rate, 2)
    except Exception:
        pass

    return amount


def normalize_price(price_raw: Optional[str]) -> tuple[Optional[float], Optional[str]]:
    if not price_raw:
        return None, None

    price = extract_price(price_raw)
    currency = extract_currency(price_raw)

    if price and price > 1000 and currency == "AED":
        pass

    return price, currency