"""
Itinerary optimization module
"""

import numpy as np
from data.city_data import CityDataHelper

class ItineraryOptimizer:
    """Optimize the allocation of days across multiple cities."""
    
    def __init__(self, cities_data, similarity_matrices, preferences, pace):
        """
        Initialize the itinerary optimizer.
        
        Args:
            cities_data (list): List of city dictionaries
            similarity_matrices (dict): Dictionary mapping city indices to similarity matrices
            preferences (list): User preferences
            pace (str): Travel pace (relaxed, moderate, fast)
        """
        self.cities_data = cities_data
        self.similarity_matrices = similarity_matrices
        self.preferences = preferences
        self.pace = pace
        
        # Set visit duration multipliers based on pace
        self.pace_multipliers = {
            'relaxed': 1.2,   # More time per attraction
            'moderate': 1.0,  # Standard time
            'fast': 0.8       # Less time per attraction
        }
    
    def allocate_days(self, total_days):
        """
        Allocate available days across cities.
        
        Args:
            total_days (int): Total number of days available
            
        Returns:
            dict: Number of days allocated to each city
        """
        # Calculate city scores based on multiple factors
        city_scores = self._calculate_city_scores()
        
        # Initial allocation based on city scores
        raw_allocations = self._get_raw_allocations(city_scores, total_days)
        
        # Refine allocations to ensure minimum stays and handle travel days
        final_allocations = self._refine_allocations(raw_allocations, total_days)
        
        return final_allocations
    
    def _calculate_city_scores(self):
        """
        Calculate scores for each city based on importance, attractions, and preferences.
        
        Returns:
            list: List of scores for each city
        """
        city_scores = []
        
        for city_idx, city in enumerate(self.cities_data):
            # Base score from city importance
            importance = city.get('importance', 3)
            base_score = importance / 5.0  # Normalize to 0-1
            
            # Score from number of attractions matching preferences
            attraction_score = self._calculate_attraction_preference_score(city_idx)
            
            # Combined score
            score = (base_score * 0.4) + (attraction_score * 0.6)
            
            city_scores.append(score)
        
        return city_scores
    
    def _calculate_attraction_preference_score(self, city_idx):
        """
        Calculate score based on how well city attractions match preferences.
        
        Args:
            city_idx (int): Index of the city
            
        Returns:
            float: Score from 0-1
        """
        city = self.cities_data[city_idx]
        attractions = city['attractions']
        
        if not attractions or not self.preferences:
            return 0.5  # Neutral score if no attractions or preferences
        
        # Count matches between attraction categories and preferences
        matching_score = 0
        max_possible = len(attractions)
        
        for attraction in attractions:
            categories = [cat.lower() for cat in attraction.get('categories', [])]
            for preference in self.preferences:
                if preference.lower() in categories:
                    matching_score += 1
                    break  # Count each attraction only once
        
        # Normalize score
        if max_possible > 0:
            return matching_score / max_possible
        else:
            return 0
    
    def _get_raw_allocations(self, city_scores, total_days):
        """
        Get initial raw allocations of days based on scores.
        
        Args:
            city_scores (list): List of scores for each city
            total_days (int): Total days available
            
        Returns:
            dict: Raw allocation of days per city
        """
        # Normalize scores
        total_score = sum(city_scores)
        if total_score == 0:
            # Equal distribution if all scores are 0
            normalized_scores = [1.0/len(city_scores) for _ in city_scores]
        else:
            normalized_scores = [score/total_score for score in city_scores]
        
        # Calculate fractional days
        fractional_days = [normalized_score * total_days for normalized_score in normalized_scores]
        
        # Create allocation dictionary
        raw_allocations = {}
        for i, days in enumerate(fractional_days):
            if days > 0.5:  # Only include cities with at least half a day allocated
                raw_allocations[i] = days
        
        return raw_allocations
    
    def _refine_allocations(self, raw_allocations, total_days):
        """
        Refine raw allocations to ensure minimum stays and account for travel time.
        
        Args:
            raw_allocations (dict): Raw allocation of days per city
            total_days (int): Total days available
            
        Returns:
            dict: Final allocation of days per city
        """
        # Sort cities by allocation (descending)
        sorted_cities = sorted(
            raw_allocations.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        # Identify top cities to visit (limited by total days)
        remaining_days = total_days
        final_allocations = {}
        city_sequence = []
        
        # First pass: assign minimum days and track used days
        for city_idx, raw_days in sorted_cities:
            # Ensure at least 1 day per city
            min_days = max(1, int(raw_days))
            
            # If we can't allocate the minimum days, skip this city
            if min_days > remaining_days:
                continue
            
            # Add city to our itinerary
            final_allocations[city_idx] = min_days
            city_sequence.append(city_idx)
            remaining_days -= min_days
        
        # Second pass: account for travel days
        travel_days = self._calculate_travel_days(city_sequence)
        remaining_days -= travel_days
        
        # Third pass: distribute any remaining days to top cities
        if remaining_days > 0:
            # Redistribute remaining days proportionally
            for city_idx in final_allocations:
                if remaining_days <= 0:
                    break
                    
                # Add an extra day to this city
                final_allocations[city_idx] += 1
                remaining_days -= 1
        
        # If we're over budget, reduce days from least important cities
        if remaining_days < 0:
            # Reverse sort to take days from least important cities first
            for city_idx, _ in reversed(sorted_cities):
                if city_idx in final_allocations and final_allocations[city_idx] > 1:
                    final_allocations[city_idx] -= 1
                    remaining_days += 1
                    if remaining_days >= 0:
                        break
        
        return final_allocations
    
    def _calculate_travel_days(self, city_sequence):
        """
        Calculate travel days required between cities.
        
        Args:
            city_sequence (list): Sequence of city indices to visit
            
        Returns:
            float: Number of travel days needed
        """
        if len(city_sequence) <= 1:
            return 0
        
        total_travel_time = 0
        
        # Calculate travel time between consecutive cities
        for i in range(len(city_sequence) - 1):
            city1 = self.cities_data[city_sequence[i]]
            city2 = self.cities_data[city_sequence[i + 1]]
            
            # Calculate distance between cities
            distance = CityDataHelper.calculate_distance_between_cities(city1, city2)
            
            # Estimate travel time
            travel_time, _ = CityDataHelper.estimate_travel_time(distance)
            
            # Convert to days (assuming 8 hours of effective travel per day)
            travel_days = travel_time / 8.0
            
            total_travel_time += travel_days
        
        # Round up to nearest 0.5 days
        return np.ceil(total_travel_time * 2) / 2