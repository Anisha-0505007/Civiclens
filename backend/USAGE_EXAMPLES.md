# CivicLens API Usage Examples

This document provides practical examples for using the CivicLens API.

## Quick Start Example

### Complete Flow: Register → Create Issue → Vote → Comment

```bash
#!/bin/bash

BASE_URL="http://localhost:8001/api"

# 1. Register a new user
echo "Registering user..."
REGISTER_RESPONSE=$(curl -s -X POST "${BASE_URL}/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securepass123"
  }')

# Extract token
TOKEN=$(echo "$REGISTER_RESPONSE" | jq -r '.access_token')
echo "Token: $TOKEN"

# 2. Create a civic issue
echo "Creating issue..."
ISSUE_RESPONSE=$(curl -s -X POST "${BASE_URL}/issues" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "title": "Broken Sidewalk on Oak Street",
    "description": "There is a large crack in the sidewalk that poses a tripping hazard",
    "category": "Infrastructure",
    "subcategory": "Sidewalks",
    "latitude": 40.7580,
    "longitude": -73.9855,
    "area_name": "Manhattan, New York",
    "image_url": "https://example.com/photos/sidewalk-crack.jpg"
  }')

ISSUE_ID=$(echo "$ISSUE_RESPONSE" | jq -r '.id')
echo "Issue created: $ISSUE_ID"

# 3. Register another user to vote
echo "Registering second user..."
REGISTER2=$(curl -s -X POST "${BASE_URL}/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "jane_smith",
    "email": "jane@example.com",
    "password": "securepass456"
  }')

TOKEN2=$(echo "$REGISTER2" | jq -r '.access_token')

# 4. Vote on the issue
echo "Voting on issue..."
curl -s -X POST "${BASE_URL}/issues/${ISSUE_ID}/vote" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN2" \
  -d '{"vote_type": "upvote"}'

# 5. Add a comment
echo "Adding comment..."
curl -s -X POST "${BASE_URL}/issues/${ISSUE_ID}/comments" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN2" \
  -d '{"text": "I noticed this too. It needs to be fixed soon!"}'

# 6. Check notifications
echo "Checking notifications for original user..."
curl -s "${BASE_URL}/notifications" \
  -H "Authorization: Bearer $TOKEN" | jq '.'

echo "Complete!"
```

---

## Common Use Cases

### 1. Finding Nearby Issues

Find all issues within 5km of a location:

```bash
curl -G "${BASE_URL}/issues" \
  --data-urlencode "lat=40.7128" \
  --data-urlencode "lon=-74.0060" \
  --data-urlencode "radius=5000"
```

Find issues in a specific city:

```bash
curl -G "${BASE_URL}/issues" \
  --data-urlencode "city=New York"
```

---

### 2. Filter Issues by Status

Get all reported issues:

```bash
curl -G "${BASE_URL}/issues" \
  --data-urlencode "status=Reported"
```

Get issues under review:

```bash
curl -G "${BASE_URL}/issues" \
  --data-urlencode "status=Under Review"
```

---

### 3. Filter by Category

Get all infrastructure issues:

```bash
curl -G "${BASE_URL}/issues" \
  --data-urlencode "category=Infrastructure"
```

---

### 4. Combined Filters

Get infrastructure issues in New York that are under review:

```bash
curl -G "${BASE_URL}/issues" \
  --data-urlencode "category=Infrastructure" \
  --data-urlencode "city=New York" \
  --data-urlencode "status=Under Review"
```

---

### 5. Update Issue Status Workflow

```bash
# Get token
TOKEN="your-token-here"
ISSUE_ID="issue-uuid-here"

# Move to Under Review
curl -X PATCH "${BASE_URL}/issues/${ISSUE_ID}/status" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"status": "Under Review"}'

# Move to Work in Progress
curl -X PATCH "${BASE_URL}/issues/${ISSUE_ID}/status" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"status": "Work in Progress"}'

# Mark as Resolved
curl -X PATCH "${BASE_URL}/issues/${ISSUE_ID}/status" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"status": "Resolved"}'
```

---

### 6. Managing Notifications

Get all notifications:

