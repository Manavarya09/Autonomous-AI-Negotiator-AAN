# AAN V2 Master Plan

## Version: 2.0 — Production Ready  
**Created:** April 2026  
**Status:** In Progress

---

## Phase Branches

| Branch | Phase | Status |
|--------|-------|---------|
| `v2-phase1-platform-expansion` | Platform Expansion | In Progress |
| `v2-phase2-smarter-negotiation` | Smarter Negotiation | Pending |
| `v2-phase3-production-ready` | Production Readiness | Pending |
| `v2-phase4-user-experience` | User Experience | Pending |
| `v2-phase5-scale-monetize` | Scale & Monetize | Pending |

---

# Phase 1: Platform Expansion (Weeks 1-4)

## Goals
- Add more marketplace scrapers
- Improve data quality
- Expand geographic coverage

## Tasks

### P1.1 Enhanced Scrapers
- [ ] P1.1.1 Add Facebook Marketplace scraper
- [ ] P1.1.2 Add Noon Daily scraper
- [ ] P1.1.3 Add Amazon.ae offers scraper  
- [ ] P1.1.4 Implement proxy rotation with BrightData
- [ ] P1.1.5 Add scraper reliability fallback system

### P1.2 Improved Intent Parsing
- [ ] P1.2.1 LLM-powered intent classification
- [ ] P1.2.2 Multi-language support (Arabic, Hindi, English)
- [ ] P1.2.3 Context-aware sentiment analysis
- [ ] P1.2.4 Extract condition notes, reason for selling

### P1.3 Infrastructure Hardening
- [ ] P1.3.1 Add proper error handling and retry logic
- [ ] P1.3.2 Implement circuit breaker for failing scrapers
- [ ] P1.3.3 Add structured logging with trace IDs
- [ ] P1.3.4 Database connection pooling

---

# Phase 2: Smarter Negotiation (Weeks 5-8)

## Goals
- Advanced AI strategies
- Learning from outcomes
- Better intent parsing

## Tasks

### P2.1 Adaptive Strategy Engine
- [ ] P2.1.1 Dynamic strategy switching
- [ ] P2.1.2 Game-theoretic counter-offer calculation
- [ ] P2.1.3 Seller personality detection
- [ ] P2.1.4 Concession planning

### P2.2 Learning System
- [ ] P2.2.1 Track strategy outcomes
- [ ] P2.2.2 Build seller profile database
- [ ] P2.2.3 A/B test different offers
- [ ] P2.2.4 Automated strategy optimization

### P2.3 Multi-Channel Communication
- [ ] P2.3.1 WhatsApp Business API
- [ ] P2.3.2 Platform-specific templates
- [ ] P2.3.3 In-app messaging

---

# Phase 3: Production Readiness (Weeks 9-12)

## Goals
- Better testing
- Monitoring
- Error handling
- CI/CD improvements

## Tasks

### P3.1 Testing & Quality
- [ ] P3.1.1 Add 50+ integration tests
- [ ] P3.1.2 Contract testing
- [ ] P3.1.3 E2E test scenarios
- [ ] P3.1.4 Load testing (100 users)

### P3.2 Monitoring & Observability
- [ ] P3.2.1 Prometheus metrics
- [ ] P3.2.2 Grafana dashboards
- [ ] P3.2.3 Error tracking (Sentry)
- [ ] P3.2.4 Slack alerts

### P3.3 Deployment & CI/CD
- [ ] P3.3.1 Multi-stage deployments
- [ ] P3.3.2 Blue-green deployment
- [ ] P3.3.3 Database migrations
- [ ] P3.3.4 Rollback mechanism

---

# Phase 4: User Experience (Weeks 13-16)

## Goals
- Real-time dashboard
- Better onboarding
- Notifications

## Tasks

### P4.1 Dashboard Overhaul
- [ ] P4.1.1 Real-time job status (WebSocket)
- [ ] P4.1.2 Interactive listing map
- [ ] P4.1.3 Negotiation timeline
- [ ] P4.1.4 Deal comparison

### P4.2 User Onboarding
- [ ] P4.2.1 Interactive search wizard
- [ ] P4.2.2 Quick-start templates
- [ ] P4.2.3 Budget recommendations

### P4.3 Notifications
- [ ] P4.3.1 Email notifications
- [ ] P4.3.2 Push notifications
- [ ] P4.3.3 Deal summaries

---

# Phase 5: Scale & Monetize (Weeks 17-24)

## Goals
- Multi-tenancy
- Monetization
- Advanced features

## Tasks

### P5.1 Multi-Tenancy
- [ ] P5.1.1 Organization support
- [ ] P5.1.2 Team collaboration

### P5.2 Monetization
- [ ] P5.2.1 Free tier (3 jobs/month)
- [ ] P5.2.2 Pro tier ($9.99/month)
- [ ] P5.2.3 Stripe/PayPal integration

### P5.3 Advanced Features
- [ ] P5.3.1 Price prediction
- [ ] P5.3.2 Deal alerts
- [ ] P5.3.3 Developer API

---

# Technical Debt

| Issue | Priority |
|-------|----------|
| Hardcoded secrets | Critical |
| No rate limiting | Critical |
| Scraper failures | High |
| No idempotency | Medium |