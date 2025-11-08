# CivicLens API Documentation

## Overview
CivicLens is a backend API for civic issue reporting and management. Built with FastAPI, PostgreSQL with PostGIS extension for geospatial data support.

**Base URL**: `/api`

---

## Authentication

All protected endpoints require JWT Bearer token authentication.

### Register User
**POST** `/auth/register`

Register a new user account.

**Request Body**:
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "password123"
}
```

**Response** (201 Created):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "uuid-here",
    "username": "johndoe",
    "email": "john@example.com",
    "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=johndoe",
    "trust_score": 0,
    "badges": "",
    "created_at": "2025-01-08T12:00:00Z"
  }
}
```

**Errors**:
- `400`: Email already registered or username already taken
- `422`: Validation error (invalid email, password too short, etc.)

---

### Login User
**POST** `/auth/login`

Authenticate and get access token.

**Request Body**:
```json
{
  "email": "john@example.com",
  "password": "password123"
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "uuid-here",
    "username": "johndoe",
    "email": "john@example.com",
    "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=johndoe",
    "trust_score": 0,
    "badges": "",
    "created_at": "2025-01-08T12:00:00Z"
  }
}
```

**Errors**:
- `401`: Incorrect email or password

---

### Get Current User
**GET** `/auth/me`

Get current authenticated user information.

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):
```json
{
  "id": "uuid-here",
  "username": "johndoe",
  "email": "john@example.com",
  "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=johndoe",
  "trust_score": 5,
  "badges": "",
  "created_at": "2025-01-08T12:00:00Z"
}
```

---

### Logout User
**POST** `/auth/logout`

Logout user (client should delete token).

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):
```json
{
  "message": "Successfully logged out"
}
```

---

## Issues

### Create Issue
**POST** `/issues`

Create a new civic issue report.

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "title": "Broken Street Light on Main Street",
  "description": "The street light at the corner of Main Street and 5th Avenue has been broken for a week",
  "category": "Infrastructure",
  "subcategory": "Street Lighting",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "area_name": "New York, NY",
  "image_url": "https://example.com/images/broken-light.jpg"
}
```

**Response** (201 Created):
```json
{
  "id": "uuid-here",
  "title": "Broken Street Light on Main Street",
  "description": "The street light at the corner...",
  "category": "Infrastructure",
  "subcategory": "Street Lighting",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "area_name": "New York, NY",
  "image_url": "https://example.com/images/broken-light.jpg",
  "reporter_id": "user-uuid",
  "status": "Reported",
  "upvotes": 0,
  "downvotes": 0,
  "created_at": "2025-01-08T12:00:00Z",
  "updated_at": "2025-01-08T12:00:00Z",
  "reporter": {
    "id": "user-uuid",
    "username": "johndoe",
    "email": "john@example.com",
    "avatar": "...",
    "trust_score": 5,
    "badges": "",
    "created_at": "2025-01-08T12:00:00Z"
  }
}
```

**Features**:
- Automatically detects duplicate issues within 100m with similar title
- Increases reporter's trust score by 5 points

**Errors**:
- `400`: Similar issue already exists nearby
- `401`: Unauthorized (no token)
- `422`: Validation error

---

### List Issues
**GET** `/issues`

List all issues with optional filters.

**Query Parameters**:
- `category` (optional): Filter by category (e.g., "Infrastructure")
- `city` (optional): Filter by city name
- `status` (optional): Filter by status ("Reported", "Under Review", "Work in Progress", "Resolved")
- `lat` (optional): Latitude for geospatial filtering
- `lon` (optional): Longitude for geospatial filtering
- `radius` (optional): Radius in meters (requires lat and lon)
- `skip` (optional): Pagination offset (default: 0)
- `limit` (optional): Max results (default: 100)

**Examples**:
```
GET /api/issues?category=Infrastructure
GET /api/issues?status=Reported&city=New%20York
GET /api/issues?lat=40.7128&lon=-74.0060&radius=5000
```

**Response** (200 OK):
```json
[
  {
    "id": "uuid-here",
    "title": "Broken Street Light on Main Street",
    "description": "...",
    "category": "Infrastructure",
    "subcategory": "Street Lighting",
    "latitude": 40.7128,
    "longitude": -74.0060,
    "area_name": "New York, NY",
    "image_url": "...",
    "reporter_id": "user-uuid",
    "status": "Reported",
    "upvotes": 5,
    "downvotes": 1,
    "created_at": "2025-01-08T12:00:00Z",
    "updated_at": "2025-01-08T12:00:00Z",
    "reporter": { ... }
  }
]
```

---

### Get Issue Details
**GET** `/issues/{issue_id}`

Get detailed information about a specific issue.

**Response** (200 OK):
```json
{
  "id": "uuid-here",
  "title": "Broken Street Light on Main Street",
  "description": "...",
  "category": "Infrastructure",
  "subcategory": "Street Lighting",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "area_name": "New York, NY",
  "image_url": "...",
  "reporter_id": "user-uuid",
  "status": "Reported",
  "upvotes": 5,
  "downvotes": 1,
  "created_at": "2025-01-08T12:00:00Z",
  "updated_at": "2025-01-08T12:00:00Z",
  "reporter": { ... }
}
```

**Errors**:
- `404`: Issue not found

---

### Update Issue Status
**PATCH** `/issues/{issue_id}/status`

Update the status of an issue.

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "status": "Under Review"
}
```

