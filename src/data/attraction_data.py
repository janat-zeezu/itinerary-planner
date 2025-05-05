"""
Attraction data processing module for the Intelligent Itinerary Planner
"""

import json
import os
from pathlib import Path

class AttractionDataProcessor:
    """Process and validate attraction data."""
    
    def __init__(self, data_path):
        """
        Initialize the attraction data processor.
        
        Args:
            data_path (str or Path): Path to the attraction data JSON file
        """
        self.data_path = Path(data_path)
        self.cities_data = self._load_data()
        self._preprocess_data()
    
    def _load_data(self):
        """
        Load attraction data from JSON file.
        
        Returns:
            dict: The loaded data
        
        Raises:
            FileNotFoundError: If the data file cannot be found
            json.JSONDecodeError: If the data file is not valid JSON
        """
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Check if the data has the expected structure
            if 'cities' not in data:
                raise ValueError("Data format error: 'cities' key not found in the data.")
                
            return data['cities']
        except FileNotFoundError:
            raise FileNotFoundError(f"Attraction data file not found: {self.data_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON format in attraction data file: {self.data_path}")
    
    def _preprocess_data(self):
        """
        Clean, normalize, and validate the attraction data.
        
        This method processes each city and its attractions to ensure data quality
        and consistency. It also adds derived fields that will be useful for itinerary planning.
        """
        for city in self.cities_data:
            # Validate city data
            required_city_fields = ['name', 'country', 'attractions']
            for field in required_city_fields:
                if field not in city:
                    raise ValueError(f"Missing required field '{field}' for city: {city.get('name', 'Unknown')}")
            
            # Set default importance if not provided
            if 'importance' not in city:
                city['importance'] = 3  # Medium importance by default
            
            # Process attractions for this city
            self._process_attractions(city)
    
    def _process_attractions(self, city):
        """
        Process attractions for a specific city.
        
        Args:
            city (dict): City data including attractions
        """
        if not city.get('attractions'):
            city['attractions'] = []
            return
        
        for idx, attraction in enumerate(city['attractions']):
            # Validate attraction data
            required_attraction_fields = ['name', 'description', 'duration_hours', 'categories']
            for field in required_attraction_fields:
                if field not in attraction:
                    raise ValueError(
                        f"Missing required field '{field}' for attraction: "
                        f"{attraction.get('name', f'Unknown (index {idx})')} in {city['name']}"
                    )
            
            # Normalize text fields
            attraction['name'] = attraction['name'].strip()
            attraction['description'] = attraction['description'].strip()
            
            # Ensure categories is a list
            if isinstance(attraction['categories'], str):
                attraction['categories'] = [cat.strip() for cat in attraction['categories'].split(',')]
            
            # Normalize and validate categories
            attraction['categories'] = [cat.lower().strip() for cat in attraction['categories']]
            
            # Set default values if not provided
            if 'popularity' not in attraction:
                attraction['popularity'] = 3  # Medium popularity by default
                
            if 'cost' not in attraction:
                attraction['cost'] = '€€'  # Medium cost by default
                
            if 'best_time' not in attraction:
                attraction['best_time'] = ['morning', 'afternoon']  # Default time
                
            # Create a rich text representation for embedding
            attraction['text_for_embedding'] = (
                f"{attraction['name']}. {attraction['description']} "
                f"Categories: {', '.join(attraction['categories'])}"
            )
    
    def get_processed_data(self):
        """
        Get the processed cities data.
        
        Returns:
            list: List of city dictionaries with processed attraction data
        """
        return self.cities_data
    
    def get_attraction_texts(self):
        """
        Extract text representations for all attractions.
        
        Returns:
            list: List of attraction text representations
            list: Corresponding city and attraction indices
        """
        texts = []
        indices = []  # [(city_idx, attraction_idx), ...]
        
        for city_idx, city in enumerate(self.cities_data):
            for attraction_idx, attraction in enumerate(city['attractions']):
                texts.append(attraction['text_for_embedding'])
                indices.append((city_idx, attraction_idx))
        
        return texts, indices