#!/usr/bin/env python3
"""
Intelligent Itinerary Planner - Main Entry Point
"""

import argparse
import json
import sys
import os
from pathlib import Path

from data.attraction_data import AttractionDataProcessor
from models.embedding_model import TransformerEmbeddingModel, SimpleEmbeddingModel
from algorithms.similarity_calculator import SemanticSimilarityCalculator
from algorithms.itinerary_optimizer import ItineraryOptimizer
from algorithms.route_planner import RoutePlanner
from utils.helpers import format_itinerary_output

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Intelligent Itinerary Planner')
    parser.add_argument('--use-transformer', action='store_true',
                        help='Use transformer model for embeddings')
    parser.add_argument('--days', type=int, required=True,
                        help='Number of days for the trip')
    parser.add_argument('--preferences', nargs='+', required=True,
                        help='Travel preferences (e.g., art museum cultural)')
    parser.add_argument('--pace', type=str, default='moderate',
                        choices=['relaxed', 'moderate', 'fast'],
                        help='Travel pace: relaxed, moderate, or fast')
    parser.add_argument('--output', type=str, required=True,
                        help='Output JSON file name')
    parser.add_argument('--data', type=str, default=None,
                        help='Path to attraction data JSON file (default: use built-in sample data)')
    
    return parser.parse_args()

def main():
    """Main execution function."""
    args = parse_arguments()
    
    # Print welcome message
    print("=" * 80)
    print("Intelligent Itinerary Planner")
    print("=" * 80)
    print(f"Days: {args.days}")
    print(f"Preferences: {', '.join(args.preferences)}")
    print(f"Pace: {args.pace}")
    print(f"Using Transformer: {args.use_transformer}")
    print("=" * 80)
    
    # Determine path to attraction data
    if args.data:
        data_path = args.data
    else:
        # Use sample data included with the program
        script_dir = Path(__file__).parent
        data_path = script_dir / "data" / "sample_attractions.json"
    
    try:
        # Step 1: Load and preprocess data
        print("Loading and preprocessing attraction data...")
        data_processor = AttractionDataProcessor(data_path)
        cities_data = data_processor.get_processed_data()
        
        # Step 2: Initialize embedding model
        print("Initializing embedding model...")
        if args.use_transformer:
            embedding_model = TransformerEmbeddingModel()
        else:
            embedding_model = SimpleEmbeddingModel()
        
        # Step 3: Calculate attraction similarities
        print("Calculating attraction similarities...")
        similarity_calculator = SemanticSimilarityCalculator(embedding_model)
        similarity_matrices = similarity_calculator.calculate_similarities(
            cities_data, args.preferences
        )
        
        # Step 4: Optimize itinerary across cities
        print("Planning optimal city allocation...")
        itinerary_optimizer = ItineraryOptimizer(
            cities_data, similarity_matrices, args.preferences, args.pace
        )
        city_allocation = itinerary_optimizer.allocate_days(args.days)
        
        # Step 5: Plan routes within each city
        print("Planning daily routes...")
        route_planner = RoutePlanner(cities_data, similarity_matrices)
        itinerary = route_planner.create_itinerary(city_allocation, args.preferences, args.pace)
        
        # Step 6: Format and save the itinerary output
        print("Formatting itinerary output...")
        output_itinerary = format_itinerary_output(itinerary, args.preferences, args.pace)
        
        # Save the output
        output_dir = os.path.dirname(args.output)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(output_itinerary, f, indent=2, ensure_ascii=False)
        
        print(f"Itinerary successfully generated and saved to {args.output}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()