**Valid Statuses**:
- `Reported`
- `Under Review`
- `Work in Progress`
- `Resolved`

**Response** (200 OK):
```json
{
  "id": "uuid-here",
  "title": "Broken Street Light on Main Street",
  "status": "Under Review",
  ...
}
```

**Features**:
- Automatically creates notification for issue reporter

**Errors**:
- `404`: Issue not found
- `401`: Unauthorized

---

### Vote on Issue
**POST** `/issues/{issue_id}/vote`

Upvote or downvote an issue.

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "vote_type": "upvote"
}
```

**Valid Vote Types**: `upvote`, `downvote`

**Response** (200 OK):
```json
{
  "message": "Vote recorded",
  "upvotes": 6,
  "downvotes": 1
}
```

**Features**:
- Toggles vote: voting same type again removes vote
- Switches vote: upvote → downvote or vice versa
- Creates notification for issue reporter (upvotes only)
- Cannot vote on own issue (no notification)

**Errors**:
- `404`: Issue not found
- `401`: Unauthorized
- `422`: Invalid vote type

---

## Comments

### Add Comment
**POST** `/issues/{issue_id}/comments`

Add a comment to an issue.

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "text": "I noticed this too! It has been very dark at night."
}
```

**Response** (201 Created):
```json
{
  "id": "comment-uuid",
  "issue_id": "issue-uuid",
  "user_id": "user-uuid",
  "text": "I noticed this too! It has been very dark at night.",
  "created_at": "2025-01-08T12:00:00Z",
  "user": {
    "id": "user-uuid",
    "username": "johndoe",
    "email": "john@example.com",
    "avatar": "...",
    "trust_score": 5,
    "badges": "",
    "created_at": "2025-01-08T12:00:00Z"
  }
}
```

**Features**:
- Text is sanitized (HTML tags removed)
- Creates notification for issue reporter

**Errors**:
- `404`: Issue not found
- `401`: Unauthorized
- `422`: Validation error (empty text, too long)

---

### Get Comments
**GET** `/issues/{issue_id}/comments`

Get all comments for an issue.

**Query Parameters**:
- `skip` (optional): Pagination offset (default: 0)
- `limit` (optional): Max results (default: 100)

**Response** (200 OK):
```json
[
  {
    "id": "comment-uuid",
    "issue_id": "issue-uuid",
    "user_id": "user-uuid",
    "text": "I noticed this too! It has been very dark at night.",
    "created_at": "2025-01-08T12:00:00Z",
    "user": {
      "id": "user-uuid",
      "username": "johndoe",
      ...
    }
  }
]
```

**Errors**:
- `404`: Issue not found

---

## Notifications

### Get Notifications
**GET** `/notifications`

Get notifications for current user.

**Headers**: `Authorization: Bearer <token>`

**Query Parameters**:
- `skip` (optional): Pagination offset (default: 0)
- `limit` (optional): Max results (default: 50)

**Response** (200 OK):
```json
[
  {
    "id": "notif-uuid",
    "user_id": "user-uuid",
    "notification_type": "Status Updates",
    "title": "Issue Status Updated",
    "message": "Your issue 'Broken Street Light' status changed from Reported to Under Review",
    "is_read": false,
    "created_at": "2025-01-08T12:00:00Z"
  },
  {
    "id": "notif-uuid-2",
    "user_id": "user-uuid",
    "notification_type": "Reactions",
    "title": "New Upvote",
    "message": "alice upvoted your issue 'Broken Street Light'",
    "is_read": false,
    "created_at": "2025-01-08T11:30:00Z"
  }
]
```

**Notification Types**:
- `Status Updates`: Issue status changes
- `Reactions`: Upvotes and comments
- `Badges`: Badge achievements
- `Milestones`: Milestone thresholds

**Errors**:
- `401`: Unauthorized

---

### Mark Notification as Read
**PATCH** `/notifications/{notification_id}/read`

Mark a specific notification as read.

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):
```json
{
  "id": "notif-uuid",
  "user_id": "user-uuid",
  "notification_type": "Status Updates",
  "title": "Issue Status Updated",
  "message": "Your issue 'Broken Street Light' status changed...",
  "is_read": true,
  "created_at": "2025-01-08T12:00:00Z"
}
```

**Errors**:
- `404`: Notification not found
- `401`: Unauthorized

---

### Clear All Notifications
**DELETE** `/notifications/clear`

Clear all notifications for current user.

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):
```json
{
  "message": "All notifications cleared"
}
```

**Errors**:
- `401`: Unauthorized

---

## Leaderboard

### Get Leaderboard
**GET** `/leaderboard`

Get top users based on verified issues and upvotes.

