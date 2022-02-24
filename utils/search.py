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
import plotly.io as pio
pio.renderers.default = "browser"



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
        self.tif_dsm(lambert_coo)
        self.tif_dtm(lambert_coo)
        
    def tif_dsm(self, lambert_coo):
        folder_path = os.path.abspath("/home/becode2/data/GeoTIFF_DSM/")
        for path, dirs, files in os.walk(folder_path):
            for filename in files:
                tif = f'{folder_path}/{filename}'
                possible_dsm_ds = rasterio.open(tif)
                b_list = possible_dsm_ds.bounds
                #print(f'{possible_ds}, {int(b_list[0])},{int(b_list[1])},{int(lambert_coo[0][0])},{int(lambert_coo[0][1])},')
                if int(b_list[0]) <= int(lambert_coo[0][0]) <= int(b_list[2]) and int(b_list[1]) <= int(lambert_coo[0][1]) <= int(b_list[3]) :
                    ds_dsm = possible_dsm_ds
                    self.tif_dsm_clipping(ds,lambert_coo)
    
    def tif_dtm(self, lambert_coo):
            folder_path = os.path.abspath("/home/becode2/data/GeoTIFF_DTM/")
            for path, dirs, files in os.walk(folder_path):
                for filename in files:
                    tif = f'{folder_path}/{filename}'
                    possible_dtm_ds = rasterio.open(tif)
                    b_list = possible_dtm_ds.bounds
                    #print(f'{possible_ds}, {int(b_list[0])},{int(b_list[1])},{int(lambert_coo[0][0])},{int(lambert_coo[0][1])},')
                    if int(b_list[0]) <= int(lambert_coo[0][0]) <= int(b_list[2]) and int(b_list[1]) <= int(lambert_coo[0][1]) <= int(b_list[3]) :
                        ds_dtm = possible_dtm_ds
                        self.tif_dsm_clipping(ds,lambert_coo)

    def boundries(self, )
         xmin = lambert_coo[0][0] - 50
        xmax = lambert_coo[0][0] + 50
        ymin = lambert_coo[0][1] - 50
        ymax = lambert_coo[0][1] + 50
        bbox = (xmin,ymax,xmax,ymin)           

    def tif_dsm_clipping(self,ds_dsm,lambert_coo):
        
        print(bbox, lambert_coo[0][1])
        gdal.Translate('new.tif', ds.name, projWin = bbox)
        ds2 = rasterio.open('new.tif')
        self.final_plot(ds2)

    
                    

    def tif_dtm_clipping(self,ds,lambert_coo):
        xmin = lambert_coo[0][0] - 50
        xmax = lambert_coo[0][0] + 50
        ymin = lambert_coo[0][1] - 50
        ymax = lambert_coo[0][1] + 50
        bbox = (xmin,ymax,xmax,ymin)
        print(bbox, lambert_coo[0][1])
        gdal.Translate('new.tif', ds.name, projWin = bbox)
        ds2 = rasterio.open('new.tif')
        self.final_plot(ds2)

    def final_plot(self,ds3):
        array = ds3.read(1)
        df = pd.DataFrame(data=array)
        fig = go.Figure(data=[go.Surface(z=df.values)])
        fig.update_layout(title='Pyiterator', autosize=False, width=1000, height=1000, margin=dict(l=65, r=50, b=65, t=90))
        fig.show()
        ds3.close()
Search()
