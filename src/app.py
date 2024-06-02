import sys
import os

# Add the parent directory to sys.path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

#Import the app
from app_init import app
#Import the layouts
from app_layout import layout

#import dash_auth


"""
#Authentification
auth = dash_auth.BasicAuth(
    app,
    ld.load_users()[1]#ld.load_users_login
)
"""
#Start the app
if __name__ == "__main__":  
    server = app.server
    app.layout = layout
    app.run(debug=False)
    #app.run_server(debug=True)