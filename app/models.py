import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base

def generate_uuid() -> str:
    return uuid.uuid4().hex

class Trip(Base):
    __tablename__ = "trips"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    destination = Column(String(255), nullable=False)
    origin = Column(String(255), nullable=True)
    duration_days = Column(Integer, nullable=False, default=3)
    budget_tier = Column(String(50), nullable=True, default="Moderate")
    travel_style = Column(String(100), nullable=True, default="Explorer")
    travelers = Column(String(50), nullable=True, default="Solo")
    user_prompt = Column(Text, nullable=False)
    model_used = Column(String(100), nullable=False, default="llama3.2:latest")
    
    # Structured trip sections stored as JSON
    overview = Column(JSON, nullable=True)
    flights = Column(JSON, nullable=True)
    hotels = Column(JSON, nullable=True)
    weather = Column(JSON, nullable=True)
    itinerary = Column(JSON, nullable=True)
    budget = Column(JSON, nullable=True)
    
    # Generated Markdown summary for instant copy & markdown download
    raw_markdown = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Follow up chat messages
    messages = relationship("ChatMessage", back_populates="trip", cascade="all, delete-orphan", order_by="ChatMessage.created_at")

    def to_summary_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "destination": self.destination,
            "origin": self.origin,
            "duration_days": self.duration_days,
            "budget_tier": self.budget_tier,
            "travel_style": self.travel_style,
            "travelers": self.travelers,
            "model_used": self.model_used,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def to_detail_dict(self):
        return {
            **self.to_summary_dict(),
            "user_prompt": self.user_prompt,
            "overview": self.overview or {},
            "flights": self.flights or {},
            "hotels": self.hotels or {},
            "weather": self.weather or {},
            "itinerary": self.itinerary or [],
            "budget": self.budget or {},
            "raw_markdown": self.raw_markdown or "",
            "messages": [m.to_dict() for m in self.messages] if self.messages else []
        }

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trip_id = Column(String(36), ForeignKey("trips.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), nullable=False) # "user" or "assistant"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    trip = relationship("Trip", back_populates="messages")

    def to_dict(self):
        return {
            "id": self.id,
            "trip_id": self.trip_id,
            "role": self.role,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