```bash
curl "${BASE_URL}/notifications" \
  -H "Authorization: Bearer $TOKEN"
```

Mark a notification as read:

```bash
NOTIF_ID="notification-uuid"
curl -X PATCH "${BASE_URL}/notifications/${NOTIF_ID}/read" \
  -H "Authorization: Bearer $TOKEN"
```

Clear all notifications:

```bash
curl -X DELETE "${BASE_URL}/notifications/clear" \
  -H "Authorization: Bearer $TOKEN"
```

---

### 7. View Leaderboard

Top 10 users:

```bash
curl "${BASE_URL}/leaderboard"
```

Top 20 users:

```bash
curl "${BASE_URL}/leaderboard?limit=20"
```

---

## Python Examples

### Using `requests` library

```python
import requests

BASE_URL = "http://localhost:8001/api"

# 1. Register and login
def register_user(username, email, password):
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password
        }
    )
    return response.json()

def login_user(email, password):
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": email,
            "password": password
        }
    )
    return response.json()

# 2. Create issue
def create_issue(token, title, description, category, lat, lon, area_name):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{BASE_URL}/issues",
        json={
            "title": title,
            "description": description,
            "category": category,
            "latitude": lat,
            "longitude": lon,
            "area_name": area_name
        },
        headers=headers
    )
    return response.json()

# 3. List issues with filters
def list_issues(category=None, city=None, status=None, lat=None, lon=None, radius=None):
    params = {}
    if category:
        params['category'] = category
    if city:
        params['city'] = city
    if status:
        params['status'] = status
    if lat and lon and radius:
        params.update({'lat': lat, 'lon': lon, 'radius': radius})
    
    response = requests.get(f"{BASE_URL}/issues", params=params)
    return response.json()

# 4. Vote on issue
def vote_issue(token, issue_id, vote_type):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{BASE_URL}/issues/{issue_id}/vote",
        json={"vote_type": vote_type},
        headers=headers
    )
    return response.json()

# 5. Add comment
def add_comment(token, issue_id, text):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{BASE_URL}/issues/{issue_id}/comments",
        json={"text": text},
        headers=headers
    )
    return response.json()

# Usage example
if __name__ == "__main__":
    # Register
    user_data = register_user("alice", "alice@example.com", "password123")
    token = user_data['access_token']
    print(f"Registered user: {user_data['user']['username']}")
    
    # Create issue
    issue = create_issue(
        token,
        "Pothole on Main Street",
        "Large pothole causing damage to vehicles",
        "Road Maintenance",
        40.7128,
        -74.0060,
        "New York, NY"
    )
    print(f"Created issue: {issue['id']}")
    
    # List nearby issues
    nearby_issues = list_issues(lat=40.7128, lon=-74.0060, radius=10000)
    print(f"Found {len(nearby_issues)} issues nearby")
    
    # Vote
    vote_result = vote_issue(token, issue['id'], "upvote")
    print(f"Vote result: {vote_result}")
```

---

## JavaScript/Node.js Examples

### Using `axios`

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:8001/api';

// Register user
async function registerUser(username, email, password) {
  const response = await axios.post(`${BASE_URL}/auth/register`, {
    username,
    email,
    password
  });
  return response.data;
}

// Login user
async function loginUser(email, password) {
  const response = await axios.post(`${BASE_URL}/auth/login`, {
    email,
    password
  });
  return response.data;
}

