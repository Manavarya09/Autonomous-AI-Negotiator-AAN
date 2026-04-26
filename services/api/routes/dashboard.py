"""Simple HTML dashboard for AAN."""

from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import get_db
from config.database.models import NormalizedListing, NegotiationJob

router = APIRouter(prefix="", tags=["dashboard"])

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AAN - Listings Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f7fa; }
        .header { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); color: white; padding: 1.5rem 2rem; }
        .header h1 { font-size: 1.5rem; margin-bottom: 0.25rem; }
        .header .subtitle { opacity: 0.7; font-size: 0.875rem; }
        .container { max-width: 1400px; margin: 0 auto; padding: 2rem; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
        .stat-card { background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .stat-card .label { color: #666; font-size: 0.875rem; margin-bottom: 0.5rem; }
        .stat-card .value { font-size: 2rem; font-weight: 700; color: #1a1a2e; }
        .filters { background: white; padding: 1.5rem; border-radius: 12px; margin-bottom: 2rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .filters form { display: flex; gap: 1rem; flex-wrap: wrap; align-items: flex-end; }
        .form-group { display: flex; flex-direction: column; gap: 0.5rem; }
        .form-group label { font-size: 0.875rem; color: #666; font-weight: 500; }
        .form-group input, .form-group select { padding: 0.75rem; border: 1px solid #e5e7eb; border-radius: 8px; font-size: 1rem; min-width: 150px; }
        .form-group input:focus, .form-group select:focus { outline: none; border-color: #4f46e5; }
        .btn { padding: 0.75rem 1.5rem; background: #4f46e5; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 1rem; font-weight: 500; transition: background 0.2s; }
        .btn:hover { background: #4338ca; }
        .btn-secondary { background: white; color: #4f46e5; border: 1px solid #4f46e5; }
        .btn-secondary:hover { background: #f5f7fa; }
        .listings-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 1.5rem; }
        .listing-card { background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1); transition: all 0.2s; }
        .listing-card:hover { transform: translateY(-4px); box-shadow: 0 8px 25px rgba(0,0,0,0.15); }
        .listing-image { height: 180px; background: linear-gradient(135deg, #e5e7eb 0%, #d1d5db 100%); display: flex; align-items: center; justify-content: center; color: #9ca3af; font-size: 1.25rem; }
        .listing-content { padding: 1.25rem; }
        .listing-title { font-size: 1rem; font-weight: 600; margin-bottom: 0.5rem; color: #1a1a2e; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .listing-price { font-size: 1.5rem; font-weight: 700; color: #059669; margin-bottom: 0.75rem; }
        .listing-meta { display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 0.5rem; }
        .badge { display: inline-block; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 500; }
        .badge-platform { background: #dbeafe; color: #1e40af; }
        .badge-condition { background: #d1fae5; color: #065f46; }
        .listing-details { font-size: 0.875rem; color: #666; }
        .listing-details span { margin-right: 1rem; }
        .score-bar { height: 6px; background: #e5e7eb; border-radius: 3px; margin-top: 1rem; overflow: hidden; }
        .score-fill { height: 100%; background: linear-gradient(90deg, #4f46e5, #7c3aed); border-radius: 3px; transition: width 0.3s; }
        .score-label { font-size: 0.75rem; color: #666; margin-top: 0.5rem; display: flex; justify-content: space-between; }
        .empty { text-align: center; padding: 4rem; color: #666; background: white; border-radius: 12px; }
        .empty h2 { margin-bottom: 0.5rem; color: #1a1a2e; }
        .empty p { margin-bottom: 1.5rem; }
    </style>
</head>
<body>
    <div class="header">
        <h1>AAN - Autonomous AI Negotiator</h1>
        <div class="subtitle">Deal Discovery Dashboard</div>
    </div>
    <div class="container">
        <div class="stats">
            <div class="stat-card">
                <div class="label">Total Listings</div>
                <div class="value">{{ total_listings }}</div>
            </div>
            <div class="stat-card">
                <div class="label">Platforms</div>
                <div class="value">{{ platforms }}</div>
            </div>
            <div class="stat-card">
                <div class="label">Avg Score</div>
                <div class="value">{{ avg_score }}%</div>
            </div>
            <div class="stat-card">
                <div class="label">Active Jobs</div>
                <div class="value">{{ active_jobs }}</div>
            </div>
        </div>
        <div class="filters">
            <form method="get" action="/dashboard">
                <div class="form-group">
                    <label>Search</label>
                    <input type="text" name="product" placeholder="Nikon D750, MacBook..." value="{{ product_filter }}">
                </div>
                <div class="form-group">
                    <label>Platform</label>
                    <select name="platform">
                        <option value="">All</option>
                        <option value="dubizzle" {% if platform_filter == 'dubizzle' %}selected{% endif %}>Dubizzle</option>
                        <option value="olx" {% if platform_filter == 'olx' %}selected{% endif %}>OLX</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Max Price</label>
                    <input type="number" name="max_price" placeholder="AED" value="{{ max_price_filter }}">
                </div>
                <div class="form-group">
                    <label>Sort</label>
                    <select name="sort">
                        <option value="score" {% if sort == 'score' %}selected{% endif %}>Best Score</option>
                        <option value="price" {% if sort == 'price' %}selected{% endif %}>Lowest Price</option>
                        <option value="date" {% if sort == 'date' %}selected{% endif %}>Newest</option>
                    </select>
                </div>
                <button type="submit" class="btn">Filter</button>
                <a href="/dashboard" class="btn btn-secondary">Clear</a>
            </form>
        </div>
        {% if listings %}
        <div class="listings-grid">
            {% for listing in listings %}
            <div class="listing-card">
                <div class="listing-image">{% if listing.image_urls and listing.image_urls[0] %}<img src="{{ listing.image_urls[0] }}" style="width:100%;height:100%;object-fit:cover;">{% else %}No Image{% endif %}</div>
                <div class="listing-content">
                    <div class="listing-title">{{ listing.product_name }}</div>
                    <div class="listing-price">AED {{ "%.0f"|format(listing.price) }}</div>
                    <div class="listing-meta">
                        <span class="badge badge-platform">{{ listing.platform }}</span>
                        <span class="badge badge-condition">{{ listing.condition or 'used' }}</span>
                    </div>
                    <div class="listing-details">
                        <span>{{ listing.location_city or 'Dubai' }}</span>
                        {% if listing.is_negotiable %}<span style="color:#059669;">Negotiable</span>{% endif %}
                    </div>
                    <div class="score-bar"><div class="score-fill" style="width: {{ listing.listing_score * 100 }}%"></div>
                    <div class="score-label"><span>Score</span><span>{{ "%.0f"|format(listing.listing_score * 100) }}%</span></div>
                </div>
            </div>
            {% endfor %}
        </div>
        {% else %}
        <div class="empty">
            <h2>No listings found</h2>
            <p>Adjust filters or create a job to discover listings.</p>
            <a href="/jobs/new" class="btn">Create New Job</a>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    product: str = Query(None),
    platform: str = Query(None),
    max_price: float = Query(None),
    sort: str = Query("score"),
    db: AsyncSession = None,
):
    query = select(NormalizedListing)

    if product:
        query = query.where(NormalizedListing.product_name.ilike(f"%{product}%"))
    if platform:
        query = query.where(NormalizedListing.platform == platform)
    if max_price:
        query = query.where(NormalizedListing.price <= max_price)

    if sort == "price":
        query = query.order_by(NormalizedListing.price.asc())
    elif sort == "date":
        query = query.order_by(NormalizedListing.normalized_at.desc())
    else:
        query = query.order_by(NormalizedListing.listing_score.desc())

    query = query.limit(50)
    result = await db.execute(query)
    listings = result.scalars().all()

    count_result = await db.execute(select(func.count(NormalizedListing.id)))
    total_listings = count_result.scalar() or 0

    platform_result = await db.execute(
        select(func.count(func.distinct(NormalizedListing.platform)))
    )
    platforms = platform_result.scalar() or 0

    avg_result = await db.execute(
        select(func.avg(NormalizedListing.listing_score))
    )
    avg_score = avg_result.scalar() or 0

    job_result = await db.execute(
        select(func.count(NegotiationJob.id)).where(
            NegotiationJob.status.in_(["queued", "running"])
        )
    )
    active_jobs = job_result.scalar() or 0

    listings_data = []
    for l in listings:
        listings_data.append({
            "product_name": l.product_name or "Unknown",
            "price": l.price or 0,
            "platform": l.platform or "unknown",
            "condition": l.condition or "used",
            "location_city": l.location_city or "Dubai",
            "is_negotiable": l.is_negotiable,
            "listing_score": l.listing_score or 0,
            "image_urls": list(l.image_urls) if l.image_urls else [],
        })

    html = DASHBOARD_HTML
    import re

    def replace_var(match):
        var = match.group(1)
        mapping = {
            "total_listings": str(total_listings),
            "platforms": str(platforms),
            "avg_score": str(int(avg_score * 100)),
            "active_jobs": str(active_jobs),
            "product_filter": product or "",
            "platform_filter": platform or "",
            "max_price_filter": str(int(max_price)) if max_price else "",
            "sort": sort,
        }
        return mapping.get(var, "")

    html = re.sub(r"\{\{ (\w+) \}\}", replace_var, html)

    from typing import Any
    listings_json = str(listings_data).replace("'", '"')
    html = html.replace("{{ listings }}", listings_json)

    final_html = DASHBOARD_HTML
    final_html = final_html.replace("{{ total_listings }}", str(total_listings))
    final_html = final_html.replace("{{ platforms }}", str(platforms))
    final_html = final_html.replace("{{ avg_score }}", str(int(avg_score * 100)))
    final_html = final_html.replace("{{ active_jobs }}", str(active_jobs))
    final_html = final_html.replace("{{ product_filter }}", product or "")
    final_html = final_html.replace("{{ platform_filter }}", platform or "")
    final_html = final_html.replace("{{ max_price_filter }}", str(int(max_price)) if max_price else "")
    final_html = final_html.replace("{{ sort }}", sort)

    return final_html


@router.get("/dashboard/", response_class=HTMLResponse)
async def dashboard_slash(db: AsyncSession = None):
    return await dashboard(db=db)