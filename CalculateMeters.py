import math

def coordinateDistance(lat1, lon1, lat2, lon2):
#Convert degrees to radians
    radLat1 = lat1 * math.pi / 180
    radLon1 = lon1 * math.pi / 180
    radLat2 = lat2 * math.pi / 180
    radLon2 = lon2 * math.pi / 180
# Radius of the Earth in meters
    R = 6_371_000 # meters

# Differences in coordinates
    dLat = radLat2 - radLat1
    dLon = radLon2 - radLon1
# Haversine formula
    a = math.sin(dLat / 2) * math.sin(dLat / 2) + math.cos(radLat1) * math.cos(radLat2) * math.sin(dLon / 2) * math.sin(dLon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance # Return distance rounded to 2 decimal places



lat_min, lat_max = -2.726999, -2.713094
lon_min, lon_max = 37.646067, 37.665329

print(coordinateDistance(lat_min,lon_min, lat_max, lon_max))