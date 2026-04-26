"""Unit tests for AAN components."""

import pytest


class TestPriceExtraction:
    """Tests for price extraction in normalization."""
    
    def test_extract_simple_price(self):
        from services.worker.normalization.price import extract_price
        
        assert extract_price("AED 3,800") == 3800
        assert extract_price("3800 AED") == 3800
        assert extract_price("3,800") == 3800
    
    def test_extract_no_price(self):
        from services.worker.normalization.price import extract_price
        
        assert extract_price("Contact seller") is None
    
    def test_extract_invalid(self):
        from services.worker.normalization.price import extract_price
        
        assert extract_price("") is None
        assert extract_price(None) is None


class TestConditionNormalization:
    """Tests for condition normalization."""
    
    def test_new_condition(self):
        from services.worker.normalization.condition import normalize_condition
        
        label, score = normalize_condition("Brand new")
        assert label == "new"
        assert score == 1.0
    
    def test_used_condition(self):
        from services.worker.normalization.condition import normalize_condition
        
        label, score = normalize_condition("Used")
        assert label == "used"
        assert score == 0.6
    
    def test_excellent_condition(self):
        from services.worker.normalization.condition import normalize_condition
        
        label, score = normalize_condition("Excellent condition")
        assert label == "excellent"
        assert score == 0.8


class TestListingScore:
    """Tests for listing score calculation."""
    
    def test_best_deal_score(self):
        from services.worker.normalization.scoring import calculate_listing_score
        
        score = calculate_listing_score(
            price=3500,
            min_price=3500,
            max_price=4000,
            condition_score=0.9,
            posted_days_ago=1,
            is_negotiable=True,
            distance_km=2,
            radius_km=30,
        )
        assert score >= 0.8
    
    def test_poor_deal_score(self):
        from services.worker.normalization.scoring import calculate_listing_score
        
        score = calculate_listing_score(
            price=4500,
            min_price=3500,
            max_price=4000,
            condition_score=0.5,
            posted_days_ago=30,
            is_negotiable=False,
            distance_km=30,
            radius_km=30,
        )
        assert score <= 0.3


class TestIntentParser:
    """Tests for intent parsing."""
    
    def test_accept_intent(self):
        from services.worker.negotiation.intent_parser import classify_intent
        
        intent = classify_intent("Ok deal, you can take it")
        assert intent.value == "accept"
    
    def test_reject_intent(self):
        from services.worker.negotiation.intent_parser import classify_intent
        
        intent = classify_intent("No, thanks. Not selling.")
        assert intent.value == "reject"
    
    def test_counter_intent(self):
        from services.worker.negotiation.intent_parser import classify_intent
        
        intent = classify_intent("Last price is 4000 AED")
        assert intent.value == "counter"
    
    def test_price_extraction(self):
        from services.worker.negotiation.intent_parser import extract_price
        
        price = extract_price("My price is 3500 AED")
        assert price == 3500


class TestAgentState:
    """Tests for negotiation agent."""
    
    def test_initial_offer_low_anchor(self):
        from services.worker.negotiation.agent import AgentState, NegotiationStrategy
        from uuid import uuid4
        
        agent = AgentState(
            job_id=uuid4(),
            listing_id=uuid4(),
            seller_name="John",
            seller_contact="john@test.com",
            platform="dubizzle",
            list_price=4000,
            target_price=3500,
            max_price=4000,
            strategy=NegotiationStrategy.LOW_ANCHOR,
        )
        
        initial = agent.get_counter_offer()
        assert initial == 3500 * 0.85
    
    def test_is_terminal(self):
        from services.worker.negotiation.agent import AgentState, NegotiationStatus
        from uuid import uuid4
        
        agent = AgentState(
            job_id=uuid4(),
            listing_id=uuid4(),
            seller_name="John",
            seller_contact="john@test.com",
            platform="dubizzle",
            list_price=4000,
            target_price=3500,
            max_price=4000,
            status=NegotiationStatus.ACCEPTED,
        )
        
        assert agent.is_terminal() == True
    
    def test_non_terminal(self):
        from services.worker.negotiation.agent import AgentState, NegotiationStatus
        from uuid import uuid4
        
        agent = AgentState(
            job_id=uuid4(),
            listing_id=uuid4(),
            seller_name="John",
            seller_contact="john@test.com",
            platform="dubizzle",
            list_price=4000,
            target_price=3500,
            max_price=4000,
            status=NegotiationStatus.ACTIVE,
        )
        
        assert agent.is_terminal() == False


class TestSellerClassification:
    """Tests for seller behavior classification."""
    
    def test_flexible_seller(self):
        from services.worker.negotiation.agent import classify_seller, SellerType
        
        seller_type = classify_seller(
            title="Sony PS5 - OBO or offers",
            description="Negotiable price",
            price=3500,
            target_price=3500,
        )
        
        assert seller_type == SellerType.FLEXIBLE
    
    def test_rigid_seller(self):
        from services.worker.negotiation.agent import classify_seller, SellerType
        
        seller_type = classify_seller(
            title="iPhone 15 Pro",
            description="Price is firm",
            price=3500,
            target_price=2500,
        )
        
        assert seller_type == SellerType.RIGID


class TestDecisionEngine:
    """Tests for deal scoring."""
    
    def test_calculate_deal_score(self):
        from services.worker.negotiation.decision import calculate_deal_score
        
        score = calculate_deal_score(
            agreed_price=3500,
            target_price=3500,
            max_price=4000,
            trust_score=0.8,
            time_to_close_hours=12,
            rounds_taken=3,
            max_rounds=5,
        )
        
        assert score > 0.7
    
    def test_should_auto_close(self):
        from services.worker.negotiation.decision import should_auto_close
        
        assert should_auto_close(0.80) == True
        assert should_auto_close(0.60) == False


class TestDeduplication:
    """Tests for listing deduplication."""
    
    def test_duplicate_detection(self):
        from services.worker.normalization.deduplication import is_duplicate_title
        
        result = is_duplicate_title(
            "Nikon D750 Camera Body",
            "Nikon D750 Camera Body",
        )
        
        assert result == True
    
    def test_unique_detection(self):
        from services.worker.normalization.deduplication import is_duplicate_title
        
        result = is_duplicate_title(
            "Nikon D750 Camera Body",
            "Canon EOS R5",
        )
        
        assert result == False