"""
City data processing module for the Intelligent Itinerary Planner
"""

from geopy.distance import great_circle

class CityDataHelper:
    """Helper functions for working with city data."""
    
    @staticmethod
    def calculate_distance_between_cities(city1, city2):
        """
        Calculate the approximate travel distance between two cities.
        
        Args:
            city1 (dict): First city data
            city2 (dict): Second city data
            
        Returns:
            float: Distance in kilometers between the cities
            
        Note:
            This is a simplified approach. In a real system, we might use
            an external API for more accurate travel distances/times.
        """
        # Use representative coordinates for each city
        # In a real system, these would be stored in the city data
        city_coords = {
            "Paris": (48.8566, 2.3522),
            "Barcelona": (41.3851, 2.1734),
            "Rome": (41.9028, 12.4964),
            "Amsterdam": (52.3676, 4.9041),
            "London": (51.5074, -0.1278),
            "Berlin": (52.5200, 13.4050),
            "Prague": (50.0755, 14.4378),
            "Vienna": (48.2082, 16.3738),
            "Budapest": (47.4979, 19.0402),
            "Athens": (37.9838, 23.7275),
            "Madrid": (40.4168, -3.7038),
            "Lisbon": (38.7223, -9.1393),
            "Dublin": (53.3498, -6.2603),
            "Stockholm": (59.3293, 18.0686),
            "Copenhagen": (55.6761, 12.5683),
            "Oslo": (59.9139, 10.7522),
            "Helsinki": (60.1699, 24.9384),
            "Warsaw": (52.2297, 21.0122),
            # Default coordinates if city not found
            "default": (0, 0)
        }
        
        # Get coordinates for both cities
        coord1 = city_coords.get(city1['name'], city_coords["default"])
        coord2 = city_coords.get(city2['name'], city_coords["default"])
        
        # Calculate distance using great circle distance (as the crow flies)
        distance = great_circle(coord1, coord2).kilometers
        
        return distance
    
    @staticmethod
    def estimate_travel_time(distance):
        """
        Estimate travel time between cities based on distance.
        
        Args:
            distance (float): Distance in kilometers
            
        Returns:
            float: Estimated travel time in hours
            str: Travel mode (flight, train, or bus)
        """
        # Simple heuristics for travel time estimation
        if distance > 800:
            # Long distance - flight
            travel_time = 2 + (distance / 800)  # Base 2 hours + flight time
            travel_mode = "flight"
        elif distance > 300:
            # Medium distance - train or flight
            travel_time = 1 + (distance / 150)  # Base 1 hour + train time
            travel_mode = "train"
        else:
            # Short distance - train or bus
            travel_time = 0.5 + (distance / 100)  # Base 0.5 hours + travel time
            travel_mode = "train" if distance > 100 else "bus"
        
        return round(travel_time, 1), travel_mode
    
    @staticmethod
    def calculate_distances_between_attractions(attractions):
        """
        Calculate distances between attractions within a city.
        
        Args:
            attractions (list): List of attraction dictionaries with location data
            
        Returns:
            list: 2D matrix of distances between attractions
        """
        n = len(attractions)
        distances = [[0 for _ in range(n)] for _ in range(n)]
        
        for i in range(n):
            for j in range(i+1, n):
                # Get locations
                loc_i = attractions[i].get('location', {'lat': 0, 'lng': 0})
                loc_j = attractions[j].get('location', {'lat': 0, 'lng': 0})
                
                # Calculate distance
                try:
                    dist = great_circle(
                        (loc_i['lat'], loc_i['lng']),
                        (loc_j['lat'], loc_j['lng'])
                    ).kilometers
                    
                    # Store distance in both directions
                    distances[i][j] = distances[j][i] = dist
                except:
                    # Default distance if calculation fails
                    distances[i][j] = distances[j][i] = 2.0
        
        return distances