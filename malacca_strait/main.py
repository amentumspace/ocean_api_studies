import map_plotter
import async_api_caller
import streamlit as st
import numpy as np
import numpy.ma as ma
import os


url = "https://ocean.amentum.io/gebco"
key = os.getenv("API_KEY")
if key is None: ValueError("set env var API_KEY")
headers = {'API-Key': key}


def main():
    print("Hello from malacca-strait!")

    # bathymetry map high res 


    # animation of day by day change in temp and salnity and
    # current between monsoon seasons
    # 


    st.title("🌊 Amentum Ocean Depth Map")

    st.markdown("""
    Enter a bounding box to retrieve and display bathymetry data for a given ROI
    """)

    # Bounding box input
    lon_min = st.number_input("Min Longitude", value=99.5)
    lon_max = st.number_input("Max Longitude", value=105.5)
    lat_min = st.number_input("Min Latitude", value=1)
    lat_max = st.number_input("Max Latitude", value=6.5)

    # Figure 1 salinity maps at different depths 
    res = 0.1 # deg (change to 0.1 deg)
    lons_l = np.arange(lon_min, lon_max, res)
    lats_l = np.arange(lat_min, lat_max, res)
    lons_g, lats_g = np.meshgrid(lons_l, lats_l, indexing='ij')
    # flatten gridded lat lons
    lons_f = lons_g.flatten()
    lats_f = lats_g.flatten()

    param_list = [
        dict(
            latitude = lat,
            longitude = lon, 
        )
        for (lat, lon) in zip(lats_f, lons_f)
    ]
    
    if st.button("Start mapping!"):
        with st.spinner("Fetching data..."):    

            # Send it! Bombard API with requests in an asyncronous fashion 
            # (order maintained by the package, automagically cached)
            responses_json = async_api_caller.run(
                url, headers, param_list
            )

            depths = [-r['elevation']['value'] for r in responses_json]

            depths = np.reshape(np.array(depths), lats_g.shape).astype(float)

            # over land points will be None 
            masked_depths = ma.masked_invalid(depths)

            cont = map_plotter.plot(lons_g, lats_g, masked_depths,  
                            units="m", img_name=f"bathy.png", 
                            save=True, zlims=[-100, 0])
            st.pyplot(cont.figure)



if __name__ == "__main__":
    main()
