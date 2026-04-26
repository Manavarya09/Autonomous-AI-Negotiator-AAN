# Autonomous AI Negotiator (AAN)

An AI-powered system that discovers deals across online marketplaces and autonomously negotiates with sellers to get the best price.

## Project Structure

```
Autonomous-AI-Negotiator-AAN/
├── services/
│   ├── api/           # FastAPI REST API
│   └── worker/        # Celery workers
├── config/
│   ├── core/          # Settings and config
│   └── scrapers/       # Platform scraper configs
├── tests/
│   ├── unit/          # Unit tests
│   └── integration/    # Integration tests
├── docker-compose.yml
└── pyproject.toml
```

## Quick Setup

1. Install dependencies:
   ```bash
   pip install -e .
   ```

2. Copy environment file:
   ```bash
   cp .env.example .env
   ```

3. Start with Docker Compose:
   ```bash
   docker-compose up -d
   ```

## Development

The project follows a branch-per-task workflow:
- Each major task has its own branch
- Branches are merged to main after review

## License

MIT