# CivicLens Backend API

A comprehensive backend API for civic issue reporting and management, built with FastAPI and PostgreSQL with PostGIS for geospatial capabilities.

## Features

### Core Features
- ✅ **User Management**: Register, login, logout with JWT authentication
- ✅ **Issue Management**: Full CRUD operations for civic issues
- ✅ **Status Tracking**: Track issues through lifecycle (Reported → Under Review → Work in Progress → Resolved)
- ✅ **Voting System**: Upvote/downvote issues with toggle support
- ✅ **Comments**: Add and retrieve comments on issues
- ✅ **Notifications**: Real-time notifications for status updates, reactions, badges, and milestones
- ✅ **Leaderboard**: Rank users by verified issues and upvotes
- ✅ **Geospatial Queries**: PostGIS-powered location search and duplicate detection

### Technical Features
- 🔐 **Security**: JWT authentication, bcrypt password hashing, input sanitization
- 🗺️ **Geospatial**: PostGIS for advanced location queries (radius search, duplicate detection)
- 📊 **Database**: PostgreSQL 15 with PostGIS extension
- ⚡ **Performance**: Async operations with SQLAlchemy 2.0
- 📝 **Validation**: Pydantic models for request/response validation
- 🎯 **Type Safety**: Full Python type hints

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 15+ with PostGIS
- pip or poetry for dependency management

### Installation

1. **Clone the repository** (if not already done)

2. **Install dependencies**:
```bash
cd /app/backend
pip install -r requirements.txt
```

3. **Set up PostgreSQL and PostGIS**:
```bash
chmod +x init_postgres.sh
./init_postgres.sh
```

This script will:
- Install PostgreSQL and PostGIS
- Create `civiclens` database
- Set up database user
- Enable PostGIS extension

4. **Configure environment variables**:

Edit `.env` file:
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/civiclens
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200  # 30 days
CORS_ORIGINS=*
```

5. **Run the server**:
```bash
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

The API will be available at:
- **Base URL**: `http://localhost:8001/api`
- **Health Check**: `http://localhost:8001/api/health`
- **API Docs**: `http://localhost:8001/docs` (Swagger UI)
- **ReDoc**: `http://localhost:8001/redoc`

## Project Structure

```
/app/backend/
├── server.py              # Main FastAPI application and routes
├── database.py            # Database connection and session management
├── models.py              # SQLAlchemy ORM models
├── schemas.py             # Pydantic request/response schemas
├── auth.py                # JWT authentication utilities
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
├── init_postgres.sh       # PostgreSQL setup script
├── API_DOCUMENTATION.md   # Complete API documentation
└── README.md              # This file
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/logout` - Logout user

### Issues
- `POST /api/issues` - Create new issue
- `GET /api/issues` - List issues (with filters)
- `GET /api/issues/{id}` - Get issue details
- `PATCH /api/issues/{id}/status` - Update issue status
- `POST /api/issues/{id}/vote` - Vote on issue

### Comments
- `POST /api/issues/{id}/comments` - Add comment
- `GET /api/issues/{id}/comments` - Get comments

### Notifications
- `GET /api/notifications` - Get user notifications
- `PATCH /api/notifications/{id}/read` - Mark as read
- `DELETE /api/notifications/clear` - Clear all notifications

### Leaderboard
- `GET /api/leaderboard` - Get top users

### Health
- `GET /api/health` - Health check
- `GET /api/` - API info

For complete API documentation, see [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)

## Testing

### Manual Testing with curl

```bash
# 1. Register a user
curl -X POST http://localhost:8001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'

# 2. Login (save the token)
TOKEN=$(curl -s -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }' | jq -r '.access_token')

# 3. Create an issue
curl -X POST http://localhost:8001/api/issues \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "title": "Broken Street Light",
    "description": "Street light on Main St is not working",
    "category": "Infrastructure",
    "latitude": 40.7128,
    "longitude": -74.0060,
    "area_name": "New York, NY"
  }'

# 4. List all issues
curl http://localhost:8001/api/issues

# 5. Get leaderboard
curl http://localhost:8001/api/leaderboard
```

### Run Test Script

A comprehensive test script is provided:
```bash
chmod +x test_api.sh
./test_api.sh
```

## Database Models

### User
- Basic profile: username, email, avatar, trust_score, badges
- Password hashing with bcrypt
- Relationship to issues, comments, votes, notifications

