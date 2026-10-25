import os
import logging
from typing import List
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, PlainTextResponse, Response
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.config import HOST, PORT, DEFAULT_MODEL, BASE_DIR
from app.database import init_db, get_db, check_db_health
from app.models import Trip, ChatMessage
from app.schemas import (
    TripGenerateRequest,
    ChatMessageCreate,
    TripSummaryResponse,
    TripDetailResponse,
    SystemHealthResponse
)
from app.ollama_client import ollama_client
from app.planner import (
    build_planner_prompt,
    extract_json_from_text,
    fallback_markdown_parser,
    build_followup_prompt
)
from app.export_utils import generate_markdown

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("travel_planner.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize database
    logger.info("Initializing database...")
    init_db()
    # Check Ollama
    health = await ollama_client.check_health()
    if health.get("online"):
        logger.info(f"Ollama is reachable. Detected models: {health.get('models')}")
    else:
        logger.warning(f"Ollama is not currently reachable: {health.get('error')}")
    yield
    logger.info("Application shutting down.")

app = FastAPI(
    title="AI Travel Planner",
    description="Intelligent Local AI Travel Planner powered by Ollama and PostgreSQL",
    version="1.0.0",
    lifespan=lifespan
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- API ROUTES ----------------

@app.get("/api/health", response_model=SystemHealthResponse)
async def get_system_health():
    """Returns the live status of the Ollama AI engine and PostgreSQL database."""
    ollama_health = await ollama_client.check_health()
    db_health = check_db_health()
    
    models = ollama_health.get("models", [])
    selected_model = DEFAULT_MODEL if DEFAULT_MODEL in models else (models[0] if models else DEFAULT_MODEL)

    return SystemHealthResponse(
        ollama_online=ollama_health.get("online", False),
        ollama_url=ollama_client.base_url,
        ollama_latency_ms=ollama_health.get("latency_ms", 0.0),
        available_models=models,
        selected_model=selected_model,
        database_online=db_health.get("connected", False),
        database_type=db_health.get("type", "Unknown"),
        database_latency_ms=db_health.get("latency_ms", 0.0),
        database_error=db_health.get("error")
    )

@app.get("/api/models")
async def get_available_models():
    """Get list of installed Ollama models."""
    models = await ollama_client.get_models()
    return {"models": models, "default": DEFAULT_MODEL}

@app.get("/api/trips", response_model=List[TripSummaryResponse])
def list_trips(db: Session = Depends(get_db)):
    """List all saved trips, newest first."""
    trips = db.query(Trip).order_by(desc(Trip.updated_at)).all()
    return [t.to_summary_dict() for t in trips]

@app.post("/api/trips/generate", response_model=TripDetailResponse)
async def generate_trip(req: TripGenerateRequest, db: Session = Depends(get_db)):
    """Generate a complete trip plan using Ollama and save it to PostgreSQL."""
    # Ensure there is some input
    raw_prompt = req.prompt or ""
    if not raw_prompt.strip() and not req.destination:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide either a prompt in plain English or a destination in the trip builder."
        )

    # Destination inference
    dest = req.destination or "Destination"
    if not req.destination and raw_prompt:
        # Quick fallback extraction of destination from prompt if possible
        dest = raw_prompt.split("to ")[-1].split("for")[0].split("in")[0].strip() or "Your Destination"
        if len(dest) > 50:
            dest = dest[:50]

    system_prompt, user_prompt = build_planner_prompt(req)
    chosen_model = req.model or DEFAULT_MODEL
    logger.info(f"Generating trip with model '{chosen_model}' for: {dest}")

    # Generate with Ollama
    try:
        raw_output = await ollama_client.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            model=chosen_model,
            json_format=True,
            timeout=240.0
        )
    except Exception as e:
        logger.error(f"Error calling Ollama: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI Generation failed: {str(e)}"
        )

    # Parse JSON from AI response
    try:
        plan_data = extract_json_from_text(raw_output)
    except Exception as e:
        logger.warning(f"JSON parsing failed ({e}). Falling back to markdown parser.")
        plan_data = fallback_markdown_parser(raw_output, dest, req.duration_days or 4)

    # Normalize fields
    title = plan_data.get("title") or f"{req.duration_days or 4} Days in {dest.title()}"
    final_destination = plan_data.get("destination") or dest
    duration_days = plan_data.get("duration_days") or req.duration_days or 4
    overview = plan_data.get("overview") or {}
    flights = plan_data.get("flights") or {}
    hotels = plan_data.get("hotels") or {}
    weather = plan_data.get("weather") or {}
    itinerary = plan_data.get("itinerary") or []
    budget = plan_data.get("budget") or {}

    # Build markdown for export
    full_dict = {
        "title": title,
        "destination": final_destination,
        "origin": req.origin,
        "duration_days": duration_days,
        "budget_tier": req.budget_tier or "Moderate",
        "travel_style": req.travel_style or "Explorer",
        "travelers": req.travelers or "Solo",
        "overview": overview,
        "flights": flights,
        "hotels": hotels,
        "weather": weather,
        "itinerary": itinerary,
        "budget": budget,
    }
    raw_markdown = generate_markdown(full_dict)

    # Save to database
    trip = Trip(
        title=title,
        destination=final_destination,
        origin=req.origin,
        duration_days=duration_days,
        budget_tier=req.budget_tier or "Moderate",
        travel_style=req.travel_style or "Explorer",
        travelers=req.travelers or "Solo",
        user_prompt=raw_prompt or f"Trip to {final_destination}",
        model_used=chosen_model,
        overview=overview,
        flights=flights,
        hotels=hotels,
        weather=weather,
        itinerary=itinerary,
        budget=budget,
        raw_markdown=raw_markdown
    )
    db.add(trip)
    db.commit()
    db.refresh(trip)

    logger.info(f"Successfully generated and saved trip ID {trip.id} ({trip.title})")
    return trip.to_detail_dict()

