"""
Social Features Models
=====================
Posts, comments, likes, follows
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Content
    caption = Column(Text, nullable=True)
    image_url = Column(String, nullable=False)
    
    # Links to other content
    tryon_id = Column(Integer, ForeignKey("tryon_history.id"), nullable=True)
    outfit_id = Column(Integer, ForeignKey("outfits.id"), nullable=True)
    
    # Tags
    tags = Column(String, nullable=True)  # Comma-separated hashtags
    
    # Stats
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    
    # Status
    is_public = Column(Boolean, default=True, index=True)
    is_featured = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="post", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Post {self.id} by User {self.user_id}>"


class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Content
    text = Column(Text, nullable=False)
    
    # Nested comments (replies)
    parent_comment_id = Column(Integer, ForeignKey("comments.id"), nullable=True)
    
    # Stats
    like_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    post = relationship("Post", back_populates="comments")
    user = relationship("User")
    replies = relationship("Comment", backref="parent", remote_side=[id])
    
    def __repr__(self):
        return f"<Comment {self.id} on Post {self.post_id}>"


class Like(Base):
    __tablename__ = "likes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # What is liked
    item_type = Column(String, nullable=False, index=True)  # post, comment, tryon, outfit
    item_id = Column(Integer, nullable=False, index=True)
    
    # For posts specifically
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    post = relationship("Post", back_populates="likes")
    user = relationship("User")
    
    def __repr__(self):
        return f"<Like {self.item_type} {self.item_id} by User {self.user_id}>"


class Follow(Base):
    __tablename__ = "follows"
    
    id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    followed_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    follower = relationship("User", foreign_keys=[follower_id], back_populates="following")
    followed = relationship("User", foreign_keys=[followed_id], back_populates="followers")
    
    def __repr__(self):
        return f"<Follow {self.follower_id} -> {self.followed_id}>"
