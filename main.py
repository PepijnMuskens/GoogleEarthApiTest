import ee
import geemap

# Trigger the authentication flow.
ee.Authenticate()

service_account = 'greendigger@grand-solstice-352909.iam.gserviceaccount.com'
credentials = ee.ServiceAccountCredentials(service_account, './keys.json')
ee.Initialize(credentials)

print('connected')
# Import the USGS ground elevation image.
elv = ee.Image('USGS/SRTMGL1_003')



u_lon = 37.646067
u_lat = -2.713094
u_poi = ee.Geometry.Point(u_lon, u_lat)

# Define the rural location of interest as a point away from the city.

r_lon = 37.665329
r_lat = -2.726999
r_poi = ee.Geometry.Point(r_lon, r_lat)

roi = r_poi.buffer(500)

scale = 30  # scale in meters

# Print the elevation near Lyon, France.

elv_list = elv.sample(roi,scale).getInfo()
print(elv_list)

elv_urban_point = elv.sample(u_poi, scale).first().get('elevation').getInfo()
print('Ground elevation at urban point:', elv_urban_point, 'm')