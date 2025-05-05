"""
Helper utilities for the Intelligent Itinerary Planner
"""

import json
import datetime

def format_itinerary_output(itinerary, preferences, pace):
    """
    Format the itinerary output into a structured format.
    
    Args:
        itinerary (list): List of daily itineraries
        preferences (list): User preferences
        pace (str): Travel pace
        
    Returns:
        dict: Structured itinerary output
    """
    # Calculate summary statistics
    cities_visited = set()
    total_attractions = 0
    countries_visited = set()
    
    for day in itinerary:
        if 'transition' in day and day['transition']:
            cities_visited.add(day['from_city'])
            cities_visited.add(day['to_city'])
            countries_visited.add(day['from_country'])
            countries_visited.add(day['to_country'])
        else:
            cities_visited.add(day['city'])
            countries_visited.add(day['country'])
            total_attractions += len(day.get('attractions', []))
    
    # Create summary
    summary = {
        "total_days": len(itinerary),
        "cities_visited": list(cities_visited),
        "countries_visited": list(countries_visited),
        "total_attractions": total_attractions,
        "preferences": preferences,
        "pace": pace,
        "generated_date": datetime.datetime.now().strftime("%Y-%m-%d"),
    }
    
    # Create detailed day plans
    days = []
    for day_data in itinerary:
        day_plan = {
            "day_number": day_data['day'],
            "date": None  # This would be set by the user later
        }
        
        # Handle transition days specially
        if 'transition' in day_data and day_data['transition']:
            day_plan.update({
                "is_transition_day": True,
                "from_city": day_data['from_city'],
                "from_country": day_data['from_country'],
                "to_city": day_data['to_city'],
                "to_country": day_data['to_country'],
                "travel_details": {
                    "mode": day_data['travel_mode'],
                    "duration_hours": day_data['travel_time_hours'],
                    "distance_km": day_data['distance_km'],
                },
                "travel_tips": day_data['travel_tips']
            })
        else:
            # Regular day in a city
            attractions_list = []
            for attraction in day_data.get('attractions', []):
                attractions_list.append({
                    "name": attraction['name'],
                    "category": attraction['categories'],
                    "duration_hours": attraction['duration_hours'],
                    "start_time": attraction['start_time'],
                    "end_time": attraction['end_time'],
                    "cost": attraction.get('cost', '€€'),
                    "description": attraction['description']
                })
            
            day_plan.update({
                "is_transition_day": False,
                "city": day_data['city'],
                "country": day_data['country'],
                "attractions": attractions_list,
                "meals": day_data.get('meals', {})
            })
            
            # Add city tips if it's the first day in a city
            if day_data['day'] == 1 or itinerary[day_data['day']-2].get('city', '') != day_data['city']:
                day_plan["city_tips"] = generate_city_tips(day_data['city'], day_data['country'])
        
        days.append(day_plan)
    
    # Create full output structure
    output = {
        "itinerary_summary": summary,
        "daily_plans": days
    }
    
    return output

def generate_city_tips(city, country):
    """
    Generate tips for a specific city.
    
    Args:
        city (str): City name
        country (str): Country name
        
    Returns:
        list: Tips for the city
    """
    # City-specific tips
    city_tips = {
        "Paris": [
            "Paris Metro tickets can be purchased in books of 10 ('carnet') for a discount.",
            "Many museums are free on the first Sunday of each month.",
            "The Paris Museum Pass gives access to over 50 museums and monuments.",
            "Locals often picnic along the Seine River in the evening."
        ],
        "Barcelona": [
            "The Barcelona Card offers free public transportation and discounts to many attractions.",
            "Be aware of pickpockets, especially on Las Ramblas and in crowded tourist areas.",
            "Many shops close for a few hours in the afternoon for siesta.",
            "Tapas bars are typically busiest after 9 PM."
        ],
        "Rome": [
            "Drinking from Rome's public fountains ('nasoni') is safe and the water is refreshing.",
            "Many museums require reservations, especially the Vatican Museums.",
            "Dress code for churches requires covered shoulders and knees.",
            "Avoid driving in the historic center - use public transportation instead."
        ],
        "Amsterdam": [
            "The I Amsterdam City Card includes free public transport and entry to many museums.",
            "Bike rental is the most popular way to get around the city.",
            "Watch out for bike lanes - pedestrians should stay on the sidewalks.",
            "Many museums and attractions require advance online booking."
        ]
    }
    
    # Get city-specific tips if available, otherwise use generic tips
    tips = city_tips.get(city, [
        f"Public transportation is a convenient way to explore {city}.",
        f"Learn a few basic phrases in the local language of {country}.",
        f"Keep a copy of your hotel address and contact information with you.",
        f"Check opening hours for attractions as they may vary by season."
    ])
    
    return tips