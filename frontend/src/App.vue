<template>
  <div>
    <!-- Navigation -->
    <nav class="nav">
      <div class="nav-container">
        <div class="nav-logo">
          <div class="logo-icon">A</div>
          <span class="logo-text">AAN</span>
        </div>
        <ul class="nav-links">
          <li><a href="#features">Features</a></li>
          <li><a href="#how-it-works">How It Works</a></li>
          <li><a href="#pricing">Pricing</a></li>
        </ul>
        <div class="nav-cta">
          <a href="/dashboard" class="btn btn-secondary">Dashboard</a>
          <a href="#pricing" class="btn btn-primary">Get Started</a>
        </div>
      </div>
    </nav>

    <!-- Hero Section -->
    <section class="hero">
      <div class="hero-content">
        <div class="hero-badge">
          <span>🚀</span>
          <span>AI-Powered Deal Negotiation</span>
        </div>
        <h1 class="hero-title">
          Never<span class="highlight">Overpay</span> Again
        </h1>
        <p class="hero-subtitle">
          Let our autonomous AI negotiate the best deals for you across 
          Dubizzle, OLX, Facebook Marketplace & more. Save time, save money.
        </p>
        <div class="hero-buttons">
          <a href="/dashboard" class="btn btn-primary">Start Free Trial</a>
          <a href="#how-it-works" class="btn btn-secondary">See How It Works</a>
        </div>
        <div class="hero-stats">
          <div class="stat">
            <div class="stat-value">40%+</div>
            <div class="stat-label">Average Savings</div>
          </div>
          <div class="stat">
            <div class="stat-value">50+</div>
            <div class="stat-label">Active Negotiations</div>
          </div>
          <div class="stat">
            <div class="stat-value">24h</div>
            <div class="stat-label">Avg. Time to Close</div>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section id="features" class="features">
      <div class="features-container">
        <div class="section-header">
          <div class="section-label">Features</div>
          <h2 class="section-title">Everything You Need to Save</h2>
          <p class="section-subtitle">
            Powerful AI automation that finds deals, negotiates prices, 
            and closes deals while you focus on what matters.
          </p>
        </div>
        <div class="features-grid">
          <div class="feature-card">
            <div class="feature-icon">🔍</div>
            <h3 class="feature-title">Multi-Platform Discovery</h3>
            <p class="feature-description">
              Aggregates listings from Dubizzle, OLX, Facebook Marketplace, 
              Noon & Amazon.ae in real-time.
            </p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">🤖</div>
            <h3 class="feature-title">AI-Powered Negotiation</h3>
            <p class="feature-description">
              Large language models generate human-like negotiation 
              messages adapted to each seller's behavior.
            </p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">📊</div>
            <h3 class="feature-title">Smart Scoring</h3>
            <p class="feature-description">
              Weighted algorithms score deals based on price, condition, 
              location, negotiability & recency.
            </p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">⚡</div>
            <h3 class="feature-title">Parallel Threads</h3>
            <p class="feature-description">
              Negotiate with multiple sellers simultaneously to find 
              the best deal fast.
            </p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">📧</div>
            <h3 class="feature-title">Email Automation</h3>
            <p class="feature-description">
              Automated email communication with intelligent reply 
              parsing and intent classification.
            </p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">🎯</div>
            <h3 class="feature-title">Auto-Close</h3>
            <p class="feature-description">
              Auto-accept deals when they meet your criteria. 
              Zero manual intervention needed.
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- How It Works -->
    <section id="how-it-works" class="how-it-works">
      <div class="steps-container">
        <div class="section-header">
          <div class="section-label">How It Works</div>
          <h2 class="section-title">Set It & Forget It</h2>
          <p class="section-subtitle">
            Your personal AI negotiator works 24/7 to get you the best deals.
          </p>
        </div>
        <div class="steps">
          <div class="step">
            <div class="step-number">1</div>
            <div class="step-content">
              <h3>Submit Your Query</h3>
              <p>Tell us what you want to buy, your target price, max budget, and preferred location.</p>
            </div>
          </div>
          <div class="step">
            <div class="step-number">2</div>
            <div class="step-content">
              <h3>AI Discovers Deals</h3>
              <p>Our scrapers find listings across 5+ platforms, normalize the data, and score them.</p>
            </div>
          </div>
          <div class="step">
            <div class="step-number">3</div>
            <div class="step-content">
              <h3>Negotiation Begins</h3>
              <p>AI agents negotiate with sellers via email using adaptive strategies.</p>
            </div>
          </div>
          <div class="step">
            <div class="step-number">4</div>
            <div class="step-content">
              <h3>Deal Closed</h3>
              <p>Get notified with the best deal. Auto-close if it meets your criteria.</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Pricing Section -->
    <section id="pricing" class="pricing">
      <div class="pricing-container">
        <div class="section-header">
          <div class="section-label">Pricing</div>
          <h2 class="section-title">Simple, Transparent Pricing</h2>
          <p class="section-subtitle">
            Start free, upgrade when you're ready. No hidden fees.
          </p>
        </div>
        <div class="pricing-grids">
          <div class="pricing-card">
            <h3 class="pricing-name">Starter</h3>
            <div class="pricing-price">$0<span>/month</span></div>
            <p class="pricing-description">Perfect for trying it out</p>
            <ul class="pricing-features">
              <li>3 job searches/month</li>
              <li>5 negotiations/month</li>
              <li>Basic scoring</li>
              <li>Email support</li>
            </ul>
            <a href="#" class="btn btn-secondary" style="width: 100%; display: block;">Get Started</a>
          </div>
          <div class="pricing-card featured">
            <h3 class="pricing-name">Pro</h3>
            <div class="pricing-price">$29<span>/month</span></div>
            <p class="pricing-description">For serious buyers</p>
            <ul class="pricing-features">
              <li>Unlimited job searches</li>
              <li>Unlimited negotiations</li>
              <li>Advanced scoring</li>
              <li>Auto-close feature</li>
              <li>Priority support</li>
            </ul>
            <a href="#" class="btn btn-primary" style="width: 100%; display: block;">Start Free Trial</a>
          </div>
          <div class="pricing-card">
            <h3 class="pricing-name">Business</h3>
            <div class="pricing-price">$99<span>/month</span></div>
            <p class="pricing-description">For resellers & teams</p>
            <ul class="pricing-features">
              <li>Everything in Pro</li>
              <li>5 team members</li>
              <li>API access</li>
              <li>Dedicated support</li>
              <li>Custom integrations</li>
            </ul>
            <a href="#" class="btn btn-secondary" style="width: 100%; display: block;">Contact Sales</a>
          </div>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="footer">
      <div class="footer-container">
        <div class="footer-brand">
          <div class="nav-logo">
            <div class="logo-icon">A</div>
            <span class="logo-text">AAN</span>
          </div>
          <p>Autonomous AI Negotiator - Your personal AI agent for finding and negotiating the best deals.</p>
        </div>
        <div>
          <h4 class="footer-title">Product</h4>
          <ul class="footer-links">
            <li><a href="#features">Features</a></li>
            <li><a href="#pricing">Pricing</a></li>
            <li><a href="/docs">Documentation</a></li>
          </ul>
        </div>
        <div>
          <h4 class="footer-title">Company</h4>
          <ul class="footer-links">
            <li><a href="#">About</a></li>
            <li><a href="#">Blog</a></li>
            <li><a href="#">Careers</a></li>
          </ul>
        </div>
        <div>
          <h4 class="footer-title">Legal</h4>
          <ul class="footer-links">
            <li><a href="#">Privacy</a></li>
            <li><a href="#">Terms</a></li>
            <li><a href="#">Security</a></li>
          </ul>
        </div>
      </div>
      <div class="footer-bottom">
        <span>&copy; 2026 AAN. All rights reserved.</span>
        <span>Built with 🤖 by Manav Arya Singh</span>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const isScrolled = ref(false)

onMounted(() => {
  window.addEventListener('scroll', () => {
    isScrolled.value = window.scrollY > 50
  })
})
</script>