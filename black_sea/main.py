import map_plotter
import async_api_caller
import numpy as np 
import numpy.ma as ma
import os
from datetime import datetime

# Take from Google maps, right click, copy coords
lat_min, lon_min = 41.06967946701225, 27.658566744859286
lat_max, lon_max = 46.97335743986021, 42.82746724576293

# Figure 1 salinity maps at different depths 
res = 0.1 # deg (change to 0.1 deg)
lons_l = np.arange(lon_min, lon_max, res)
lats_l = np.arange(lat_min, lat_max, res)
lons_g, lats_g = np.meshgrid(lons_l, lats_l, indexing='ij')
# flatten gridded lat lons
lons_f = lons_g.flatten()
lats_f = lats_g.flatten()

url = "https://ocean.amentum.io/nemo/phys"
key = os.getenv("API_KEY")
if key is None: ValueError("set env var API_KEY")
headers = {'API-Key': key}
variable = "so"
dt = datetime(2024, 8, 21)

def plot_salinity_at_depth(depth):

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

    # Send it! Bombard API with requests in an asyncronous fashion 
    # (order maintained by the package, automagically cached)
    responses_json = async_api_caller.run(
        url, headers, param_list
    )

    salinities = [r['value'] for r in responses_json]

    salinities = np.reshape(np.array(salinities), lats_g.shape).astype(float)

    # over land points will be None 
    masked_salinities = ma.masked_invalid(salinities)

    map_plotter.plot(lons_g, lats_g, masked_salinities,  
                    units="PSU", img_name=f"salinity_{depth}.png", 
                    save=True)

# maps at these depths in metres
[plot_salinity_at_depth(d) for d in [0, 200, 400]]

# generating a relief map of bathymetry using hte gebco API endpoint

param_list = [
    dict(
        latitude = lat,
        longitude = lon, 
    )
    for (lat, lon) in zip(lats_f, lons_f)
]

url = "https://ocean.amentum.io/gebco"

responses_json = async_api_caller.run(
    url, headers, param_list
)

# depth is negative elevation
depths = [-float(r['elevation']['value']) for r in responses_json]

depths = np.reshape(np.array(depths), lats_g.shape).astype(float)

map_plotter.plot(lons_g, lats_g, depths,  
                 units="metres", img_name="bathymetry.png", 
                 save=True, use_log_scale=True)
