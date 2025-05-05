# Intelligent Itinerary Planner

An AI-powered system for creating optimized multi-city travel itineraries based on user preferences.

## Features

- Pre-processing of attraction data
- Transformer model integration for semantic understanding
- Attraction similarity calculation
- Intelligent day planning and city allocation
- Route optimization within cities
- Customized itineraries based on preferences and pace

## Requirements

Python 3.8+ and the packages listed in `requirements.txt`.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Create a 7-day art and culture focused itinerary
python src/main.py --use-transformer --days 7 --preferences art museum cultural --output art_culture.json

# Create a 6-day nature-focused itinerary
python src/main.py --use-transformer --days 6 --preferences outdoor nature park --output nature_trip.json

# Create a 5-day food-focused itinerary with a relaxed pace
python src/main.py --use-transformer --days 5 --preferences food culinary restaurant --pace relaxed --output food_trip.json
```

## Command Line Arguments

- `--use-transformer`: Use transformer model for embeddings (recommended)
- `--days`: Total number of days for the trip
- `--preferences`: Space-separated list of preferences (e.g., art museum cultural)
- `--pace`: Travel pace - fast, moderate, or relaxed (default: moderate)
- `--output`: Output JSON file name

## Project Structure

- `src/algorithms`: Contains optimization and planning algorithms
- `src/data`: Data handling and sample attraction data
- `src/models`: Transformer model implementation
- `src/utils`: Helper functions
- `src/main.py`: Main entry point