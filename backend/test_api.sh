#!/bin/bash

# CivicLens API Test Script
# Tests all major endpoints

BASE_URL="http://localhost:8001/api"

echo "======================================"
echo "CivicLens API Test Suite"
echo "======================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Health Check
echo -e "${YELLOW}Test 1: Health Check${NC}"
HEALTH=$(curl -s "${BASE_URL}/health")
if echo "$HEALTH" | grep -q '"status":"healthy"'; then
    echo -e "${GREEN}✓ Health check passed${NC}"
else
    echo -e "${RED}✗ Health check failed${NC}"
    exit 1
fi
echo ""

# Test 2: Register User
echo -e "${YELLOW}Test 2: Register User${NC}"
RANDOM_USER="testuser_$$"
RANDOM_EMAIL="test_$$@example.com"

REGISTER_RESPONSE=$(curl -s -X POST "${BASE_URL}/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"username\": \"${RANDOM_USER}\",
    \"email\": \"${RANDOM_EMAIL}\",
    \"password\": \"password123\"
  }")

if echo "$REGISTER_RESPONSE" | grep -q '"access_token"'; then
    echo -e "${GREEN}✓ User registration successful${NC}"
    TOKEN=$(echo "$REGISTER_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
else
    echo -e "${RED}✗ User registration failed${NC}"
    echo "$REGISTER_RESPONSE"
    exit 1
fi
echo ""

# Test 3: Login
echo -e "${YELLOW}Test 3: Login${NC}"
LOGIN_RESPONSE=$(curl -s -X POST "${BASE_URL}/auth/login" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"${RANDOM_EMAIL}\",
    \"password\": \"password123\"
  }")

if echo "$LOGIN_RESPONSE" | grep -q '"access_token"'; then
    echo -e "${GREEN}✓ Login successful${NC}"
else
    echo -e "${RED}✗ Login failed${NC}"
    exit 1
fi
echo ""

# Test 4: Get Current User
echo -e "${YELLOW}Test 4: Get Current User${NC}"
CURRENT_USER=$(curl -s "${BASE_URL}/auth/me" \
  -H "Authorization: Bearer $TOKEN")

if echo "$CURRENT_USER" | grep -q "${RANDOM_USER}"; then
    echo -e "${GREEN}✓ Get current user successful${NC}"
else
    echo -e "${RED}✗ Get current user failed${NC}"
    exit 1
fi
echo ""

# Test 5: Create Issue
echo -e "${YELLOW}Test 5: Create Issue${NC}"
ISSUE_RESPONSE=$(curl -s -X POST "${BASE_URL}/issues" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "title": "Test Issue - Broken Street Light",
    "description": "This is a test issue created by the automated test script",
    "category": "Infrastructure",
    "subcategory": "Street Lighting",
    "latitude": 40.7128,
    "longitude": -74.0060,
    "area_name": "New York, NY",
    "image_url": "https://example.com/test-image.jpg"
  }')

if echo "$ISSUE_RESPONSE" | grep -q '"id"'; then
    echo -e "${GREEN}✓ Issue creation successful${NC}"
    ISSUE_ID=$(echo "$ISSUE_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
else
    echo -e "${RED}✗ Issue creation failed${NC}"
    echo "$ISSUE_RESPONSE"
    exit 1
fi
echo ""

# Test 6: List Issues
echo -e "${YELLOW}Test 6: List Issues${NC}"
ISSUES_LIST=$(curl -s "${BASE_URL}/issues")

if echo "$ISSUES_LIST" | grep -q "Test Issue"; then
    echo -e "${GREEN}✓ List issues successful${NC}"
else
    echo -e "${RED}✗ List issues failed${NC}"
    exit 1
fi
echo ""

# Test 7: Get Issue Details
echo -e "${YELLOW}Test 7: Get Issue Details${NC}"
ISSUE_DETAIL=$(curl -s "${BASE_URL}/issues/${ISSUE_ID}")

if echo "$ISSUE_DETAIL" | grep -q "${ISSUE_ID}"; then
    echo -e "${GREEN}✓ Get issue details successful${NC}"
else
    echo -e "${RED}✗ Get issue details failed${NC}"
    exit 1
fi
echo ""

# Test 8: Create Second User for Voting
echo -e "${YELLOW}Test 8: Create Second User${NC}"
RANDOM_USER2="testuser2_$$"
RANDOM_EMAIL2="test2_$$@example.com"

REGISTER2=$(curl -s -X POST "${BASE_URL}/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"username\": \"${RANDOM_USER2}\",
    \"email\": \"${RANDOM_EMAIL2}\",
    \"password\": \"password123\"
  }")

if echo "$REGISTER2" | grep -q '"access_token"'; then
    echo -e "${GREEN}✓ Second user created${NC}"
    TOKEN2=$(echo "$REGISTER2" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
else
    echo -e "${RED}✗ Second user creation failed${NC}"
    exit 1
fi
echo ""

# Test 9: Vote on Issue
echo -e "${YELLOW}Test 9: Vote on Issue${NC}"
VOTE_RESPONSE=$(curl -s -X POST "${BASE_URL}/issues/${ISSUE_ID}/vote" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN2" \
  -d '{"vote_type": "upvote"}')

if echo "$VOTE_RESPONSE" | grep -q '"upvotes":1'; then
    echo -e "${GREEN}✓ Voting successful${NC}"
else
    echo -e "${RED}✗ Voting failed${NC}"
    echo "$VOTE_RESPONSE"
    exit 1
fi
echo ""

# Test 10: Add Comment
echo -e "${YELLOW}Test 10: Add Comment${NC}"
COMMENT_RESPONSE=$(curl -s -X POST "${BASE_URL}/issues/${ISSUE_ID}/comments" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN2" \
  -d '{"text": "This is a test comment from the automated test script"}')

if echo "$COMMENT_RESPONSE" | grep -q '"text"'; then
    echo -e "${GREEN}✓ Comment creation successful${NC}"
else
    echo -e "${RED}✗ Comment creation failed${NC}"
    exit 1
fi
echo ""

# Test 11: Get Comments
echo -e "${YELLOW}Test 11: Get Comments${NC}"
COMMENTS=$(curl -s "${BASE_URL}/issues/${ISSUE_ID}/comments")

if echo "$COMMENTS" | grep -q "test comment"; then
    echo -e "${GREEN}✓ Get comments successful${NC}"
else
    echo -e "${RED}✗ Get comments failed${NC}"
    exit 1
fi
echo ""

# Test 12: Update Issue Status
echo -e "${YELLOW}Test 12: Update Issue Status${NC}"
STATUS_RESPONSE=$(curl -s -X PATCH "${BASE_URL}/issues/${ISSUE_ID}/status" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"status": "Under Review"}')

if echo "$STATUS_RESPONSE" | grep -q '"status":"Under Review"'; then
    echo -e "${GREEN}✓ Status update successful${NC}"
else
    echo -e "${RED}✗ Status update failed${NC}"
    exit 1
fi
echo ""

# Test 13: Get Notifications
echo -e "${YELLOW}Test 13: Get Notifications${NC}"
NOTIFICATIONS=$(curl -s "${BASE_URL}/notifications" \
  -H "Authorization: Bearer $TOKEN")

if echo "$NOTIFICATIONS" | grep -q '"notification_type"'; then
    NOTIF_COUNT=$(echo "$NOTIFICATIONS" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))")
    echo -e "${GREEN}✓ Get notifications successful (${NOTIF_COUNT} notifications)${NC}"
else
    echo -e "${RED}✗ Get notifications failed${NC}"
    exit 1
fi
echo ""

# Test 14: Get Leaderboard
echo -e "${YELLOW}Test 14: Get Leaderboard${NC}"
LEADERBOARD=$(curl -s "${BASE_URL}/leaderboard")

if echo "$LEADERBOARD" | grep -q "${RANDOM_USER}"; then
    echo -e "${GREEN}✓ Get leaderboard successful${NC}"
else
    echo -e "${RED}✗ Get leaderboard failed${NC}"
    exit 1
fi
echo ""

# Test 15: Geospatial Query
echo -e "${YELLOW}Test 15: Geospatial Query (nearby issues)${NC}"
GEO_ISSUES=$(curl -s "${BASE_URL}/issues?lat=40.7128&lon=-74.0060&radius=10000")

if echo "$GEO_ISSUES" | grep -q "Test Issue"; then
    echo -e "${GREEN}✓ Geospatial query successful${NC}"
else
    echo -e "${RED}✗ Geospatial query failed${NC}"
    exit 1
fi
echo ""

# Test 16: Filter Issues by Category
echo -e "${YELLOW}Test 16: Filter Issues by Category${NC}"
FILTERED_ISSUES=$(curl -s "${BASE_URL}/issues?category=Infrastructure")

if echo "$FILTERED_ISSUES" | grep -q "Infrastructure"; then
    echo -e "${GREEN}✓ Category filter successful${NC}"
else
    echo -e "${RED}✗ Category filter failed${NC}"
    exit 1
fi
echo ""

# Summary
echo "======================================"
echo -e "${GREEN}All Tests Passed! ✓${NC}"
echo "======================================"
echo ""
echo "Test Summary:"
echo "- Health check: ✓"
echo "- User registration: ✓"
echo "- User login: ✓"
echo "- Get current user: ✓"
echo "- Create issue: ✓"
echo "- List issues: ✓"
echo "- Get issue details: ✓"
echo "- Vote on issue: ✓"
echo "- Add comment: ✓"
echo "- Get comments: ✓"
echo "- Update issue status: ✓"
echo "- Get notifications: ✓"
echo "- Get leaderboard: ✓"
echo "- Geospatial query: ✓"
echo "- Filter by category: ✓"
echo ""
echo "Total Tests: 16"
echo "Passed: 16"
echo "Failed: 0"
echo ""