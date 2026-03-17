import ee
import geemap
import pandas as pd
import numpy as np

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
num_points = 50  # resolution (increase for finer grid)

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

print(grid)