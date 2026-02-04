import googlemaps
from models import settings

gmaps = googlemaps.Client(key=settings.google_places_api_key)


def get_nearby_places(amenity: str, lat: float, lon: float, radius: int = 1000) -> str:
    """
    Finds nearby places using Google Maps.
    """
    try:
        places_result = gmaps.places_nearby(
            location=(lat, lon),
            radius=radius,
            keyword=amenity
        )
        
        results = places_result.get('results', [])
        if not results:
            return f"No {amenity} found within {radius}m."
        
        output = [f"Found {len(results)} {amenity}(s):"]
        for place in results[:5]:
            name = place.get('name')
            # 'vicinity' is the field for the simplified address in Nearby Search
            address = place.get('vicinity', 'Address not available')
            rating = place.get('rating', 'No rating')
            is_open = is_open = place.get('opening_hours', {}).get('open_now', False)
            
            # Formatted string for presentation
            output.append(f"- {name} located at {address} (Rating: {rating}) (Is Open: {is_open})")
            
        return "\n".join(output)
    except Exception as e:
        return f"Error: {str(e)}"