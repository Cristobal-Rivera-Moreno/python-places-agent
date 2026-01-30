import overpy

api = overpy.Overpass()

def get_nearby_amenities (radius: int, lat: float, lon: float, amenity: str) -> str:
  # Query for museums in a specific city area
  result = api.query(f"""
      [out:json];
      (
        node["amenity"={amenity}](around:{radius},{lat},{lon});
        way["amenity"={amenity}](around:{radius},{lat},{lon});
      );
      out center;
      """)
  # Extract names from both nodes and ways
  names = [n.tags.get("name", "Unnamed") for n in result.nodes if "name" in n.tags]
  names += [w.tags.get("name", "Unnamed") for w in result.ways if "name" in w.tags]