### Issue
- Full details: title, description, category, subcategory
- Geospatial: PostGIS Point, latitude, longitude, area_name
- Status tracking: Reported → Under Review → Work in Progress → Resolved
- Engagement: upvotes, downvotes
- Relationships: reporter, comments, votes

### Comment
- Text content with sanitization
- Linked to issue and user

### Vote
- Vote type: upvote or downvote
- One vote per user per issue (can be toggled)

### Notification
- Types: Status Updates, Reactions, Badges, Milestones
- Read/unread tracking

## Key Features Explained

### Duplicate Detection
When creating an issue, the system checks for similar issues within 100 meters using PostGIS:
```python
# Check title similarity and location proximity
ST_DWithin(
    ST_Transform(Issue.location, 3857),
    ST_Transform(point, 3857),
    100  # 100 meters
)
```

### Geospatial Search
Find issues within a radius:
```bash
curl "http://localhost:8001/api/issues?lat=40.7128&lon=-74.0060&radius=5000"
```
This finds all issues within 5000 meters (5km) of the location.

### Voting System
- First vote: adds upvote or downvote
- Same vote again: removes vote (toggle off)
- Different vote: switches from upvote to downvote or vice versa

### Trust Score
Users earn trust score through engagement:
- Creating an issue: +5 points
- (Future) Verified reports: +10 points
- (Future) Helping resolve issues: +15 points

### Notifications
Automatic notifications are created for:
- Issue status changes (to reporter)
- New upvotes on your issue
- New comments on your issue
- Badge achievements
- Milestone thresholds

## Environment Variables

| Variable | Description | Default |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:postgres@localhost:5432/civiclens` |
| `JWT_SECRET_KEY` | Secret key for JWT tokens | (required) |
| `JWT_ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | `43200` (30 days) |
| `CORS_ORIGINS` | Allowed CORS origins | `*` |

## Security Best Practices

1. **Change JWT Secret**: Always use a strong, unique secret in production
2. **Use HTTPS**: Enable SSL/TLS in production
3. **Limit CORS**: Restrict `CORS_ORIGINS` to your frontend domain
4. **Rate Limiting**: Implement rate limiting for production
5. **Database Security**: Use strong database passwords
6. **Environment Files**: Never commit `.env` to version control

## Deployment

### Using Docker (recommended)

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y postgresql-client

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001"]
```

Build and run:
```bash
docker build -t civiclens-api .
docker run -p 8001:8001 --env-file .env civiclens-api
```

### Using Supervisor (production)

The backend is already configured to run with supervisor. Just restart:
```bash
sudo supervisorctl restart backend
```

## Troubleshooting

### Database Connection Error
```
sqlalchemy.exc.OperationalError: password authentication failed
```
**Solution**: Check PostgreSQL authentication in `/etc/postgresql/15/main/pg_hba.conf`

### PostGIS Extension Error
```
ERROR: could not open extension control file
```
**Solution**: Install PostGIS:
```bash
sudo apt-get install postgresql-15-postgis-3
```

### Port Already in Use
```
ERROR: [Errno 98] Address already in use
```
**Solution**: Kill process on port 8001:
```bash
sudo lsof -ti:8001 | xargs kill -9
```

## Performance Tips

1. **Database Indexes**: Already configured on frequently queried fields
2. **Connection Pooling**: SQLAlchemy handles this automatically
3. **Async Operations**: All database operations are async
4. **Pagination**: Use `skip` and `limit` parameters for large datasets
5. **Caching**: Consider Redis for frequent queries (future enhancement)

## Contributing

When adding new features:
1. Update models in `models.py`
2. Create schemas in `schemas.py`
3. Add routes in `server.py`
4. Update `API_DOCUMENTATION.md`
5. Write tests

## Future Enhancements

- [ ] Direct image upload (S3/CloudStorage)
- [ ] Email notifications
- [ ] WebSocket for real-time updates
- [ ] Advanced analytics dashboard
- [ ] Social login (OAuth)
- [ ] Mobile API optimizations
- [ ] Sustainability data layer
- [ ] Safety indicators
- [ ] Rate limiting
- [ ] API versioning

## License

Copyright © 2025 CivicLens. All rights reserved.

## Support

For issues or questions, please refer to the API documentation or contact the development team.
