# Speed Champions - Backend API 🏁

Django REST API backend for Speed Champions, a karting race results tracking and analytics platform.

**Frontend Repository:** [https://github.com/COU7INHO/speedway-stats](https://github.com/COU7INHO/speedway-stats)

## Overview

This backend provides a robust REST API for managing karting race data, including AI-powered OCR for automatic race result extraction from timing sheet images. Built with Django and PostgreSQL, it handles driver statistics, race results, circuit information, and performance analytics.

## Key Features

### 🤖 AI-Powered OCR
Automatically extract race results from timing sheet images using Mistral AI's vision model. Upload a photo and get structured race data instantly.

### 📊 Comprehensive Analytics
- Driver performance tracking and evolution
- Circuit-specific statistics
- Leaderboard rankings
- Lap time analysis
- Race history and comparisons

### 🔒 Secure Authentication
Session-based authentication with CSRF protection, designed to work seamlessly with modern frontend frameworks.

### 🌐 CORS & Production Ready
Configured for production deployment with proper CORS policies, security headers, and optimized for serving behind Cloudflare.

## Technology Stack

- **Django 6.0** - Web framework
- **Django REST Framework** - API toolkit
- **PostgreSQL** - Database (production)
- **Mistral AI** - OCR vision model
- **Gunicorn** - WSGI server
- **Docker** - Containerization
- **Nginx** - Reverse proxy & static files

## Architecture

```
┌─────────────┐
│  Cloudflare │  HTTPS/SSL, CDN
└──────┬──────┘
       │
┌──────▼──────┐
│    Nginx    │  Reverse proxy, static files
└──────┬──────┘
       │
┌──────▼──────┐
│   Django    │  API logic, OCR processing
│  (Gunicorn) │
└──────┬──────┘
       │
┌──────▼──────┐
│ PostgreSQL  │  Race data storage
└─────────────┘
```

## Project Structure

```
speed_champion/
├── speed_champion/
│   ├── settings/           # Environment-specific settings
│   │   ├── base.py        # Common settings
│   │   ├── development.py # Local development
│   │   └── production.py  # Production config
│   ├── api/
│   │   ├── drivers/       # Driver management
│   │   ├── circuits/      # Circuit management
│   │   └── races/         # Race results & OCR
│   └── urls.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── manage.py
```

## API Endpoints

### Authentication
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `GET /api/auth/status/` - Check authentication status

### Drivers
- `GET /api/drivers/` - List all drivers
- `GET /api/drivers/{id}/` - Driver details and stats
- `GET /api/drivers/{id}/evolution/` - Performance over time
- `GET /api/drivers/compare/` - Compare multiple drivers

### Circuits
- `GET /api/circuits/` - List all circuits

### Races
- `GET /api/races/` - List races (filterable by circuit/driver)
- `GET /api/races/{id}/` - Race details with results
- `POST /api/races/upload-image/` - OCR extraction from image
- `POST /api/races/save-results/` - Save race results

### Leaderboard
- `GET /api/leaderboard/` - Current rankings

## Getting Started

### Prerequisites

- Python 3.12+
- PostgreSQL (production) or SQLite (development)
- Docker & Docker Compose (recommended)

### Development Setup

```bash
# Clone repository
git clone https://github.com/COU7INHO/karst-app-backend.git
cd karst-app-backend/speed_champion

# Install dependencies (using uv)
uv pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your configuration

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### Docker Deployment (Production)

```bash
# Build and start containers
docker compose up -d --build

# Collect static files
docker compose exec web python manage.py collectstatic --noinput

# Create superuser
docker compose exec web python manage.py createsuperuser
```

## Environment Variables

Required variables in `.env`:

```env
# Environment
DJANGO_ENV=production

# Security
SECRET_KEY=your-secret-key-here

# Database (PostgreSQL)
DB_NAME=karts_db
DB_USER=karts_user
DB_PASSWORD=your-db-password
DB_HOST=db
DB_PORT=5432

# AI/OCR
MISTRAL_API_KEY=your-mistral-api-key
```

## Deployment

The application is designed to run on a Raspberry Pi using:
- **Docker Compose** for container orchestration
- **Nginx** for serving static files and reverse proxy
- **Cloudflare Tunnel** for HTTPS and external access

See `DEPLOY.md` for detailed deployment instructions.

## Settings Organization

Settings are split by environment:

- **`base.py`** - Common settings (installed apps, middleware, etc)
- **`development.py`** - Local dev (SQLite, debug mode, CORS allow all)
- **`production.py`** - Production (PostgreSQL, security headers, restricted CORS)

Switch environments via `DJANGO_ENV` environment variable.

## Logging

Logs are configured to output to:
- **Console** - All environments
- **`app_logs.log`** - Application logs
- **`django.log`** - Framework logs

## License

Private project - All rights reserved

---

**Live Application:** [karts.tiago-coutinho.com](https://karts.tiago-coutinho.com)
