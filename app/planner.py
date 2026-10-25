import json
import re
import logging
from typing import Dict, Any, Tuple, List
from app.schemas import TripGenerateRequest

logger = logging.getLogger("travel_planner.planner")

PLANNER_SYSTEM_PROMPT = """You are an expert AI Travel Concierge and Trip Planner.
Your task is to generate a comprehensive, realistic, and highly practical travel plan based on the traveler's request.
You MUST output your response in valid JSON format matching the schema requested below.

Important requirements:
1. Provide realistic pricing and estimates in Euros (€) or local currency.
2. Ensure the day-by-day itinerary is paced realistically (do not cram 10 attractions into one morning; consider travel time, meal breaks, and relaxation).
3. Include specific local foods, transit details, and authentic neighborhoods.
4. If no origin is specified, assume a convenient European departure hub (such as Frankfurt, Munich, Berlin, or London).
5. Output ONLY the JSON object, starting with { and ending with }. Do not include markdown code block backticks if possible, or wrap cleanly in ```json ... ```.

Required JSON Structure:
{
  "title": "Evocative Title for the Trip",
  "destination": "City, Country",
  "duration_days": 4,
  "overview": {
    "summary": "2-3 sentences capturing the essence of the journey.",
    "best_time_to_visit": "Seasonal recommendation",
    "local_currency": "EUR (€)",
    "language": "Primary language and English proficiency",
    "emergency_number": "Local emergency contact (e.g. 112)",
    "highlights": ["Highlight 1", "Highlight 2", "Highlight 3", "Highlight 4"]
  },
  "flights": {
    "departure_airports": "Recommended departure airports/hubs",
    "arrival_airports": "Main arrival airports with IATA codes",
    "flight_duration_approx": "e.g. 1h 45m direct",
    "estimated_cost_range": "e.g. €120 - €260 round-trip",
    "recommended_airlines_options": "Airlines or alternative high-speed trains",
    "ground_transit_from_airport": "How to get to city center with estimated cost and time",
    "local_transit_tips": "Public transit passes, metro/tram tips, walking advice"
  },
  "hotels": {
    "recommended_areas": [
      {
        "area_name": "Neighborhood 1",
        "vibe": "Charming & Historic",
        "pros": "Walkable to main sites",
        "cons": "Can be noisy or pricier"
      },
      {
        "area_name": "Neighborhood 2",
        "vibe": "Hip & Foodie",
        "pros": "Great local restaurants and cafes",
        "cons": "Short metro ride to center"
      }
    ],
    "suggestions": [
      {
        "name": "Hotel Example 1",
        "area": "Neighborhood 1",
        "price_tier": "Moderate",
        "approx_rate_per_night": "€110 - €150",
        "why_recommended": "Great central location and boutique atmosphere"
      },
      {
        "name": "Hotel Example 2",
        "area": "Neighborhood 2",
        "price_tier": "Budget",
        "approx_rate_per_night": "€60 - €90",
        "why_recommended": "Clean, modern, friendly staff near transit"
      }
    ],
    "booking_advice": "When and where to book for best rates"
  },
  "weather": {
    "season_vibe": "Expected climate for this trip",
    "temp_range_celsius": "e.g. 16°C - 24°C",
    "rain_likelihood": "Low / Moderate / High",
    "what_to_pack": ["Comfortable walking shoes", "Layered clothing", "Light rain jacket", "Universal power adapter"]
  },
  "itinerary": [
    {
      "day_number": 1,
      "day_title": "Arrival & Historic Discovery",
      "morning": "Detailed morning activity with timing and locations",
      "afternoon": "Detailed afternoon activity with scenic stops",
      "evening": "Atmospheric evening experience, sunset viewpoint, or walk",
      "dining_recommendation": "Authentic dish and type of restaurant to try",
      "transit_tips": "How to get around on this day"
    }
  ],
  "budget": {
    "currency": "EUR (€)",
    "estimated_total_range": "e.g. €750 - €1,150 per person",
    "breakdown": {
      "flights_transit": "€180",
      "accommodation": "€360 (3 nights)",
      "food_drinks": "€220",
      "activities_attractions": "€90",
      "emergency_buffer": "€80"
    },
    "money_saving_tips": [
      "Tip 1 for saving money on meals or passes",
      "Tip 2 for free museum hours or discount cards",
      "Tip 3 for booking tickets in advance"
    ]
  }
}
"""

