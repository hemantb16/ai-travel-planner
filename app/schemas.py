from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class TripGenerateRequest(BaseModel):
    # Free-form input
    prompt: Optional[str] = Field(None, description="Trip description in plain English")
    
    # Structured form inputs (alternative to or complementary to prompt)
    destination: Optional[str] = Field(None, description="Target destination city/region/country")
    origin: Optional[str] = Field(None, description="Starting city/airport")
    duration_days: Optional[int] = Field(default=4, ge=1, le=30, description="Length of trip in days")
    start_date: Optional[str] = Field(None, description="Target month or start date")
    budget_tier: Optional[str] = Field(default="Moderate", description="Budget level: Budget, Moderate, Luxury")
    travel_style: Optional[str] = Field(default="Culture & Sightseeing", description="Travel style/vibe")
    travelers: Optional[str] = Field(default="Solo", description="Group composition: Solo, Couple, Family, Friends")
    special_interests: Optional[str] = Field(None, description="Food, art, hiking, relaxation, etc.")
    
    # Model override
    model: Optional[str] = Field(None, description="Ollama model to use for this generation")

class ChatMessageCreate(BaseModel):
    message: str = Field(..., min_length=1, description="Follow-up question or adjustment request")
    model: Optional[str] = Field(None, description="Ollama model to use for this chat response")

class ChatMessageResponse(BaseModel):
    id: int
    trip_id: str
    role: str
    content: str
    created_at: Optional[str] = None

class TripSummaryResponse(BaseModel):
    id: str
    title: str
    destination: str
    origin: Optional[str] = None
    duration_days: int
    budget_tier: Optional[str] = None
    travel_style: Optional[str] = None
    travelers: Optional[str] = None
    model_used: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class TripDetailResponse(TripSummaryResponse):
    user_prompt: str
    overview: Dict[str, Any] = {}
    flights: Dict[str, Any] = {}
    hotels: Dict[str, Any] = {}
    weather: Dict[str, Any] = {}
    itinerary: List[Dict[str, Any]] = []
    budget: Dict[str, Any] = {}
    raw_markdown: str = ""
    messages: List[ChatMessageResponse] = []

class SystemHealthResponse(BaseModel):
    ollama_online: bool
    ollama_url: str
    ollama_latency_ms: float
    available_models: List[str]
    selected_model: str
    database_online: bool
    database_type: str
    database_latency_ms: float
    database_error: Optional[str] = None
