"""
Route planning module for optimizing daily itineraries
"""

import numpy as np
from data.city_data import CityDataHelper

class RoutePlanner:
    """Plan optimal routes for each day of the itinerary."""
    
    def __init__(self, cities_data, similarity_matrices):
        """
        Initialize the route planner.
        
        Args:
            cities_data (list): List of city dictionaries
            similarity_matrices (dict): Dictionary mapping city indices to similarity matrices
        """
        self.cities_data = cities_data
        self.similarity_matrices = similarity_matrices
        
        # Calculate distance matrices for each city
        self.distance_matrices = {}
        for city_idx, city in enumerate(cities_data):
            attractions = city.get('attractions', [])
            if attractions:
                self.distance_matrices[city_idx] = CityDataHelper.calculate_distances_between_attractions(attractions)
    
    def create_itinerary(self, city_allocation, preferences, pace):
        """
        Create a complete day-by-day itinerary.
        
        Args:
            city_allocation (dict): Number of days allocated to each city
            preferences (list): User preferences
            pace (str): Travel pace (relaxed, moderate, fast)
            
        Returns:
            list: List of daily itineraries
        """
        # Determine pace multiplier
        pace_multipliers = {
            'relaxed': 0.7,   # Fewer attractions per day
            'moderate': 1.0,  # Standard number
            'fast': 1.3       # More attractions per day
        }
        pace_multiplier = pace_multipliers.get(pace, 1.0)
        
        # Create empty itinerary
        itinerary = []
        current_day = 1
        
        # Process cities in descending order of allocated days
        sorted_allocation = sorted(
            city_allocation.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        # Track city transitions
        prev_city_idx = None
        
        for city_idx, num_days in sorted_allocation:
            city = self.cities_data[city_idx]
            
            # Handle transition between cities
            if prev_city_idx is not None:
                prev_city = self.cities_data[prev_city_idx]
                transition_day = self._create_transition_day(
                    current_day, prev_city, city
                )
                itinerary.append(transition_day)
                current_day += 1
            
            # Create daily plans for this city
            daily_plans = self._plan_city_days(
                city_idx, int(num_days), preferences, pace_multiplier
            )
            
            # Add daily plans to itinerary
            for day_plan in daily_plans:
                day_plan['day'] = current_day
                itinerary.append(day_plan)
                current_day += 1
            
            prev_city_idx = city_idx
        
        return itinerary
    
    def _plan_city_days(self, city_idx, num_days, preferences, pace_multiplier):
        """
        Plan daily itineraries for a specific city.
        
        Args:
            city_idx (int): City index
            num_days (int): Number of days allocated to this city
            preferences (list): User preferences
            pace_multiplier (float): Multiplier for number of attractions per day
            
        Returns:
            list: List of daily plans for this city
        """
        city = self.cities_data[city_idx]
        attractions = city['attractions']
        
        if not attractions:
            # Return empty plans if no attractions
            return [{
                'city': city['name'],
                'country': city['country'],
                'attractions': [],
                'meals': self._suggest_meals(city, [])
            } for _ in range(num_days)]
        
        # Score attractions based on preference matching and popularity
        attraction_scores = self._score_attractions(city_idx, preferences)
        
        # Sort attractions by score (descending)
        sorted_attractions = sorted(
            zip(range(len(attractions)), attraction_scores),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Determine number of attractions to visit per day based on pace
        total_duration = sum(attr['duration_hours'] for attr in attractions)
        avg_hours_per_day = 8.0 * pace_multiplier  # Base of 8 hours adjusted by pace
        
        # Create attraction groups that fit within daily time limits
        daily_groups = []
        current_group = []
        current_duration = 0
        remaining_attractions = [idx for idx, _ in sorted_attractions]
        
        # First pass: create initial groupings based on top attractions
        while remaining_attractions and len(daily_groups) < num_days:
            suitable_found = False
            
            for i, attraction_idx in enumerate(remaining_attractions):
                attraction = attractions[attraction_idx]
                new_duration = current_duration + attraction['duration_hours']
                
                # If this attraction fits in the current day, add it
                if new_duration <= avg_hours_per_day:
                    current_group.append(attraction_idx)
                    current_duration = new_duration
                    remaining_attractions.pop(i)
                    suitable_found = True
                    break
            
            # If we couldn't find a suitable attraction, or the group is full enough
            if not suitable_found or current_duration >= avg_hours_per_day * 0.8:
                if current_group:  # Only add non-empty groups
                    daily_groups.append(current_group)
                    current_group = []
                    current_duration = 0
                # If no suitable attraction was found, force add the shortest one
                elif remaining_attractions:
                    shortest_idx = min(
                        range(len(remaining_attractions)),
                        key=lambda i: attractions[remaining_attractions[i]]['duration_hours']
                    )
                    attraction_idx = remaining_attractions.pop(shortest_idx)
                    daily_groups.append([attraction_idx])
        
        # Add any remaining attractions to the last day or create new days
        while remaining_attractions:
            if len(daily_groups) < num_days:
                # We have days available, create a new day
                shortest_idx = min(
                    range(len(remaining_attractions)),
                    key=lambda i: attractions[remaining_attractions[i]]['duration_hours']
                )
                attraction_idx = remaining_attractions.pop(shortest_idx)
                daily_groups.append([attraction_idx])
            else:
                # Add to existing days, trying to balance
                daily_groups.sort(
                    key=lambda group: sum(attractions[idx]['duration_hours'] for idx in group)
                )
                shortest_idx = min(
                    range(len(remaining_attractions)),
                    key=lambda i: attractions[remaining_attractions[i]]['duration_hours']
                )
                attraction_idx = remaining_attractions.pop(shortest_idx)
                daily_groups[0].append(attraction_idx)
        
        # Fill out days if we have more allocated than needed
        while len(daily_groups) < num_days:
            daily_groups.append([])
        
        # Second pass: optimize route for each day
        optimized_plans = []
        for group in daily_groups:
            if not group:
                # Empty day - free time
                optimized_plans.append({
                    'city': city['name'],
                    'country': city['country'],
                    'attractions': [],
                    'meals': self._suggest_meals(city, [])
                })
                continue
            
            # Optimize the route for this group
            optimized_route = self._optimize_daily_route(city_idx, group)
            
            # Create attraction list with timing
            start_time = 9.0  # 9:00 AM
            attraction_list = []
            
            for idx in optimized_route:
                attraction = attractions[idx].copy()
                
                # Format start and end times
                end_time = start_time + attraction['duration_hours']
                attraction['start_time'] = self._format_time(start_time)
                attraction['end_time'] = self._format_time(end_time)
                
                # Add buffer for travel and rest
                start_time = end_time + 0.5
                
                attraction_list.append(attraction)
            
            # Generate meal suggestions based on the day's attractions
            meals = self._suggest_meals(city, attraction_list)
            
            # Add to optimized plans
            optimized_plans.append({
                'city': city['name'],
                'country': city['country'],
                'attractions': attraction_list,
                'meals': meals
            })
        
        return optimized_plans
    
    def _score_attractions(self, city_idx, preferences):
        """
        Score attractions based on preferences and popularity.
        
        Args:
            city_idx (int): City index
            preferences (list): User preferences
            
        Returns:
            list: Scores for each attraction
        """
        city = self.cities_data[city_idx]
        attractions = city['attractions']
        
        scores = []
        for attraction in attractions:
            # Base score from popularity
            base_score = attraction.get('popularity', 3) / 5.0
            
            # Preference matching score
            pref_score = 0
            if preferences:
                categories = [cat.lower() for cat in attraction.get('categories', [])]
                for preference in preferences:
                    if preference.lower() in categories:
                        pref_score += 1
                
                # Normalize preference score
                pref_score = min(pref_score / len(preferences), 1.0)
            else:
                pref_score = 0.5  # Neutral if no preferences specified
            
            # Combined score
            final_score = (base_score * 0.4) + (pref_score * 0.6)
            scores.append(final_score)
        
        return scores
    
    def _optimize_daily_route(self, city_idx, attraction_indices):
        """
        Optimize the route for a day's attractions.
        
        Args:
            city_idx (int): City index
            attraction_indices (list): Indices of attractions to visit
            
        Returns:
            list: Optimized order of attraction indices
        """
        if not attraction_indices:
            return []
        
        if len(attraction_indices) <= 2:
            return attraction_indices
        
        # Get distance matrix for the city
        distance_matrix = self.distance_matrices.get(city_idx, None)
        if distance_matrix is None:
            return attraction_indices
        
        # Extract submatrix for our attractions
        n = len(attraction_indices)
        sub_distances = np.zeros((n, n))
        
        for i in range(n):
            for j in range(n):
                idx1 = attraction_indices[i]
                idx2 = attraction_indices[j]
                sub_distances[i, j] = distance_matrix[idx1][idx2]
        
        # Simple greedy algorithm for route optimization
        # Start at the first attraction (index 0)
        current = 0
        unvisited = set(range(1, n))
        route = [current]
        
        while unvisited:
            # Find the closest unvisited attraction
            next_idx = min(unvisited, key=lambda i: sub_distances[current, i])
            route.append(next_idx)
            unvisited.remove(next_idx)
            current = next_idx
        
        # Convert back to original attraction indices
        optimized_route = [attraction_indices[i] for i in route]
        return optimized_route
    
    def _create_transition_day(self, day_num, from_city, to_city):
        """
        Create a transition day between cities.
        
        Args:
            day_num (int): Day number
            from_city (dict): Departure city
            to_city (dict): Arrival city
            
        Returns:
            dict: Transition day details
        """
        # Calculate distance between cities
        distance = CityDataHelper.calculate_distance_between_cities(from_city, to_city)
        
        # Estimate travel time and mode
        travel_time, travel_mode = CityDataHelper.estimate_travel_time(distance)
        
        # Create transition day information
        transition_day = {
            'day': day_num,
            'transition': True,
            'from_city': from_city['name'],
            'from_country': from_city['country'],
            'to_city': to_city['name'],
            'to_country': to_city['country'],
            'travel_mode': travel_mode,
            'travel_time_hours': travel_time,
            'distance_km': round(distance, 1),
            'travel_tips': self._get_travel_tips(from_city, to_city, travel_mode)
        }
        
        return transition_day
    
    def _suggest_meals(self, city, attractions):
        """
        Suggest meals based on city and day's attractions.
        
        Args:
            city (dict): City information
            attractions (list): List of attractions for the day
            
        Returns:
            dict: Meal suggestions
        """
        # Default meal times
        breakfast = {"time": "08:00", "suggestion": f"Local breakfast in {city['name']}"}
        lunch = {"time": "13:00", "suggestion": f"Lunch near attractions in {city['name']}"}
        dinner = {"time": "19:00", "suggestion": f"Traditional {city['country']} cuisine for dinner"}
        
        # Check if we have food-related attractions
        food_attractions = [a for a in attractions if 'food' in a.get('categories', [])]
        
        # Adjust meal suggestions based on food attractions
        if food_attractions:
            for food_place in food_attractions:
                start_time = food_place.get('start_time', '')
                
                # Convert time string to hours
                if start_time:
                    try:
                        hours = float(start_time.split(':')[0])
                        if 11 <= hours <= 14:
                            # This is a lunch spot
                            lunch = {
                                "time": start_time,
                                "suggestion": f"Enjoy {food_place['name']}"
                            }
                        elif hours >= 17:
                            # This is a dinner spot
                            dinner = {
                                "time": start_time,
                                "suggestion": f"Enjoy {food_place['name']}"
                            }
                    except:
                        pass
        
        return {
            "breakfast": breakfast,
            "lunch": lunch,
            "dinner": dinner
        }
    
    def _get_travel_tips(self, from_city, to_city, travel_mode):
        """
        Generate travel tips for transitioning between cities.
        
        Args:
            from_city (dict): Departure city
            to_city (dict): Arrival city
            travel_mode (str): Mode of transportation
            
        Returns:
            list: Travel tips
        """
        tips = []
        
        # General tip
        tips.append(f"Plan to check out of your accommodation in {from_city['name']} early.")
        
        # Mode-specific tips
        if travel_mode == "flight":
            tips.append(f"Arrive at the airport at least 2 hours before your flight.")
            tips.append(f"Consider booking a direct flight to save time.")
        elif travel_mode == "train":
            tips.append(f"Train stations are usually in the city center, making transfers convenient.")
            tips.append(f"Book your train tickets in advance for better prices.")
        else:  # bus
            tips.append(f"Bus travel offers a scenic route between {from_city['name']} and {to_city['name']}.")
            tips.append(f"Buses may have less frequent schedules, so check timetables carefully.")
        
        # Arrival tip
        tips.append(f"Upon arrival in {to_city['name']}, head to your accommodation to drop off luggage.")
        
        return tips
    
    def _format_time(self, time_hours):
        """
        Format time from decimal hours to string.
        
        Args:
            time_hours (float): Time in decimal hours (e.g., 14.5 for 2:30 PM)
            
        Returns:
            str: Formatted time string (e.g., "14:30")
        """
        hours = int(time_hours)
        minutes = int((time_hours - hours) * 60)
        return f"{hours:02d}:{minutes:02d}"