def build_planner_prompt(req: TripGenerateRequest) -> Tuple[str, str]:
    """Build the prompt for the AI planner."""
    # Build user request text
    components = []
    
    if req.prompt and req.prompt.strip():
        components.append(f"Traveler Request: {req.prompt.strip()}")
        
    if req.destination:
        components.append(f"Destination: {req.destination.strip()}")
    if req.origin:
        components.append(f"Origin/Departure: {req.origin.strip()}")
    if req.duration_days:
        components.append(f"Duration: {req.duration_days} days")
    if req.start_date:
        components.append(f"Travel Timing/Season: {req.start_date.strip()}")
    if req.budget_tier:
        components.append(f"Budget Level: {req.budget_tier.strip()}")
    if req.travel_style:
        components.append(f"Travel Style/Vibe: {req.travel_style.strip()}")
    if req.travelers:
        components.append(f"Travelers: {req.travelers.strip()}")
    if req.special_interests:
        components.append(f"Special Interests/Preferences: {req.special_interests.strip()}")

    user_text = "\n".join(components)
    prompt = f"""Please create a complete, detailed, and realistic travel itinerary in JSON format for the following trip request:

{user_text}

Remember to include all {req.duration_days or 4} days in the 'itinerary' array, and fill all sections (overview, flights, hotels, weather, itinerary, budget). Return only valid JSON."""

    return PLANNER_SYSTEM_PROMPT, prompt

def extract_json_from_text(text: str) -> Dict[str, Any]:
    """Robustly parse JSON from LLM output, extracting from fences or outer brackets."""
    text = text.strip()
    
    # 1. Try direct json.loads
    try:
        return json.loads(text)
    except Exception:
        pass

    # 2. Extract from ```json ... ``` markdown block
    json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    if json_match:
        try:
            return json.loads(json_match.group(1).strip())
        except Exception:
            pass

    # 3. Find outer { ... }
    start_idx = text.find("{")
    end_idx = text.rfind("}")
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        candidate = text[start_idx:end_idx + 1].strip()
        try:
            return json.loads(candidate)
        except Exception:
            # Try cleaning trailing commas: ,} -> } and ,] -> ]
            cleaned = re.sub(r",\s*([\]}])", r"\1", candidate)
            try:
                return json.loads(cleaned)
            except Exception:
                pass

    raise ValueError("Could not parse valid JSON from AI response")

