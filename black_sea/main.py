import map_plotter
import async_api_caller
import numpy as np 
import os
from datetime import datetime

# Take from Google maps, right click, copy coords
lat_min, lon_min = 41.06967946701225, 27.658566744859286
lat_max, lon_max = 46.97335743986021, 42.82746724576293

# Figure 1 salinity maps at different depths 
res = 1 # deg (change to 0.1 deg)
lons_l = np.arange(lon_min, lon_max, res)
lats_l = np.arange(lat_min, lat_max, res)
lons_g, lats_g = np.meshgrid(lons_l, lats_l, indexing='ij')
# flatten gridded lat lons
lons_f = lons_g.flatten()
lats_f = lats_g.flatten()

url = "https://ocean.amentum.io/nemo/phys"
headers = {'API-Key': os.getenv("API_KEY")}
variable = "so"
dt = datetime(2024, 8, 21)

# Firstly salinity map at shallow depth
depth = 0 # m 

# construct param list for the API calls 
# read API docs for valid ones https://www.amentum.io/ocean_docs#tag/nemo/operation/app.api_nemo.endpoints.NEMO_Phys.point
param_list = [
    dict(
        latitude = lat,
        longitude = lon, 
        depth = depth,
        variable = variable, 
        year = dt.year,
        month = dt.month,
        day = dt.day
    )
    for (lat, lon) in zip(lats_f, lons_f)
]

# Send it! Bombard API with requests in an asyncronous fashion (order maintained by the package)
responses_json = async_api_caller.run(
    url, headers, param_list
)