// Create issue
async function createIssue(token, issueData) {
  const response = await axios.post(`${BASE_URL}/issues`, issueData, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  return response.data;
}

// List issues with filters
async function listIssues(filters = {}) {
  const response = await axios.get(`${BASE_URL}/issues`, {
    params: filters
  });
  return response.data;
}

// Vote on issue
async function voteIssue(token, issueId, voteType) {
  const response = await axios.post(
    `${BASE_URL}/issues/${issueId}/vote`,
    { vote_type: voteType },
    {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  );
  return response.data;
}

// Get notifications
async function getNotifications(token) {
  const response = await axios.get(`${BASE_URL}/notifications`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  return response.data;
}

// Usage example
async function main() {
  try {
    // Register and login
    const userData = await registerUser('bob', 'bob@example.com', 'password123');
    const token = userData.access_token;
    console.log('Registered:', userData.user.username);
    
    // Create issue
    const issue = await createIssue(token, {
      title: 'Graffiti on Public Building',
      description: 'Extensive graffiti needs cleanup',
      category: 'Vandalism',
      latitude: 40.7489,
      longitude: -73.9680,
      area_name: 'Queens, NY'
    });
    console.log('Created issue:', issue.id);
    
    // List issues
    const issues = await listIssues({ category: 'Vandalism' });
    console.log(`Found ${issues.length} vandalism issues`);
    
    // Get notifications
    const notifications = await getNotifications(token);
    console.log(`You have ${notifications.length} notifications`);
    
  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
  }
}

main();
```

---

## Frontend Integration Examples

### React Hook Example

```javascript
import { useState, useEffect } from 'react';
import axios from 'axios';

const BASE_URL = 'http://localhost:8001/api';

// Custom hook for CivicLens API
export function useCivicLens() {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [user, setUser] = useState(null);

  // Set up axios interceptor
  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    }
  }, [token]);

  const register = async (username, email, password) => {
    const response = await axios.post(`${BASE_URL}/auth/register`, {
      username,
      email,
      password
    });
    setToken(response.data.access_token);
    setUser(response.data.user);
    localStorage.setItem('token', response.data.access_token);
    return response.data;
  };

  const login = async (email, password) => {
    const response = await axios.post(`${BASE_URL}/auth/login`, {
      email,
      password
    });
    setToken(response.data.access_token);
    setUser(response.data.user);
    localStorage.setItem('token', response.data.access_token);
    return response.data;
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['Authorization'];
  };

  const createIssue = async (issueData) => {
    const response = await axios.post(`${BASE_URL}/issues`, issueData);
    return response.data;
  };

  const getIssues = async (filters = {}) => {
    const response = await axios.get(`${BASE_URL}/issues`, { params: filters });
    return response.data;
  };

  const voteIssue = async (issueId, voteType) => {
    const response = await axios.post(`${BASE_URL}/issues/${issueId}/vote`, {
      vote_type: voteType
    });
    return response.data;
  };

  const addComment = async (issueId, text) => {
    const response = await axios.post(`${BASE_URL}/issues/${issueId}/comments`, {
      text
    });
    return response.data;
  };

  const getNotifications = async () => {
    const response = await axios.get(`${BASE_URL}/notifications`);
    return response.data;
  };

  return {
    token,
    user,
    register,
    login,
    logout,
    createIssue,
    getIssues,
    voteIssue,
    addComment,
    getNotifications
  };
}

