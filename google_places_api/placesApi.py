import requests

class PlacesApi:
    
    url = "https://places.googleapis.com/v1/places:searchNearby"
        
    _fields_mask_basic = [
            "places.accessibilityOptions", "places.addressComponents",
            "places.adrFormatAddress", "places.businessStatus",
            "places.displayName", "places.formattedAddress", 
            "places.googleMapsUri", "places.iconBackgroundColor",
            "places.iconMaskBaseUri", "places.id", "places.location",
            "places.name*", "places.photos", "places.plusCode",
            "places.primaryType", "places.primaryTypeDisplayName",
            "places.shortFormattedAddress", "places.subDestinations",
            "places.types", "places.utcOffsetMinutes", "places.viewport"
        ]
        
    
    def __init__(self, api_key):
        self.api_key = api_key

    
    def searchNearby(self, latitude, longitude, radius, fieldMask=None, includedTypes=None, includedPrimaryTypes = None, maxResults=20, rankPreference = "POPULARITY"):
        
        # Define the payload
        payload = {
                    "maxResultCount": maxResults,
                    "rankPreference": rankPreference,
                    "locationRestriction": {
                        "circle": {
                            "center": {
                                "latitude": latitude,
                                "longitude": longitude},
                            "radius": radius
                        }
                    }
                  }
        
        if includedTypes:
            payload["includedTypes"] = includedTypes
        if includedPrimaryTypes:
            payload["includedPrimaryTypes"] = includedPrimaryTypes
         
         
        # Define the headers    
        headers = {
                    "Content-Type": "application/json",
                    "X-Goog-Api-Key": self.api_key,               
                } 
        if fieldMask:
            headers["X-Goog-FieldMask"] = ','.join(fieldMask)
        
        return requests.post(self.url, headers=headers, json=payload)