**Query Parameters**:
- `limit` (optional): Max results (default: 10)

**Response** (200 OK):
```json
[
  {
    "user_id": "user-uuid",
    "username": "johndoe",
    "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=johndoe",
    "trust_score": 25,
    "badges": "Verified Reporter",
    "total_issues": 5,
    "total_upvotes": 42
  },
  {
    "user_id": "user-uuid-2",
    "username": "alice",
    "avatar": "...",
    "trust_score": 15,
    "badges": "",
    "total_issues": 3,
    "total_upvotes": 28
  }
]
```

**Sorting**: Ordered by total upvotes (desc), then total issues (desc)

---

## Health Check

### Health Check
**GET** `/health`

Check API and database health.

**Response** (200 OK):
```json
{
  "status": "healthy",
  "database": "connected"
}
```

**Errors**:
- `503`: Service unavailable (database connection failed)

---

### Root Endpoint
**GET** `/`

Get API information.

**Response** (200 OK):
```json
{
  "message": "CivicLens API",
  "version": "1.0.0",
  "status": "operational"
}
```

---

## Error Handling

### Standard Error Response
```json
{
  "detail": "Error message here"
}
```

### Validation Error Response
```json
{
  "detail": [
    {
      "type": "string_pattern_mismatch",
      "loc": ["body", "vote_type"],
      "msg": "String should match pattern '^(upvote|downvote)$'",
      "input": "invalid",
      "ctx": {"pattern": "^(upvote|downvote)$"}
    }
  ]
}
```

### Common HTTP Status Codes
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `404`: Not Found
- `422`: Validation Error
- `503`: Service Unavailable

---

## Security Features

1. **JWT Authentication**: All protected endpoints require valid JWT tokens
2. **Password Hashing**: Passwords are hashed using bcrypt
3. **Input Sanitization**: HTML tags are stripped from user input
4. **Duplicate Prevention**: Geospatial checks prevent duplicate reports
5. **Token Expiration**: Access tokens expire after 30 days

---

## Geospatial Features

The API uses PostgreSQL with PostGIS extension for advanced geospatial queries:

1. **Duplicate Detection**: Checks for similar issues within 100 meters
2. **Radius Search**: Find issues within a specific radius (in meters)
3. **Location Data**: All issues stored with latitude, longitude, and PostGIS Point geometry

---

## Database Schema

### Users
- `id`: UUID (primary key)
- `username`: String (unique)
- `email`: String (unique)
- `hashed_password`: String
- `avatar`: String (URL)
- `trust_score`: Integer (default: 0)
- `badges`: String (comma-separated)
- `created_at`: DateTime

### Issues
- `id`: UUID (primary key)
- `title`: String
- `description`: Text
- `category`: String
- `subcategory`: String (nullable)
- `location`: PostGIS Point (SRID 4326)
- `latitude`: Float
- `longitude`: Float
- `area_name`: String (nullable)
- `image_url`: String (nullable)
- `reporter_id`: UUID (foreign key → users.id)
- `status`: Enum (Reported, Under Review, Work in Progress, Resolved)
- `upvotes`: Integer (default: 0)
- `downvotes`: Integer (default: 0)
- `created_at`: DateTime
- `updated_at`: DateTime

### Comments
- `id`: UUID (primary key)
- `issue_id`: UUID (foreign key → issues.id)
- `user_id`: UUID (foreign key → users.id)
- `text`: Text
- `created_at`: DateTime

### Votes
- `id`: UUID (primary key)
- `issue_id`: UUID (foreign key → issues.id)
- `user_id`: UUID (foreign key → users.id)
- `vote_type`: String ("upvote" or "downvote")
- `created_at`: DateTime

### Notifications
- `id`: UUID (primary key)
- `user_id`: UUID (foreign key → users.id)
- `notification_type`: Enum (Status Updates, Reactions, Badges, Milestones)
- `title`: String
- `message`: Text
- `is_read`: Boolean (default: false)
- `created_at`: DateTime

---

## Setup and Installation

### Prerequisites
- Python 3.11+
- PostgreSQL 15+ with PostGIS extension

### Installation Steps

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up PostgreSQL and PostGIS:
```bash
chmod +x init_postgres.sh
./init_postgres.sh
```

3. Configure environment variables in `.env`:
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/civiclens
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200
```

4. Run the server:
```bash
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

The API will be available at `http://localhost:8001/api`

---

## Testing

Run the test suite:
```bash
pytest tests/
```

---

## Future Enhancements

1. **Sustainability Data Layer**: Integration for sustainability reports
2. **Safety Indicators**: Add safety metrics and indicators
3. **Image Upload**: Direct image upload support (currently URL-only)
4. **Social Login**: OAuth integration (Google, Facebook)
5. **Real-time Updates**: WebSocket support for live notifications
6. **Advanced Analytics**: Dashboard with statistics and trends
7. **Email Notifications**: Send email alerts for important updates
8. **Mobile API**: Optimized endpoints for mobile apps

---

## License

Copyright © 2025 CivicLens. All rights reserved.