def fallback_markdown_parser(raw_text: str, default_destination: str, duration: int) -> Dict[str, Any]:
    """Fallback in case the model returns unstructured or partially structured text."""
    logger.warning("Using fallback parser for AI travel plan output.")
    
    # Simple extraction of sections
    lines = raw_text.split("\n")
    days = []
    current_day = None
    
    for line in lines:
        day_match = re.search(r"(?:Day|Tag)\s*(\d+)[:\s]*(.*)", line, re.IGNORECASE)
        if day_match:
            if current_day:
                days.append(current_day)
            num = int(day_match.group(1))
            current_day = {
                "day_number": num,
                "day_title": day_match.group(2).strip() or f"Day {num} Exploration",
                "morning": "Morning exploration of top historic landmarks.",
                "afternoon": "Afternoon walk and local culinary stop.",
                "evening": "Evening relaxation and dinner.",
                "dining_recommendation": "Local specialty bistro.",
                "transit_tips": "Walking or local metro."
            }
        elif current_day and line.strip():
            if "morning" in line.lower():
                current_day["morning"] = line.strip()
            elif "afternoon" in line.lower():
                current_day["afternoon"] = line.strip()
            elif "evening" in line.lower() or "night" in line.lower():
                current_day["evening"] = line.strip()
                
    if current_day:
        days.append(current_day)
        
    if not days:
        for d in range(1, duration + 1):
            days.append({
                "day_number": d,
                "day_title": f"Day {d} Highlights",
                "morning": f"Explore central district and key cultural landmarks.",
                "afternoon": f"Visit scenic viewpoints and local markets.",
                "evening": f"Traditional dinner at an authentic neighborhood restaurant.",
                "dining_recommendation": "Local seasonal dishes and regional wine.",
                "transit_tips": "Walkable city center with convenient public transit."
            })

    return {
        "title": f"Adventure in {default_destination.title()}",
        "destination": default_destination,
        "duration_days": duration,
        "overview": {
            "summary": raw_text[:300] + "...",
            "best_time_to_visit": "Spring through Autumn",
            "local_currency": "EUR (€)",
            "language": "Local & English widely understood",
            "emergency_number": "112",
            "highlights": ["Historic Old Town", "Local Markets", "Scenic Viewpoints", "Art & Architecture"]
        },
        "flights": {
            "departure_airports": "Major European hubs",
            "arrival_airports": f"Nearest international airport to {default_destination}",
            "flight_duration_approx": "1.5 - 3 hours",
            "estimated_cost_range": "€120 - €280 round-trip",
            "recommended_airlines_options": "Lufthansa, Ryanair, EasyJet or Deutsche Bahn",
            "ground_transit_from_airport": "Express airport train or airport shuttle (approx. €8 - €15)",
            "local_transit_tips": "24h / 72h tourist transit pass recommended"
        },
        "hotels": {
            "recommended_areas": [
                {
                    "area_name": "City Center / Old Town",
                    "vibe": "Historic & Walkable",
                    "pros": "Steps away from all attractions",
                    "cons": "Higher lodging rates"
                },
                {
                    "area_name": "Arts & University District",
                    "vibe": "Vibrant & Affordable",
                    "pros": "Lively cafes and restaurants",
                    "cons": "Short ride to main sights"
                }
            ],
            "suggestions": [
                {
                    "name": f"Hotel Boutique {default_destination}",
                    "area": "City Center",
                    "price_tier": "Moderate",
                    "approx_rate_per_night": "€110 - €150",
                    "why_recommended": "Central location with excellent guest reviews"
                },
                {
                    "name": "Urban Comfort Stay",
                    "area": "Arts District",
                    "price_tier": "Budget",
                    "approx_rate_per_night": "€65 - €90",
                    "why_recommended": "Great budget option near metro"
                }
            ],
            "booking_advice": "Reserve 4 to 6 weeks in advance for optimal rates."
        },
        "weather": {
            "season_vibe": "Pleasant temperate climate",
            "temp_range_celsius": "15°C - 25°C",
            "rain_likelihood": "Moderate",
            "what_to_pack": ["Comfortable walking shoes", "Light layers", "Compact umbrella", "Sunglasses"]
        },
        "itinerary": days,
        "budget": {
            "currency": "EUR (€)",
            "estimated_total_range": f"€{duration * 140} - €{duration * 220}",
            "breakdown": {
                "flights_transit": "€180",
                "accommodation": f"€{duration * 85}",
                "food_drinks": f"€{duration * 45}",
                "activities_attractions": f"€{duration * 20}",
                "emergency_buffer": "€100"
            },
            "money_saving_tips": [
                "Purchase multi-day public transport tickets",
                "Enjoy lunch specials ('Menu del dia' or daily lunch menus)",
                "Book popular museums online ahead of time to skip lines"
            ]
        }
    }

def build_followup_prompt(trip_dict: Dict[str, Any], chat_history: List[Dict[str, str]], new_message: str) -> List[Dict[str, str]]:
    """Build messages array for follow-up conversation about an existing trip plan."""
    trip_summary = (
        f"TRIP CONTEXT:\n"
        f"Title: {trip_dict.get('title')}\n"
        f"Destination: {trip_dict.get('destination')}\n"
        f"Duration: {trip_dict.get('duration_days')} days\n"
        f"Budget Tier: {trip_dict.get('budget_tier')}\n"
        f"Overview: {trip_dict.get('overview', {}).get('summary', '')}\n"
        f"Total Budget Range: {trip_dict.get('budget', {}).get('estimated_total_range', '')}\n"
        f"Days in Itinerary: {len(trip_dict.get('itinerary', []))}\n"
    )

    system_msg = {
        "role": "system",
        "content": (
            "You are a friendly and knowledgeable AI Travel Assistant answering questions and adjusting plans "
            "for an existing trip. You have full context of the traveler's itinerary below.\n"
            "Answer clearly and concisely in markdown format. If the traveler asks for alternatives, additions, "
            "weather adaptations, or restaurant recommendations, provide practical, concrete tips.\n\n"
            + trip_summary
        )
    }

    messages = [system_msg]
    # Add previous chat history
    for msg in chat_history[-8:]: # keep last 8 messages for context
        messages.append({
            "role": msg.get("role", "user"),
            "content": msg.get("content", "")
        })

    # Add the new message
    messages.append({
        "role": "user",
        "content": new_message
    })

    return messages
