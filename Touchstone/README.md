# Touchstone

**Open source marketing attribution for SMBs.**

Self-hosted, privacy-respecting multi-touch attribution. Drop a lightweight tracking pixel on your site, connect your CRM via webhook, and see which campaigns actually drive revenue.

## Quickstart

```bash
# With Docker
docker-compose up -d

# Without Docker (requires PostgreSQL)
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8200
```

## Tracking Pixel

Add to any page:

```html
<script src="https://your-server:8200/pixel/touchstone.js"
        data-api="https://your-server:8200"></script>
```

The pixel automatically:
- Generates an anonymous visitor ID (first-party cookie)
- Captures page views, referrer, and UTM parameters
- Respects Do Not Track (DNT) headers

### Custom Events

```javascript
touchstone.track("form_submit", { form: "contact-us" });
touchstone.identify("user@example.com", "Jane Doe", "Acme Corp");
```

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/collect` | Receive tracking events (204 No Content) |
| POST | `/api/v1/identify` | Link anonymous visitor to known contact |
| POST | `/api/v1/webhooks/crm` | Receive deal outcomes from CRM |
| GET/POST | `/api/v1/campaigns` | Campaign CRUD |
| GET | `/api/v1/contacts` | List contacts with touchpoint counts |
| GET | `/api/v1/contacts/{id}/journey` | Full touchpoint timeline |
| GET | `/api/v1/health` | Health check |

## Privacy

- First-party cookies only (no third-party tracking)
- No fingerprinting
- Respects DNT header
- All data stays on your server
- GDPR-friendly: you control the data

## Licence

MIT - Almost Magic Tech Lab
