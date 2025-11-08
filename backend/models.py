from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Enum, Text, Boolean
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from database import Base
from datetime import datetime, timezone
import enum
import uuid

class IssueStatus(str, enum.Enum):
    REPORTED = "Reported"
    UNDER_REVIEW = "Under Review"
    WORK_IN_PROGRESS = "Work in Progress"
    RESOLVED = "Resolved"

class NotificationType(str, enum.Enum):
    STATUS_UPDATE = "Status Updates"
    REACTION = "Reactions"
    BADGE = "Badges"
    MILESTONE = "Milestones"

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    avatar = Column(String, nullable=True)
    trust_score = Column(Integer, default=0)
    badges = Column(String, default="")  # Comma-separated badges
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    issues = relationship("Issue", back_populates="reporter", foreign_keys="Issue.reporter_id")
    comments = relationship("Comment", back_populates="user")
    votes = relationship("Vote", back_populates="user")
    notifications = relationship("Notification", back_populates="user")

class Issue(Base):
    __tablename__ = "issues"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String, nullable=False, index=True)
    subcategory = Column(String, nullable=True)
    location = Column(Geometry(geometry_type='POINT', srid=4326), nullable=False)  # PostGIS Point
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    area_name = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    reporter_id = Column(String, ForeignKey("users.id"), nullable=False)
    status = Column(Enum(IssueStatus), default=IssueStatus.REPORTED, index=True)
    upvotes = Column(Integer, default=0)
    downvotes = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    reporter = relationship("User", back_populates="issues", foreign_keys=[reporter_id])
    comments = relationship("Comment", back_populates="issue", cascade="all, delete-orphan")
    votes = relationship("Vote", back_populates="issue", cascade="all, delete-orphan")

class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    issue_id = Column(String, ForeignKey("issues.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    issue = relationship("Issue", back_populates="comments")
    user = relationship("User", back_populates="comments")

class Vote(Base):
    __tablename__ = "votes"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    issue_id = Column(String, ForeignKey("issues.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    vote_type = Column(String, nullable=False)  # "upvote" or "downvote"
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    issue = relationship("Issue", back_populates="votes")
    user = relationship("User", back_populates="votes")

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    notification_type = Column(Enum(NotificationType), nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User", back_populates="notifications")