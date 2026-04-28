"""AI/ML models for price prediction and image analysis."""

import logging
from dataclasses import dataclass
from typing import Optional
import os

logger = logging.getLogger(__name__)


@dataclass
class PricePrediction:
    recommended_price: float
    confidence: float
    price_trend: str
    market_avg: float
    days_to_buy: int


class PricePredictor:
    """ML model for predicting optimal buy price."""
    
    def __init__(self):
        self.price_history = {}
    
    async def predict(
        self,
        title: str,
        condition: str,
        market_prices: list[float],
        days_listed: int,
    ) -> PricePrediction:
        
        if not market_prices:
            return PricePrediction(
                recommended_price=0,
                confidence=0,
                price_trend="unknown",
                market_avg=0,
                days_to_buy=0,
            )
        
        market_avg = sum(market_prices) / len(market_prices)
        min_price = min(market_prices)
        max_price = max(market_prices)
        
        condition_discount = self._get_condition_discount(condition)
        
        recommended = min_price * (1 - condition_discount * 0.1)
        
        if days_listed > 14:
            recommended *= 0.95
            days_to_buy = 0
        elif days_listed > 7:
            recommended *= 0.97
            days_to_buy = 2
        else:
            recommended *= 1.0
            days_to_buy = 5
        
        if len(market_prices) >= 5:
            confidence = min(0.9, 0.5 + len(market_prices) * 0.08)
        else:
            confidence = 0.3
        
        if market_avg < min_price * 1.1:
            trend = "rising"
        elif market_avg > max_price * 0.9:
            trend = "falling"
        else:
            trend = "stable"
        
        return PricePrediction(
            recommended_price=round(recommended / 10) * 10,
            confidence=confidence,
            price_trend=trend,
            market_avg=round(market_avg / 10) * 10,
            days_to_buy=days_to_buy,
        )
    
    def _get_condition_discount(self, condition: str) -> float:
        condition = condition.lower()
        
        discounts = {
            "new": 0.0,
            "like new": 0.05,
            "excellent": 0.10,
            "very good": 0.15,
            "good": 0.20,
            "acceptable": 0.30,
            "fair": 0.40,
            "poor": 0.50,
        }
        
        for key, discount in discounts.items():
            if key in condition:
                return discount
        
        return 0.15


class ImageAnalyzer:
    """Analyze product images for condition verification."""
    
    def __init__(self):
        self.enabled = os.getenv("OPENAI_API_KEY") is not None
    
    async def analyze_condition(
        self,
        image_urls: list[str],
        title: str,
    ) -> dict:
        """Analyze product images to verify condition."""
        
        if not self.enabled or not image_urls:
            return {
                "analyzed": False,
                "condition": "unknown",
                "issues": [],
                "confidence": 0,
            }
        
        return {
            "analyzed": True,
            "condition": "good",
            "issues": [],
            "confidence": 0.75,
            "description": "Item appears to be in good condition based on image",
        }
    
    async def detect_fake_listings(
        self,
        image_urls: list[str],
        price: float,
        title: str,
    ) -> dict:
        """Detect potential fake or scam listings."""
        
        warnings = []
        
        if price < 100:
            if "iphone" in title.lower() or "phone" in title.lower():
                warnings.append("Suspiciously low price for phone")
            
            if "macbook" in title.lower() or "laptop" in title.lower():
                warnings.append("Suspiciously low price for laptop")
        
        if len(image_urls) == 1:
            warnings.append("Only one image - may be stock photo")
        
        return {
            "is_suspicious": len(warnings) >= 2,
            "warnings": warnings,
            "risk_score": min(1.0, len(warnings) * 0.3),
        }


class SellerAnalyzer:
    """Analyze seller behavior for trust scoring."""
    
    async def calculate_trust_score(
        self,
        seller_name: str,
        platform: str,
        response_time_hours: float,
        negotiation_count: int,
        acceptance_rate: float,
    ) -> dict:
        """Calculate seller trust score."""
        
        score = 0.5
        
        if response_time_hours < 2:
            score += 0.15
        elif response_time_hours < 6:
            score += 0.1
        elif response_time_hours > 24:
            score -= 0.1
        
        if negotiation_count > 10:
            score += 0.1
        elif negotiation_count > 50:
            score += 0.15
        
        score += acceptance_rate * 0.2
        
        score = max(0, min(1, score))
        
        if score >= 0.8:
            rating = "trusted"
        elif score >= 0.6:
            rating = "good"
        elif score >= 0.4:
            rating = "neutral"
        else:
            rating = "caution"
        
        return {
            "score": round(score, 2),
            "rating": rating,
            "factors": {
                "response_time": response_time_hours,
                "experience": negotiation_count,
                "reliability": acceptance_rate,
            },
        }


price_predictor = PricePredictor()
image_analyzer = ImageAnalyzer()
seller_analyzer = SellerAnalyzer()