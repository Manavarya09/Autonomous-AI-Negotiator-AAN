<template>
  <div>
    <nav class="nav">
      <div class="nav-container">
        <div class="nav-logo">
          <div class="logo-mark">A</div>
          <span>AAN</span>
        </div>
        <ul class="nav-links">
          <li><a href="#features">Features</a></li>
          <li><a href="#proof">Results</a></li>
        </ul>
        <div>
          <a href="/dashboard" class="btn btn-outline">Dashboard</a>
        </div>
      </div>
    </nav>

    <section class="hero">
      <div class="hero-content">
        <div class="hero-label">Autonomous Negotiation</div>
        <h1 class="hero-title">
          The smartest way<br />to buy anything.
        </h1>
        <p class="hero-subtitle">
          AAN finds listings across Dubizzle, OLX, Facebook Marketplace and more.
          Our AI negotiates with sellers in real-time to secure the best price.
          You just approve the deal.
        </p>
        <div class="hero-buttons">
          <a href="/dashboard" class="btn btn-primary">Start Negotiating</a>
        </div>
        <div class="hero-stats">
          <div class="stat">
            <div class="stat-label">Avg Savings</div>
            <div class="stat-value">18%</div>
          </div>
          <div class="stat">
            <div class="stat-label">Deals Closed</div>
            <div class="stat-value">2,400+</div>
          </div>
          <div class="stat">
            <div class="stat-label">Active Users</div>
            <div class="stat-value">850</div>
          </div>
        </div>
      </div>
    </section>

    <section id="features" class="features">
      <div class="features-container">
        <div class="section-header">
          <div class="section-label">Capabilities</div>
          <h2 class="section-title">Built for modern buyers</h2>
        </div>
        <div class="features-grid">
          <div class="feature-cell">
            <h3>Multi-Platform Search</h3>
            <p>Aggregate listings from Dubizzle, OLX, Facebook Marketplace, Noon, and Amazon.ae in real-time.</p>
          </div>
          <div class="feature-cell">
            <h3>Adaptive Negotiation</h3>
            <p>AI agents adapt to seller behavior type. Low anchor for flexible sellers, bundle strategy for rigid ones.</p>
          </div>
          <div class="feature-cell">
            <h3>Intelligent Scoring</h3>
            <p>Weighted ranking by price, condition, location, negotiability, and recency. Let the system pick the best.</p>
          </div>
          <div class="feature-cell">
            <h3>Parallel Threads</h3>
            <p>Negotiate with 10+ sellers simultaneously. First accepted deal wins.</p>
          </div>
          <div class="feature-cell">
            <h3>Auto-Close</h3>
            <p>Automatically accept when a deal hits your target. No manual approval needed.</p>
          </div>
          <div class="feature-cell">
            <h3>Outcome Learning</h3>
            <p>System learns from every negotiation. Strategy improves over time.</p>
          </div>
        </div>
      </div>
    </section>

    <section id="proof" class="proof">
      <div class="proof-container">
        <div class="proof-grid">
          <div class="proof-text">
            <div class="section-label">Performance</div>
            <h2>Real results from real users</h2>
            <ul class="proof-list">
              <li>
                <span>Average savings per deal</span>
                <span>18%</span>
              </li>
              <li>
                <span>Negotiation success rate</span>
                <span>42%</span>
              </li>
              <li>
                <span>Avg. time to close</span>
                <span>18 hours</span>
              </li>
              <li>
                <span>Top category</span>
                <span>Electronics</span>
              </li>
              <li>
                <span>Most active platform</span>
                <span>Dubizzle</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </section>

    <section class="cta">
      <div class="cta-container">
        <h2>Ready to save?</h2>
        <p>Start your first negotiation in under 60 seconds.</p>
        <a href="/dashboard" class="btn btn-primary">Launch Dashboard</a>
      </div>
    </section>

    <footer class="footer">
      <div class="footer-container">
        <div class="footer-brand">
          AAN - Autonomous AI Negotiator
        </div>
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