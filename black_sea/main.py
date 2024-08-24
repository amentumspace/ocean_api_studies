import map_plotter
import async_api_caller
import numpy as np 
import numpy.ma as ma
import os
from datetime import datetime
import matplotlib.pyplot as plt

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
dt = datetime(2024, 8, 21)

def plot_variable_at_depth(depth, variable, zlims=None):

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
                    units="PSU", img_name=f"{variable}_{depth}m.png", 
                    save=True, zlims=zlims)

# maps at these depths in metres
[plot_variable_at_depth(d, 'so') for d in [0, 200, 400]]

# plot CHl concentration map at surface
url = "https://ocean.amentum.io/nemo/bgc"
plot_variable_at_depth(10, 'chl', zlims=(0,0.5))

# TODO, plot at different dates to show swirl? 

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

flat_index = np.argmax(depths)

multi_dim_index = np.unravel_index(flat_index, depths.shape)


# Find max depth 
flat_index = np.argmax(depths)
multi_dim_index = np.unravel_index(flat_index, depths.shape)
max_depth = depths[multi_dim_index]

print(f"Maximum depth is {max_depth} m")

lat_deep = lats_f[flat_index]
lon_deep = lons_f[flat_index]

print(f"At lat, lon of {lat_deep},{lon_deep}")

# send marker for plotting
cont = map_plotter.plot(lons_g, lats_g, depths,  
                 units="metres", img_name="bathymetry.png", 
                 save=True, use_log_scale=True,
                 point_of_interest=(lat_deep, lon_deep))

# now we plot depth profiles for salinity, temperature, Chl

def plot_profile(depths: np.ndarray, values: np.ndarray, units: str, img_name: str = "image.png"):

    fig, ax = plt.subplots(figsize=(6, 8))

    ax.plot(values, depths, marker='None')

    # Invert y-axis so that depth increases downwards
    ax.invert_yaxis()

    # Adding labels and title
    ax.set_xlabel(units)
    ax.set_ylabel('Depth (m)')

    ax.set_ylim(top=0)

    # Show grid
    ax.grid(True)

    # Display the plot
    fig.savefig(img_name)

# first salinity profile, metres, 
depths = np.arange(0,2000.0,10.0)

url = "https://ocean.amentum.io/nemo/phys"

# generate param list for given variable at deepest point

def get_param_list(variable):

    return [
        dict(
            latitude = lat_deep,
            longitude = lon_deep, 
            depth = depth,
            variable = variable, 
            year = dt.year,
            month = dt.month,
            day = dt.day
        )
        for depth in depths
    ]

param_list = get_param_list('so')

responses_json = async_api_caller.run(
    url, headers, param_list
)

values = [r['value'] for r in responses_json]

plot_profile(depths, values, 'PSU', 'salinity_profile.png')

# now temp profile

param_list = get_param_list('thetao')

responses_json = async_api_caller.run(
    url, headers, param_list
)

values = [r['value'] for r in responses_json]

plot_profile(depths, values, 'deg C', 'temp_profile.png')

# now chl profile

param_list = get_param_list('chl')

url = "https://ocean.amentum.io/nemo/bgc"

responses_json = async_api_caller.run(
    url, headers, param_list
)

values = [r['value'] for r in responses_json]

max_chl = np.max(values)
max_chl_depth = depths[np.argmax(values)]

print(f"DCM of {max_chl} mg/m3 at {max_chl_depth} m")

plot_profile(depths, values, 'mg m-3', 'chl_profile.png')

# now zoom of Chl profile 

depths = np.arange(0,250.0,5.0)

param_list = get_param_list('chl')

responses_json = async_api_caller.run(
    url, headers, param_list
)

values = [r['value'] for r in responses_json]

plot_profile(depths, values, 'mg m-3', 'chl_profile_zoom.png')

# TODO, plot at different dates to animate movement? 


