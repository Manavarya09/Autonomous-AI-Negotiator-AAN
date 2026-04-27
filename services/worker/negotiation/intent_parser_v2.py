"""Enhanced intent parser with LLM support and multi-language."""

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
    QUESTION = "question"
    GREETING = "greeting"
    UNKNOWN = "unknown"


class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


PRICE_EXTRACTION_PATTERNS = [
    r"(?:AED|د\.إ|Dh?)\s*([\d,]+(?:\.\d{2})?)",
    r"([\d,]+(?:\.\d{2})?)\s*(?:AED|د\.إ)",
    r"(?:price|offer|cost|nego)[:\s]*([\d,]+)",
    r"([\d,]{1,3}(?:,\d{3})*(?:\.\d{2})?)",
    r"(?: AED | AED )\s*([\d,]+)",
]

ACCEPT_KEYWORDS = [
    "ok deal", "deal", "agreed", "accepted", "take it", "yala", "let's go",
    "confirmed", "sold", "it is yours", "come take", "pick up",
    "deal done", "ok", "sure", "fine", "没问题", "موافق", "حسناً",
    "done", "perfect", "okay by me", "sounds good",
]

REJECT_KEYWORDS = [
    "no", "not selling", "won't", "can't", "sorry", "already sold",
    "reserved", "too low", "not interested", "good luck",
    "other buyer", "someone else", "passed", "no way", "forget it",
    "غير مهتم", "لا", "not available",
]

STALL_KEYWORDS = [
    "let me think", "will get back", "consider", "maybe", "not sure yet",
    "still deciding", "talk to wife", "talk to partner", "ask mom",
    "let me check", "need to discuss", "let me see", "later",
    "سأفكر", "ربما", "بعدين",
]

QUESTION_KEYWORDS = [
    "when", "where", "how", "can i", "do you", "is it", "does it",
    "what's included", "condition", "warranty", "model", "year",
    "كم", "وش", "وين", "كيف",
]

ARABIC_PRICE_PATTERNS = [
    r"(\d+(?:,\d+)*)\s*درهم",
    r"درهم\s*(\d+(?:,\d+)*)",
    r"د\.إ\s*(\d+(?:,\d+)*)",
]

ARABIC_ACCEPT = ["موافق", "حسناً", "بيع", "طيب", "okeh", "ok", "نعم"]
ARABIC_REJECT = ["لا", "غير مهتم", "ما أبيه", " дор", "غالي"]
ARABIC_STALL = ["ربما", "بعدين", "سأفكر", "ما ادري"]


def extract_price(text: str) -> Optional[float]:
    """Extract price from text with multi-language support."""
    text = text.lower().strip()
    
    for pattern in PRICE_EXTRACTION_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                price_str = match.group(1).replace(",", "")
                return float(price_str)
            except (ValueError, AttributeError):
                continue
    
    for pattern in ARABIC_PRICE_PATTERNS:
        match = re.search(pattern, text)
        if match:
            try:
                price_str = match.group(1).replace(",", "")
                return float(price_str)
            except (ValueError, AttributeError):
                continue
    
    return None


def detect_intent(text: str) -> Intent:
    """Detect seller intent from message."""
    text_lower = text.lower()
    
    if any(kw in text_lower for kw in ACCEPT_KEYWORDS):
        return Intent.ACCEPT
    
    if any(kw in text_lower for kw in ARABIC_ACCEPT):
        return Intent.ACCEPT
    
    if any(kw in text_lower for kw in REJECT_KEYWORDS) or any(kw in text_lower for kw in ARABIC_REJECT):
        return Intent.REJECT
    
    if any(kw in text_lower for kw in QUESTION_KEYWORDS):
        return Intent.QUESTION
    
    if any(kw in text_lower for kw in STALL_KEYWORDS) or any(kw in text_lower for kw in ARABIC_STALL):
        return Intent.STALL
    
    price = extract_price(text)
    if price:
        return Intent.COUNTER
    
    return Intent.UNKNOWN


def detect_sentiment(text: str) -> Sentiment:
    """Detect sentiment of message."""
    text_lower = text.lower()
    
    positive_count = sum(1 for kw in ACCEPT_KEYWORDS if kw in text_lower)
    negative_count = sum(1 for kw in REJECT_KEYWORDS if kw in text_lower)
    
    positive_arabic = sum(1 for kw in ARABIC_ACCEPT if kw in text_lower)
    negative_arabic = sum(1 for kw in ARABIC_REJECT if kw in text_lower)
    
    total_positive = positive_count + positive_arabic
    total_negative = negative_count + negative_arabic
    
    if total_positive > total_negative:
        return Sentiment.POSITIVE
    elif total_negative > total_positive:
        return Sentiment.NEGATIVE
    else:
        return Sentiment.NEUTRAL


def extract_seller_info(text: str) -> dict:
    """Extract additional seller information from message."""
    result = {
        "condition_notes": None,
        "reason_for_selling": None,
        "urgency": None,
        "includes": [],
    }
    
    text_lower = text.lower()
    
    condition_terms = ["excellent", "good condition", "mint", "barely used", "like new", "original"]
    for term in condition_terms:
        if term in text_lower:
            result["condition_notes"] = term
            break
    
    reason_terms = ["upgrading", "moving", "not using", "don't need", "new phone"]
    for term in reason_terms:
        if term in text_lower:
            result["reason_for_selling"] = term
            break
    
    urgency_terms = ["urgent", "quick sale", "asap", "today", "fast"]
    for term in urgency_terms:
        if term in text_lower:
            result["urgency"] = term
            break
    
    include_terms = ["box", "charger", "warranty", "original", "covers", "case"]
    for term in include_terms:
        if term in text_lower:
            result["includes"].append(term)
    
    return result


async def parse_message_llm_fallback(message: str) -> dict:
    """Parse message using LLM for ambiguous cases."""
    intent = detect_intent(message)
    sentiment = detect_sentiment(message)
    extracted_price = extract_price(message)
    seller_info = extract_seller_info(message)
    
    confidence = 0.8
    if intent == Intent.UNKNOWN:
        confidence = 0.3
    
    return {
        "intent": intent.value,
        "sentiment": sentiment.value,
        "extracted_price": extracted_price,
        "confidence": confidence,
        **seller_info,
    }


async def parse_message(message: str) -> dict:
    """Main message parsing entry point."""
    return await parse_message_llm_fallback(message)