@app.get("/api/trips/{trip_id}", response_model=TripDetailResponse)
def get_trip(trip_id: str, db: Session = Depends(get_db)):
    """Get full details of a saved trip including chat history."""
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip.to_detail_dict()

@app.delete("/api/trips/{trip_id}")
def delete_trip(trip_id: str, db: Session = Depends(get_db)):
    """Delete a saved trip and its chat history."""
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    db.delete(trip)
    db.commit()
    return {"success": True, "message": "Trip deleted successfully"}

@app.post("/api/trips/{trip_id}/chat")
async def chat_followup(trip_id: str, req: ChatMessageCreate, db: Session = Depends(get_db)):
    """Ask a follow-up question about an existing trip without starting over."""
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    # Record user question
    user_msg = ChatMessage(
        trip_id=trip.id,
        role="user",
        content=req.message.strip()
    )
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)

    # Format history and prompt for Ollama
    existing_messages = [m.to_dict() for m in trip.messages]
    chat_prompt_messages = build_followup_prompt(
        trip.to_detail_dict(),
        existing_messages,
        req.message.strip()
    )

    chosen_model = req.model or trip.model_used or DEFAULT_MODEL
    try:
        reply_content = await ollama_client.chat(
            messages=chat_prompt_messages,
            model=chosen_model
        )
    except Exception as e:
        logger.error(f"Error during follow-up chat: {e}")
        reply_content = f"⚠️ Could not generate response from Ollama: {str(e)}"

    # Record assistant response
    assistant_msg = ChatMessage(
        trip_id=trip.id,
        role="assistant",
        content=reply_content
    )
    db.add(assistant_msg)
    db.commit()
    db.refresh(assistant_msg)

    return {
        "user_message": user_msg.to_dict(),
        "assistant_message": assistant_msg.to_dict()
    }

@app.get("/api/trips/{trip_id}/export/markdown")
def export_trip_markdown(trip_id: str, db: Session = Depends(get_db)):
    """Download the trip plan formatted as Markdown."""
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    content = trip.raw_markdown or generate_markdown(trip.to_detail_dict())
    clean_title = "".join(c for c in trip.title if c.isalnum() or c in (" ", "_", "-")).strip().replace(" ", "_")
    filename = f"{clean_title}.md"

    return Response(
        content=content,
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

# Static files and frontend route
STATIC_DIR = BASE_DIR / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
def serve_index():
    """Serve the single page web application."""
    index_file = STATIC_DIR / "index.html"
    return FileResponse(str(index_file))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=HOST, port=PORT, reload=False)
