import sys
import os

# Add the parent directory to sys.path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

#Import the app
from app_init import app
#Import the layouts
from app_layout import layout

app.layout = layout
server = app.server

#Start the app
if __name__ == "__main__":  
    app.run_server(debug=True)
