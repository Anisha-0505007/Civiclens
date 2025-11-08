from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime
from models import IssueStatus, NotificationType
import re

# User Schemas
class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    
    @field_validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username can only contain letters, numbers, underscores and hyphens')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    avatar: Optional[str] = None
    trust_score: int
    badges: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# Issue Schemas
class IssueCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=10)
    category: str
    subcategory: Optional[str] = None
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    area_name: Optional[str] = None
    image_url: Optional[str] = None
    
    @field_validator('title', 'description')
    def sanitize_text(cls, v):
        # Remove any HTML tags for basic sanitization
        return re.sub(r'<[^>]+>', '', v).strip()

class IssueUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=200)
    description: Optional[str] = Field(None, min_length=10)
    category: Optional[str] = None
    subcategory: Optional[str] = None
    area_name: Optional[str] = None
    image_url: Optional[str] = None

class IssueStatusUpdate(BaseModel):
    status: IssueStatus

class IssueResponse(BaseModel):
    id: str
    title: str
    description: str
    category: str
    subcategory: Optional[str] = None
    latitude: float
    longitude: float
    area_name: Optional[str] = None
    image_url: Optional[str] = None
    reporter_id: str
    status: str
    upvotes: int
    downvotes: int
    created_at: datetime
    updated_at: datetime
    reporter: Optional[UserResponse] = None
    
    class Config:
        from_attributes = True

# Comment Schemas
class CommentCreate(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000)
    
    @field_validator('text')
    def sanitize_text(cls, v):
        return re.sub(r'<[^>]+>', '', v).strip()

class CommentResponse(BaseModel):
    id: str
    issue_id: str
    user_id: str
    text: str
    created_at: datetime
    user: Optional[UserResponse] = None
    
    class Config:
        from_attributes = True

# Vote Schema
class VoteCreate(BaseModel):
    vote_type: str = Field(..., pattern="^(upvote|downvote)$")

# Notification Schemas
class NotificationResponse(BaseModel):
    id: str
    user_id: str
    notification_type: str
    title: str
    message: str
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Leaderboard Schema
class LeaderboardEntry(BaseModel):
    user_id: str
    username: str
    avatar: Optional[str] = None
    trust_score: int
    badges: str
    total_issues: int
    total_upvotes: int
    
    class Config:
        from_attributes = True