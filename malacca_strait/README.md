
start

# TODO explain why so awkward

uv run streamlit run main.py


setup 

Skip this 

uv init 
uv add git+https://github.com/amentumspace/async_api_caller.git
uv add git+https://github.com/amentumspace/map_plotter    
uv add streamlit
uv add cartopy
uv add numpy 
uv lock 


to upgrade a git-sourced dependency 
uv pip install --upgrade --reinstall git+https://github.com/amentumspace/async_api_caller.git