// Usage in component
function IssueList() {
  const { getIssues, voteIssue } = useCivicLens();
  const [issues, setIssues] = useState([]);

  useEffect(() => {
    loadIssues();
  }, []);

  const loadIssues = async () => {
    const data = await getIssues({ status: 'Reported' });
    setIssues(data);
  };

  const handleVote = async (issueId) => {
    await voteIssue(issueId, 'upvote');
    loadIssues(); // Refresh list
  };

  return (
    <div>
      {issues.map(issue => (
        <div key={issue.id}>
          <h3>{issue.title}</h3>
          <p>{issue.description}</p>
          <button onClick={() => handleVote(issue.id)}>
            Upvote ({issue.upvotes})
          </button>
        </div>
      ))}
    </div>
  );
}
```

---

## Advanced Geospatial Queries

### Find Issues Near User's Location

```javascript
// Get user's current location
navigator.geolocation.getCurrentPosition(async (position) => {
  const { latitude, longitude } = position.coords;
  
  // Find issues within 2km
  const nearbyIssues = await axios.get(`${BASE_URL}/issues`, {
    params: {
      lat: latitude,
      lon: longitude,
      radius: 2000  // 2km in meters
    }
  });
  
  console.log(`Found ${nearbyIssues.data.length} issues near you`);
});
```

### Prevent Duplicate Issue Submission

```javascript
// Check before submitting
async function submitIssue(issueData) {
  try {
    const response = await axios.post(`${BASE_URL}/issues`, issueData, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    console.log('Issue created successfully');
    return response.data;
  } catch (error) {
    if (error.response?.status === 400) {
      // Duplicate detected
      alert('A similar issue already exists nearby. Please check existing reports.');
    } else {
      alert('Error creating issue');
    }
    throw error;
  }
}
```

---

## Pagination Example

```javascript
// Load issues with pagination
async function loadIssuesPaginated(page = 0, pageSize = 20) {
  const response = await axios.get(`${BASE_URL}/issues`, {
    params: {
      skip: page * pageSize,
      limit: pageSize
    }
  });
  return response.data;
}

// Load first page
const page1 = await loadIssuesPaginated(0, 20);

// Load second page
const page2 = await loadIssuesPaginated(1, 20);
```

---

## Error Handling Best Practices

```javascript
async function safeApiCall(apiFunction) {
  try {
    return await apiFunction();
  } catch (error) {
    if (error.response) {
      // Server responded with error
      switch (error.response.status) {
        case 401:
          console.error('Unauthorized - please login');
          // Redirect to login
          break;
        case 404:
          console.error('Resource not found');
          break;
        case 422:
          console.error('Validation error:', error.response.data.detail);
          break;
        default:
          console.error('Server error:', error.response.data);
      }
    } else if (error.request) {
      // Request made but no response
      console.error('Network error - server not responding');
    } else {
      // Error in request setup
      console.error('Error:', error.message);
    }
    throw error;
  }
}

// Usage
await safeApiCall(async () => {
  return await createIssue(token, issueData);
});
```

---

## Monitoring and Analytics

### Track User Engagement

```javascript
// Get user stats
async function getUserStats(userId) {
  const leaderboard = await axios.get(`${BASE_URL}/leaderboard`);
  const userEntry = leaderboard.data.find(entry => entry.user_id === userId);
  
  return {
    totalIssues: userEntry.total_issues,
    totalUpvotes: userEntry.total_upvotes,
    trustScore: userEntry.trust_score,
    badges: userEntry.badges.split(',').filter(b => b)
  };
}
```

### Issue Analytics

```javascript
// Get issue statistics
async function getIssueStats() {
  const allIssues = await axios.get(`${BASE_URL}/issues`);
  
  const stats = {
    total: allIssues.data.length,
    byStatus: {},
    byCategory: {},
    totalUpvotes: 0,
    totalComments: 0
  };
  
  for (const issue of allIssues.data) {
    // By status
    stats.byStatus[issue.status] = (stats.byStatus[issue.status] || 0) + 1;
    
    // By category
    stats.byCategory[issue.category] = (stats.byCategory[issue.category] || 0) + 1;
    
    // Total upvotes
    stats.totalUpvotes += issue.upvotes;
  }
  
  return stats;
}
```

---

## WebSocket Integration (Future)

While the current API doesn't support WebSockets, here's how you could implement real-time notifications in the future:

```javascript
// Pseudo-code for WebSocket integration
const ws = new WebSocket('ws://localhost:8001/ws/notifications');

ws.onopen = () => {
  // Send authentication
  ws.send(JSON.stringify({
    type: 'auth',
    token: token
  }));
};

ws.onmessage = (event) => {
  const notification = JSON.parse(event.data);
  // Display notification to user
  showNotification(notification);
};
```

---

## Testing Tips

1. **Use a test user**: Always use test credentials for development
2. **Clean up**: Delete test issues after testing
3. **Mock location**: Use fixed coordinates for testing geospatial features
4. **Rate limiting**: Be mindful of API rate limits (implement in future)
5. **Error scenarios**: Test edge cases (invalid data, missing fields, etc.)

---

## Production Checklist

Before deploying to production:

- [ ] Change JWT_SECRET_KEY to a strong random value
- [ ] Enable HTTPS/SSL
- [ ] Configure CORS_ORIGINS to only allow your frontend domain
- [ ] Set up database backups
- [ ] Implement rate limiting
- [ ] Set up monitoring and logging
- [ ] Configure environment-specific settings
- [ ] Test all endpoints thoroughly
- [ ] Set up CI/CD pipeline
- [ ] Document API for your team

---

For more information, see:
- [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) - Complete API reference
- [README.md](./README.md) - Setup and installation guide
