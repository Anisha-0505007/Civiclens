from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, text, or_, and_
from geoalchemy2.functions import ST_Distance, ST_GeogFromText, ST_SetSRID, ST_MakePoint
from typing import List, Optional
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Import local modules
from database import get_db, init_db
from models import User, Issue, Comment, Vote, Notification, IssueStatus, NotificationType
from schemas import (
    UserRegister, UserLogin, UserResponse, Token,
    IssueCreate, IssueUpdate, IssueStatusUpdate, IssueResponse,
    CommentCreate, CommentResponse,
    VoteCreate,
    NotificationResponse,
    LeaderboardEntry
)
from auth import (
    get_password_hash, verify_password, create_access_token, get_current_user
)

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Create the main app
app = FastAPI(title="CivicLens API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==================== Authentication Endpoints ====================

@api_router.post("/auth/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    existing_user = db.query(User).filter(
        or_(User.email == user_data.email, User.username == user_data.username)
    ).first()
    
    if existing_user:
        if existing_user.email == user_data.email:
            raise HTTPException(status_code=400, detail="Email already registered")
        else:
            raise HTTPException(status_code=400, detail="Username already taken")
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        avatar=f"https://api.dicebear.com/7.x/avataaars/svg?seed={user_data.username}"
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create access token
    access_token = create_access_token(data={"sub": new_user.id})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": new_user
    }

