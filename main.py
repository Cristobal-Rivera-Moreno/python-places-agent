from google import genai
from google.genai import types
from tools import get_nearby_amenities_from_google_maps
from routes import app
client = genai.Client(api_key="AIzaSyB_rhWvrvrVULIz0Urz_6FVNClsu5ugCQM")

tools_list = [get_nearby_amenities_from_google_maps]

# chat = client.chats.create(
#     model="gemini-2.0-flash",
#     config=types.GenerateContentConfig(
#         tools=tools_list,
#         system_instruction="You are a local concierge. Use Google Maps to find accurate location data for users. Provide a formatted answer as bulleted list")
# )

# def main():
#     print("Hello from python-places-agent!")
#     # Example Request
#     response = chat.send_message("What are some good pharmacies near lat 21.9167, lon -102.3069?")
#     print(f"Agent:\n{response.text}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="10.30.0.72", port=8000)
