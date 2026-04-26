<template>
  <div>
    <!-- Navigation -->
    <nav class="nav">
      <div class="nav-container">
        <a href="/" class="nav-logo">
          <div class="logo-mark">A</div>
          <span>AAN</span>
        </a>
        <ul class="nav-links">
          <li><a href="#features">Features</a></li>
          <li><a href="#how-it-works">How It Works</a></li>
        </ul>
        <div class="nav-actions">
          <a href="/dashboard" class="btn btn-primary">Get Started</a>
        </div>
      </div>
    </nav>

    <!-- Hero Section -->
    <section class="hero">
      <div class="hero-content">
        <div class="hero-tag">Autonomous Negotiation</div>
        <h1 class="hero-title">
          The smartest way<br />to buy anything.
        </h1>
        <p class="hero-subtitle">
          AAN finds listings across Dubizzle, OLX, Facebook Marketplace and more.
          Our AI negotiates with sellers in real-time to secure the best price.
          You just approve the deal.
        </p>
        <div class="hero-actions">
          <a href="/dashboard" class="btn btn-primary">Start Negotiating</a>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section id="features" class="section">
      <div class="section-inner">
        <div class="section-header">
          <div class="section-label">Capabilities</div>
          <h2 class="section-title">Built for modern buyers</h2>
        </div>
        <div class="features-grid">
          <div class="feature-card">
            <h3 class="feature-title">Multi-Platform Search</h3>
            <p class="feature-text">Aggregate listings from Dubizzle, OLX, Facebook Marketplace, Noon, and Amazon.ae in real-time.</p>
          </div>
          <div class="feature-card">
            <h3 class="feature-title">Adaptive Negotiation</h3>
            <p class="feature-text">AI agents adapt to seller behavior. Low anchor for flexible sellers, bundle strategy for rigid ones.</p>
          </div>
          <div class="feature-card">
            <h3 class="feature-title">Intelligent Scoring</h3>
            <p class="feature-text">Weighted ranking by price, condition, location, negotiability, and recency.</p>
          </div>
          <div class="feature-card">
            <h3 class="feature-title">Parallel Threads</h3>
            <p class="feature-text">Negotiate with 10+ sellers simultaneously. First accepted deal wins.</p>
          </div>
          <div class="feature-card">
            <h3 class="feature-title">Auto-Close</h3>
            <p class="feature-text">Automatically accept when a deal hits your target. Zero manual intervention.</p>
          </div>
          <div class="feature-card">
            <h3 class="feature-title">Outcome Learning</h3>
            <p class="feature-text">System learns from every negotiation. Strategy improves over time.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- How It Works -->
    <section id="how-it-works" class="section">
      <div class="section-inner">
        <div class="section-header">
          <div class="section-label">Process</div>
          <h2 class="section-title">Four simple steps</h2>
        </div>
        <div class="steps-grid">
          <div class="step">
            <div class="step-num">Step 01</div>
            <h3 class="step-title">Submit Query</h3>
            <p class="step-text">Tell us what you want to buy, your target price, and max budget.</p>
          </div>
          <div class="step">
            <div class="step-num">Step 02</div>
            <h3 class="step-title">AI Discovers</h3>
            <p class="step-text">Our scrapers find listings across 5+ platforms and normalize the data.</p>
          </div>
          <div class="step">
            <div class="step-num">Step 03</div>
            <h3 class="step-title">Negotiation</h3>
            <p class="step-text">AI agents negotiate with sellers using adaptive strategies via email.</p>
          </div>
          <div class="step">
            <div class="step-num">Step 04</div>
            <h3 class="step-title">Deal Closed</h3>
            <p class="step-text">Get notified with the best deal. Auto-close if it meets your criteria.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Use Cases -->
    <section class="section">
      <div class="section-inner">
        <div class="section-header">
          <div class="section-label">Use Cases</div>
          <h2 class="section-title">Who it's for</h2>
        </div>
        <div class="use-cases">
          <div class="use-case">
            <h3 class="use-case-title">Electronics Buyers</h3>
            <p class="use-case-text">Find the best deals on laptops, cameras, phones, and gadgets across UAE marketplaces.</p>
          </div>
          <div class="use-case">
            <h3 class="use-case-title">Resellers</h3>
            <p class="use-case-text">Source products at minimum cost across multiple platforms for arbitrage opportunities.</p>
          </div>
          <div class="use-case">
            <h3 class="use-case-title">Furniture Seekers</h3>
            <p class="use-case-text">Negotiate on sofas, beds, and appliances. Get the best price without the back-and-forth.</p>
          </div>
          <div class="use-case">
            <h3 class="use-case-title">Car Buyers</h3>
            <p class="use-case-text">Navigate used car listings. Negotiate price based on market data and vehicle condition.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="cta-section">
      <h2 class="cta-title">Ready to save?</h2>
      <p class="cta-subtitle">Start your first negotiation in under 60 seconds.</p>
      <a href="/dashboard" class="btn btn-primary">Launch Dashboard</a>
    </section>

    <!-- Footer -->
    <footer class="footer">
      <div class="footer-inner">
        <div class="footer-text">AAN - Autonomous AI Negotiator</div>
        <ul class="footer-links">
          <li><a href="#">Privacy</a></li>
          <li><a href="#">Terms</a></li>
          <li><a href="#">Contact</a></li>
        </ul>
      </div>
    </footer>
  </div>
</template>

<script setup>
</script>