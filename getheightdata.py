import ee
import geemap
import pandas as pd
import numpy as np
import CalculateMeters

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

ee.Authenticate()

service_account = 'greendigger@grand-solstice-352909.iam.gserviceaccount.com'
credentials = ee.ServiceAccountCredentials(service_account, './keys.json')
ee.Initialize(credentials)


# ----------------------------
# 1. Define your region (bbox)
# ----------------------------
lat_min, lat_max = -2.726999, -2.713094
lon_min, lon_max = 37.646067, 37.665329

roi = ee.Geometry.Rectangle([lon_min, lat_min, lon_max, lat_max])
# ----------------------------
# 2. Create a regular grid
# ----------------------------
num_points = 70  # resolution (increase for finer grid) ##TODO Calculate this based on the avarage lenght of a the points needed for a 30 meter interval

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

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

ax.plot_surface(X, Y, Z)

ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
ax.set_zlabel("Elevation")

plt.show()