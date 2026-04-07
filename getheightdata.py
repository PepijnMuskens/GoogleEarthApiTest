import ee
import geemap
import pandas as pd
import numpy as np
import CalculateMeters
import math

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

ee.Authenticate()

service_account = 'greendigger@grand-solstice-352909.iam.gserviceaccount.com'
credentials = ee.ServiceAccountCredentials(service_account, './keys.json')
ee.Initialize(credentials)


# ----------------------------
# 1. Define your region (bbox)
# ----------------------------
lat_min, lat_max = -2.726959, -2.713594
lon_min, lon_max = 37.646567, 37.665389

#lat_min, lat_max = 51.469734, 51.486017
#lon_min, lon_max = 5.336235, 5.361959

roi = ee.Geometry.Rectangle([lon_min, lat_min, lon_max, lat_max])
# ----------------------------
# 2. Create a regular grid
# ----------------------------


#get vertical step size and starting point
vertdist = CalculateMeters.coordinateDistance(lat_max,lon_min,lat_min, lon_min)

vertremainder = vertdist % 30
vert_num_points = int(vertdist /30)
lat_max = lat_max - CalculateMeters.distanceToLat(vertremainder)
vertdist = CalculateMeters.coordinateDistance(lat_max,lon_min,lat_min, lon_min)
print(vertdist)


len1 = CalculateMeters.coordinateDistance(lat_max,lon_min, lat_max, lon_max)
len2 = CalculateMeters.coordinateDistance(lat_min,lon_min, lat_min, lon_max)



print(f"{len1}  {len2}")
num_points = 0  # resolution (increase for finer grid) ##TODO Calculate this based on the avarage lenght of a the points needed for a 30 meter interval
if len1 > len2 :
    num_points = int(len1 / 30)
else: 
    num_points = int(len2 / 30)

print(num_points)



lats = np.linspace(lat_min, lat_max, num_points)
lons = np.linspace(lon_min, lon_max, num_points)

features = []
for lat in lats:
    for lon in lons:
        point = ee.Geometry.Point([lon, lat])
        features.append(ee.Feature(point, {
            "latitude": lat,
            "longitude": lon
        }))

grid_fc = ee.FeatureCollection(features)

# ----------------------------
# 3. Load elevation dataset
# ----------------------------
elevation = ee.Image("USGS/SRTMGL1_003")

# ----------------------------
# 4. Sample using sampleRegions
# ----------------------------
sampled = elevation.sampleRegions(
    collection=grid_fc,
    properties=["latitude", "longitude"],  # keep coords
    scale=30
)

# ----------------------------
# 5. Convert to pandas
# ----------------------------
data = sampled.getInfo()

rows = []
for f in data["features"]:
    props = f["properties"]
    
    rows.append({
        "latitude": props["latitude"],
        "longitude": props["longitude"],
        "elevation": props["elevation"]
    })

df = pd.DataFrame(rows)

grid = df.pivot(index="latitude", columns="longitude", values="elevation")

lon0 = grid.columns[0]
lat0 = grid.index[0]

lons = []
lats = []
print(grid.to_numpy()[2][2])
for lon in grid.columns:
    t = CalculateMeters.coordinateDistance(lon0, grid.index[24], lon, grid.index[24])
    lons.append(t)
for lat in grid.index:
    t = CalculateMeters.coordinateDistance(grid.index[24],lat0, grid.index[24],lat)
    lats.append(t)
grid.columns = lons
grid.index = lats
print(grid)
# Prepare meshgrid
X, Y = np.meshgrid(grid.columns, grid.index)
Z = grid.values

min_lon = 1000000
min_lat = 1000000
min_y = 1000000

max_lon = 0
max_lat = 0
max_y = 0

for lon, items in grid.items():
    if items.max() > max_y:
        max_y = items.max()
        max_lon = lon
        max_lat = items.idxmax()
    elif items.min() < min_y:
        min_y = items.min()
        min_lon = lon
        min_lat = items.idxmin()
    
a = abs(min_lat - max_lat)
b = abs(min_lon - max_lon)

c = math.sqrt(a*a + b*b)

h = max_y - min_y

slope = h / c * 100

print(f"slope: {slope}")

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

ax.plot_surface(X, Y, Z)

ax.set_xlabel("Longitude m")
ax.set_ylabel("Latitude m")
ax.set_zlabel("Elevation m")

plt.show()