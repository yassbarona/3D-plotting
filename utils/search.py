import geopy
from geopy.geocoders import Nominatim
from osgeo import gdal,ogr,osr
import rasterio #Used for handling .tif files
from rasterio.plot import show
import rioxarray as rio
import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go


class Search:

    nom = Nominatim(user_agent="Mon_Application")
   

    def __init__(self):
        address = input('Enter address ')
        result = self.nom.geocode(address)
        try:
            confirmation = input(f'\n Is this the address you are looking for? \n”{result.raw["display_name"]}" \n Yes/Y No/N --> ')
            if confirmation == "Y":
                lat = result.latitude
                lon = result.longitude
                self.coordinates(lat,lon)
            elif confirmation == "N" :
                print("Please try beign more specific. Include city and country to the search")
                Search()
            else:
                print('Invalid answer. Please try again!')
                Search()
        except Exception as e:
            print('Somethign went wrong. Verify that address is corrrect')
            print('ex',e)
            

    def coordinates(self, lat, lon):
        gps_coo = [lat, lon]
        lambert_coo = []
        tgt_srs= osr.SpatialReference()
        tgt_srs.ImportFromEPSG(31370)
        src_srs= osr.SpatialReference()
        src_srs.ImportFromEPSG(4326)
        transform = osr.CoordinateTransformation(src_srs, tgt_srs)
        x,y,z = transform.TransformPoint(lat,lon)
        lambert_coo.append([x,y])
        self.tif(lambert_coo)
        
    def tif(self, lambert_coo):
        folder_path = os.path.abspath("/home/becode2/data/GeoTIFF/")
        for path, dirs, files in os.walk(folder_path):
            for filename in files:
                tif = f'{folder_path}/{filename}'
                possible_ds = rasterio.open(tif)
                b_list = possible_ds.bounds
                #print(f'{possible_ds}, {int(b_list[0])},{int(b_list[1])},{int(lambert_coo[0][0])},{int(lambert_coo[0][1])},')
                if int(b_list[0]) <= int(lambert_coo[0][0]) <= int(b_list[2]) and int(b_list[1]) <= int(lambert_coo[0][1]) <= int(b_list[3]) :
                    ds = possible_ds
                    print(ds.name)
                    self.tif_clipping(ds,lambert_coo)
                    

    def tif_clipping(self,ds,lambert_coo):
        xmin = lambert_coo[0][0] - 20
        xmax = lambert_coo[0][0] + 20
        ymax = lambert_coo[0][1] + 20
        ymin = lambert_coo[0][1] - 20
        bbox = (xmin,ymax,xmax,ymin)
        print(bbox, lambert_coo[0][1])
        ds2 = gdal.Translate('new.tif', ds.name, projWin = bbox)
        ds3 = rasterio.open('new.tif')
        self.final_plot(ds3)
        

    def final_plot(self,ds3):
        array = ds3.read(1)
        df = pd.DataFrame(data=array)
        fig = go.Figure(data=[go.Surface(z=df.values)])
        fig.update_layout(title='Pyiterator', autosize=False, width=1000, height=1000, margin=dict(l=65, r=20, b=65, t=90))
        fig.show()
Search()
