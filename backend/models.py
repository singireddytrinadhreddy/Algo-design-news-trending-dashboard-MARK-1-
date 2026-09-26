from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, ForeignKey,
    UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
from backend.database import Base

class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    slug = Column(String(30), unique=True, nullable=False, index=True)
    display_name = Column(String(60), nullable=False)
    source_category = Column(String(1), nullable=False)  # 'A' = Direct API, 'B' = Derived Signal
    source_type_label = Column(String(40), nullable=False)  # 'Official API', 'Search Interest', 'News Coverage'
    icon_filename = Column(String(50), nullable=True)
    is_enabled = Column(Boolean, nullable=False, default=True)
    fetch_interval_min = Column(Integer, nullable=False, default=15)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    trending_items = relationship("TrendingItem", back_populates="source", cascade="all, delete-orphan")
    fetch_logs = relationship("FetchLog", back_populates="source", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Source(slug='{self.slug}', name='{self.display_name}', cat='{self.source_category}')>"


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    color = Column(String(7), nullable=True)

    # Relationships
    trending_items = relationship("TrendingItem", back_populates="category")

    def __repr__(self):
        return f"<Category(name='{self.name}', color='{self.color}')>"


class TrendingItem(Base):
    __tablename__ = "trending_items"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id", ondelete="CASCADE"), nullable=False, index=True)
    external_id = Column(String(128), nullable=False)
    title = Column(String(512), nullable=False)
    description = Column(Text, nullable=True)
    url = Column(String(2048), nullable=False)
    thumbnail_url = Column(String(2048), nullable=True)
    author = Column(String(256), nullable=True)
    engagement_value = Column(Integer, nullable=True)
    engagement_label = Column(String(32), nullable=True)
    secondary_value = Column(Integer, nullable=True)
    secondary_label = Column(String(32), nullable=True)
    rank = Column(Integer, nullable=True)
    region = Column(String(16), default="global")
    source_category = Column(String(1), nullable=False, index=True)  # Denormalized 'A' or 'B'
    published_at = Column(DateTime, nullable=True, index=True)
    fetched_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True)
    ai_summary = Column(Text, nullable=True)
    location_india = Column(String(128), nullable=True)
    ai_processed = Column(Boolean, nullable=False, default=False, index=True)
    raw_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    source = relationship("Source", back_populates="trending_items")
    category = relationship("Category", back_populates="trending_items")

    # Constraints & Indexes
    __table_args__ = (
        UniqueConstraint("source_id", "external_id", name="uq_source_external_id"),
        Index("idx_items_source_fetched", "source_id", "fetched_at"),
        Index("idx_items_source_category_fetched", "source_category", "fetched_at"),
    )

    def __repr__(self):
        return f"<TrendingItem(id={self.id}, source='{self.source.slug if self.source else self.source_id}', title='{self.title[:30]}...')>"


class FetchLog(Base):
    __tablename__ = "fetch_logs"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(20), nullable=False)  # 'success', 'error', 'skipped'
    items_fetched = Column(Integer, default=0, nullable=False)
    items_new = Column(Integer, default=0, nullable=False)
    error_message = Column(Text, nullable=True)
    duration_ms = Column(Integer, default=0, nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    source = relationship("Source", back_populates="fetch_logs")

    def __repr__(self):
        return f"<FetchLog(source_id={self.source_id}, status='{self.status}', fetched={self.items_fetched}, new={self.items_new})>"