@api_router.post("/auth/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Login user"""
    user = db.query(User).filter(User.email == user_data.email).first()
    
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user.id})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@api_router.get("/auth/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user info"""
    return current_user

@api_router.post("/auth/logout")
def logout(current_user: User = Depends(get_current_user)):
    """Logout user (client should delete token)"""
    return {"message": "Successfully logged out"}

# ==================== Issue Endpoints ====================

@api_router.post("/issues", response_model=IssueResponse, status_code=status.HTTP_201_CREATED)
def create_issue(
    issue_data: IssueCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new issue"""
    # Check for duplicate issues nearby (within 100 meters with similar title)
    point = ST_SetSRID(ST_MakePoint(issue_data.longitude, issue_data.latitude), 4326)
    
    nearby_issues = db.query(Issue).filter(
        and_(
            func.lower(Issue.title).contains(issue_data.title.lower()[:20]),
            func.ST_DWithin(
                func.ST_Transform(Issue.location, 3857),
                func.ST_Transform(point, 3857),
                100  # 100 meters
            )
        )
    ).first()
    
    if nearby_issues:
        raise HTTPException(
            status_code=400,
            detail="A similar issue already exists nearby. Please check existing reports."
        )
    
    # Create new issue
    new_issue = Issue(
        title=issue_data.title,
        description=issue_data.description,
        category=issue_data.category,
        subcategory=issue_data.subcategory,
        latitude=issue_data.latitude,
        longitude=issue_data.longitude,
        location=f"POINT({issue_data.longitude} {issue_data.latitude})",
        area_name=issue_data.area_name,
        image_url=issue_data.image_url,
        reporter_id=current_user.id
    )
    
    db.add(new_issue)
    
    # Update user trust score for creating issue
    current_user.trust_score += 5
    
    db.commit()
    db.refresh(new_issue)
    
    # Load reporter relationship
    db.refresh(new_issue, ['reporter'])
    
    return new_issue

@api_router.get("/issues", response_model=List[IssueResponse])
def list_issues(
    category: Optional[str] = None,
    city: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    radius: Optional[float] = Query(None, description="Radius in meters"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List issues with optional filters"""
    query = db.query(Issue)
    
    # Apply filters
    if category:
        query = query.filter(Issue.category == category)
    
    if city:
        query = query.filter(Issue.area_name.ilike(f"%{city}%"))
    
    if status_filter:
        try:
            status_enum = IssueStatus(status_filter)
            query = query.filter(Issue.status == status_enum)
        except ValueError:
            pass
    
    # Geospatial filter
    if lat is not None and lon is not None and radius is not None:
        point = ST_SetSRID(ST_MakePoint(lon, lat), 4326)
        query = query.filter(
            func.ST_DWithin(
                func.ST_Transform(Issue.location, 3857),
                func.ST_Transform(point, 3857),
                radius
            )
        )
    
    # Order by created_at descending
    query = query.order_by(Issue.created_at.desc())
    
    issues = query.offset(skip).limit(limit).all()
    
    # Load reporter relationship for all issues
    for issue in issues:
        db.refresh(issue, ['reporter'])
    
    return issues

@api_router.get("/issues/{issue_id}", response_model=IssueResponse)
def get_issue(issue_id: str, db: Session = Depends(get_db)):
    """Get issue details"""
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    # Load reporter relationship
    db.refresh(issue, ['reporter'])
    
    return issue

@api_router.patch("/issues/{issue_id}/status", response_model=IssueResponse)
def update_issue_status(
    issue_id: str,
    status_data: IssueStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update issue status"""
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    old_status = issue.status
    issue.status = status_data.status
    
    # Create notification for issue reporter
    notification = Notification(
        user_id=issue.reporter_id,
        notification_type=NotificationType.STATUS_UPDATE,
        title="Issue Status Updated",
        message=f"Your issue '{issue.title}' status changed from {old_status.value} to {status_data.status.value}"
    )
    db.add(notification)
    
    db.commit()
    db.refresh(issue)
    db.refresh(issue, ['reporter'])
    
    return issue

@api_router.post("/issues/{issue_id}/vote")
def vote_issue(
    issue_id: str,
    vote_data: VoteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Vote on an issue (upvote or downvote)"""
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    # Check if user already voted
    existing_vote = db.query(Vote).filter(
        and_(Vote.issue_id == issue_id, Vote.user_id == current_user.id)
    ).first()
    
    if existing_vote:
        # Update existing vote
        old_vote_type = existing_vote.vote_type
        
        if old_vote_type == vote_data.vote_type:
            # Remove vote if same type
            if vote_data.vote_type == "upvote":
                issue.upvotes = max(0, issue.upvotes - 1)
            else:
                issue.downvotes = max(0, issue.downvotes - 1)
            db.delete(existing_vote)
        else:
            # Switch vote type
            if old_vote_type == "upvote":
                issue.upvotes = max(0, issue.upvotes - 1)
                issue.downvotes += 1
            else:
                issue.downvotes = max(0, issue.downvotes - 1)
                issue.upvotes += 1
            existing_vote.vote_type = vote_data.vote_type
    else:
        # Create new vote
        new_vote = Vote(
            issue_id=issue_id,
            user_id=current_user.id,
            vote_type=vote_data.vote_type
        )
        db.add(new_vote)
        
        if vote_data.vote_type == "upvote":
            issue.upvotes += 1
        else:
            issue.downvotes += 1
        
        # Create notification for issue reporter (only for upvotes)
        if vote_data.vote_type == "upvote" and issue.reporter_id != current_user.id:
            notification = Notification(
                user_id=issue.reporter_id,
                notification_type=NotificationType.REACTION,
                title="New Upvote",
                message=f"{current_user.username} upvoted your issue '{issue.title}'"
            )
            db.add(notification)
    
    db.commit()
    
    return {
        "message": "Vote recorded",
        "upvotes": issue.upvotes,
        "downvotes": issue.downvotes
    }

# ==================== Comment Endpoints ====================

@api_router.post("/issues/{issue_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
    issue_id: str,
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a comment to an issue"""
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    new_comment = Comment(
        issue_id=issue_id,
        user_id=current_user.id,
        text=comment_data.text
    )
    
    db.add(new_comment)
    
    # Create notification for issue reporter
    if issue.reporter_id != current_user.id:
        notification = Notification(
            user_id=issue.reporter_id,
            notification_type=NotificationType.REACTION,
            title="New Comment",
            message=f"{current_user.username} commented on your issue '{issue.title}'"
        )
        db.add(notification)
    
    db.commit()
    db.refresh(new_comment)
    db.refresh(new_comment, ['user'])
    
    return new_comment

@api_router.get("/issues/{issue_id}/comments", response_model=List[CommentResponse])
def get_comments(
    issue_id: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get comments for an issue"""
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    comments = db.query(Comment).filter(
        Comment.issue_id == issue_id
    ).order_by(Comment.created_at.asc()).offset(skip).limit(limit).all()
    
    # Load user relationship for all comments
    for comment in comments:
        db.refresh(comment, ['user'])
    
    return comments

# ==================== Notification Endpoints ====================

@api_router.get("/notifications", response_model=List[NotificationResponse])
def get_notifications(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get notifications for current user"""
    notifications = db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()
    
    return notifications

@api_router.patch("/notifications/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a notification as read"""
    notification = db.query(Notification).filter(
        and_(
            Notification.id == notification_id,
            Notification.user_id == current_user.id
        )
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notification.is_read = True
    db.commit()
    db.refresh(notification)
    
    return notification

@api_router.delete("/notifications/clear")
def clear_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Clear all notifications for current user"""
    db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).delete()
    db.commit()
    
    return {"message": "All notifications cleared"}

# ==================== Leaderboard Endpoint ====================

@api_router.get("/leaderboard", response_model=List[LeaderboardEntry])
def get_leaderboard(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get leaderboard based on verified issues and upvotes"""
    # Query users with their issue count and total upvotes
    leaderboard = db.query(
        User.id.label('user_id'),
        User.username,
        User.avatar,
        User.trust_score,
        User.badges,
        func.count(Issue.id).label('total_issues'),
        func.coalesce(func.sum(Issue.upvotes), 0).label('total_upvotes')
    ).outerjoin(Issue, User.id == Issue.reporter_id).group_by(
        User.id
    ).order_by(
        func.coalesce(func.sum(Issue.upvotes), 0).desc(),
        func.count(Issue.id).desc()
    ).limit(limit).all()
    
    return [
        LeaderboardEntry(
            user_id=entry.user_id,
            username=entry.username,
            avatar=entry.avatar,
            trust_score=entry.trust_score,
            badges=entry.badges,
            total_issues=entry.total_issues,
            total_upvotes=entry.total_upvotes
        )
        for entry in leaderboard
    ]

# ==================== Health Check ====================

@api_router.get("/")
def root():
    return {"message": "CivicLens API", "version": "1.0.0", "status": "operational"}

@api_router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")

# Include the router in the main app
app.include_router(api_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    logger.info("Initializing database...")
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise