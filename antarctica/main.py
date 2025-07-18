

"""
Given area of interest (defined by lower and upper lat/lon bounds), 
Plot wave info
"""
import numpy as np 
import async_api_caller as aac
import map_plotter
from environs import Env
from datetime import datetime, timedelta
 
env = Env()
env.read_env("./.env")    
API_KEY = env("API_KEY")
headers = {'API-Key': API_KEY}

res = 1 # degree

lat_min, lon_min = -48.747100548604756, 79.95050415729786
lat_max, lon_max = -32.28616231410426, 174.39351169674035


def main():

    print("Hello from antarctica!")

    for day in range(7):

        lons_l = np.arange(lon_min, lon_max, res)
        lats_l = np.arange(lat_min, lat_max, res)

        lons_g, lats_g = np.meshgrid(lons_l, lats_l, indexing='ij')

        lons_f = lons_g.flatten()
        lats_f = lats_g.flatten()

        url = "https://ocean.amentum.io"

        dt = datetime.today() + timedelta(days=day)

        layers = {}

        for variable in ['uo', 'vo']:

            param_list = []

            for lon, lat in zip(lons_f, lats_f):

                param_list.append({
                    "latitude": lat,
                    "longitude": lon,
                    "variable": variable,
                    "year": dt.year,
                    "month": dt.month,
                    "day": dt.day,
                    "depth": 10, # m
                })

            responses_json = aac.run(
                f"{url}/nemo/phys", headers, param_list
            )

            variables = []
            for response_json in responses_json:
                variables.append(response_json['value'])

            layers[variable] = np.reshape(np.array(variables), lats_g.shape).astype(float)

        uo = layers['uo']
        vo = layers['vo']
        magnitudes = np.sqrt(np.power(uo,2) + np.power(vo,2))
        uo /= magnitudes
        vo /= magnitudes

        map_plotter.plot(lons_g, lats_g, 
                        variable=magnitudes, 
                        units="m/s", 
                        zlims=(0,1),
                        variable_vector=(uo, vo),
                        img_name=f"currents_{day}.png", 
                        plot=False, save=True)

    # convert -delay 200 -loop 0  currents_0.png currents_1.png currents_2.png currents_3.png currents_4.png currents_5.png currents_6.png  animated_heights.gif

if __name__ == "__main__":
    main()
