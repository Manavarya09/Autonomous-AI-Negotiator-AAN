"""Intent parsing engine for incoming seller messages."""

import logging
import re
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


class Intent(str, Enum):
    ACCEPT = "accept"
    REJECT = "reject"
    COUNTER = "counter"
    INFORMATION_REQUEST = "information_request"
    STALL = "stall"
    UNKNOWN = "unknown"


PRICE_EXTRACTION_PATTERNS = [
    r"(?:AED|د\.إ|Dh?)\s*([\d,]+(?:\.\d{2})?)",
    r"([\d,]+(?:\.\d{2})?)\s*(?:AED|د\.إ)",
    r"(?:price|offer|cost)[:\s]*([\d,]+)",
    r"([\d,]{1,3}(?:,\d{3})*(?:\.\d{2})?)",
]

ACCEPT_KEYWORDS = [
    "ok deal", "deal", "agreed", "accepted", "take it", "yala", "let's go",
    "confirmed", "sold", "it is yours", "come take", "pick up",
]

REJECT_KEYWORDS = [
    "no", "not selling", "won't", "can't", "sorry", "already sold",
    "reserved", "too low", "not interested", "good luck",
    "other buyer", "someone else", "passed",
]

STALL_KEYWORDS = [
    "let me think", "will get back", "consider", "maybe", "not sure yet",
    "still deciding", "talk to wife", "talk to partner", "ask mom",
    "need time", "tomorrow", "later", "next week",
]

INFO_REQUEST_KEYWORDS = [
    "cash or transfer", "where are you", "can you come", "pickup only",
    "delivery", "shipping", "condition", "working", "k clicks",
    "accessories", "box", "warranty", "receipt",
]


def extract_price(text: str) -> Optional[float]:
    if not text:
        return None

    for pattern in PRICE_EXTRACTION_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                price_str = match.group(1).replace(",", "")
                return float(price_str)
            except (ValueError, IndexError):
                continue

    numbers = re.findall(r"[\d,]+(?:\.\d{2})?", text)
    for num_str in numbers:
        try:
            num = float(num_str.replace(",", ""))
            if 10 < num < 100000:
                return num
        except ValueError:
            continue

    return None


def classify_intent(text: str) -> Intent:
    if not text:
        return Intent.UNKNOWN

    text_lower = text.lower()

    if any(kw in text_lower for kw in ACCEPT_KEYWORDS):
        return Intent.ACCEPT

    if any(kw in text_lower for kw in REJECT_KEYWORDS):
        return Intent.REJECT

    if any(kw in text_lower for kw in STALL_KEYWORDS):
        return Intent.STALL

    if any(kw in text_lower for kw in INFO_REQUEST_KEYWORDS):
        return Intent.INFORMATION_REQUEST

    price = extract_price(text)
    if price:
        return Intent.COUNTER

    return Intent.UNKNOWN


async def parse_message(
    text: str,
    conversation_context: str = "",
) -> dict:
    intent = classify_intent(text)
    price = extract_price(text)

    return {
        "raw_text": text,
        "intent": intent.value,
        "extracted_price": price,
        "confidence": 0.8 if price else 0.5,
    }


async def llm_classify_intent(
    text: str,
    conversation_context: str = "",
) -> dict:
    try:
        from litellm import acompletion

        prompt = f"""Classify this seller message into one of these intents:
- accept: Seller agrees to your offer
- reject: Seller refuses to negotiate or sell
- counter: Seller makes a counter-offer with a price
- information_request: Seller asks for more info before deciding
- stall: Seller is non-committal, needs more time
- unknown: Cannot determine

Message: {text}

Conversation: {conversation_context}

Respond with just the intent name:"""

        response = await acompletion(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=20,
        )

        intent_str = response.choices[0].message.content.strip().lower()

        try:
            intent = Intent(intent_str)
        except ValueError:
            intent = Intent.UNKNOWN

        return {"intent": intent.value, "llm_confidence": 0.9}

    except Exception as e:
        logger.error(f"LLM intent classification failed: {e}")
        return {"intent": Intent.UNKNOWN.value, "llm_confidence": 0.0}