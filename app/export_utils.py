from typing import Dict, Any

def generate_markdown(trip_data: Dict[str, Any]) -> str:
    """Generate clean, beautifully formatted Markdown representation of a trip plan."""
    title = trip_data.get("title", "Trip Itinerary")
    dest = trip_data.get("destination", "Destination")
    days = trip_data.get("duration_days", 3)
    overview = trip_data.get("overview", {})
    flights = trip_data.get("flights", {})
    hotels = trip_data.get("hotels", {})
    weather = trip_data.get("weather", {})
    itinerary = trip_data.get("itinerary", [])
    budget = trip_data.get("budget", {})

    lines = []
    lines.append(f"# ✈️ {title}")
    lines.append(f"**Destination:** {dest} | **Duration:** {days} Days | **Budget:** {trip_data.get('budget_tier', 'Moderate')}")
    lines.append("")
    
    # Overview
    if overview:
        lines.append("## 🌍 Overview & Highlights")
        if overview.get("summary"):
            lines.append(f"{overview['summary']}\n")
        lines.append(f"- **Best Time to Visit:** {overview.get('best_time_to_visit', 'N/A')}")
        lines.append(f"- **Local Currency:** {overview.get('local_currency', 'EUR (€)')}")
        lines.append(f"- **Language:** {overview.get('language', 'N/A')}")
        lines.append(f"- **Emergency Contact:** {overview.get('emergency_number', '112')}")
        
        highlights = overview.get("highlights", [])
        if highlights:
            lines.append("\n**Key Highlights:**")
            for h in highlights:
                lines.append(f"- {h}")
        lines.append("")

    # Flights & Transit
    if flights:
        lines.append("## 🛫 Flights & Transportation")
        lines.append(f"- **Departure Hubs:** {flights.get('departure_airports', 'Major European hubs')}")
        lines.append(f"- **Arrival Airports:** {flights.get('arrival_airports', 'Nearest airport')}")
        lines.append(f"- **Estimated Flight Time:** {flights.get('flight_duration_approx', 'N/A')}")
        lines.append(f"- **Estimated Flight Cost:** {flights.get('estimated_cost_range', 'N/A')}")
        lines.append(f"- **Recommended Carriers:** {flights.get('recommended_airlines_options', 'N/A')}")
        lines.append(f"- **Airport to City Transit:** {flights.get('ground_transit_from_airport', 'N/A')}")
        lines.append(f"- **Local Transit Tips:** {flights.get('local_transit_tips', 'N/A')}")
        lines.append("")

    # Hotels & Accommodations
    if hotels:
        lines.append("## 🏨 Hotels & Accommodations")
        areas = hotels.get("recommended_areas", [])
        if areas:
            lines.append("### Recommended Neighborhoods")
            for a in areas:
                name = a.get("area_name", "Area")
                vibe = a.get("vibe", "")
                pros = a.get("pros", "")
                cons = a.get("cons", "")
                lines.append(f"- **{name}** ({vibe}): Pros: {pros} | Cons: {cons}")
            lines.append("")

        suggestions = hotels.get("suggestions", [])
        if suggestions:
            lines.append("### Hotel Recommendations")
            for s in suggestions:
                name = s.get("name", "Hotel")
                rate = s.get("approx_rate_per_night", "")
                tier = s.get("price_tier", "")
                area = s.get("area", "")
                why = s.get("why_recommended", "")
                lines.append(f"- **{name}** ({tier} • ~{rate}/night in {area}): {why}")
            lines.append("")

        if hotels.get("booking_advice"):
            lines.append(f"**Booking Advice:** {hotels['booking_advice']}\n")

    # Weather
    if weather:
        lines.append("## ☀️ Weather & Packing")
        lines.append(f"- **Season & Climate:** {weather.get('season_vibe', 'N/A')}")
        lines.append(f"- **Temperature Range:** {weather.get('temp_range_celsius', 'N/A')}")
        lines.append(f"- **Rain Likelihood:** {weather.get('rain_likelihood', 'N/A')}")
        pack = weather.get("what_to_pack", [])
        if pack:
            lines.append("\n**Packing Essentials:**")
            for item in pack:
                lines.append(f"- [ ] {item}")
        lines.append("")

    # Itinerary
    if itinerary:
        lines.append("## 🗺️ Day-by-Day Itinerary")
        for day in itinerary:
            d_num = day.get("day_number", 1)
            d_title = day.get("day_title", f"Day {d_num}")
            lines.append(f"### Day {d_num}: {d_title}")
            lines.append(f"- **🌅 Morning:** {day.get('morning', 'Explore sights')}")
            lines.append(f"- **☀️ Afternoon:** {day.get('afternoon', 'Local walk & culture')}")
            lines.append(f"- **🌙 Evening:** {day.get('evening', 'Dinner & scenic walk')}")
            if day.get("dining_recommendation"):
                lines.append(f"- **🍽️ Dining Tip:** {day['dining_recommendation']}")
            if day.get("transit_tips"):
                lines.append(f"- **🚶 Transit:** {day['transit_tips']}")
            lines.append("")

    # Budget
    if budget:
        lines.append("## 💰 Estimated Budget Breakdown")
        lines.append(f"**Total Estimate:** {budget.get('estimated_total_range', 'N/A')} ({budget.get('currency', 'EUR')})\n")
        bd = budget.get("breakdown", {})
        if bd:
            lines.append("| Category | Estimated Cost |")
            lines.append("| :--- | :--- |")
            for cat, cost in bd.items():
                cat_formatted = cat.replace("_", " ").title()
                lines.append(f"| {cat_formatted} | {cost} |")
            lines.append("")

        tips = budget.get("money_saving_tips", [])
        if tips:
            lines.append("**Money-Saving Tips:**")
            for tip in tips:
                lines.append(f"- {tip}")
            lines.append("")

    lines.append("---")
    lines.append("*Generated by AI Travel Planner (Local Ollama & PostgreSQL)*")
    
    return "\n".join(lines)
