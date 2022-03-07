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
import math 




class Search:

    nom = Nominatim(user_agent="Mon_Application")
    lambert_coo = []
    n = 0

    def __init__(self):
        address = input('Enter address---> ')
        result = self.nom.geocode(address)
        try:
            confirmation = input(f'\n Is this the address you are looking for? \n”{result.raw["display_name"]}" \n Yes/Y No/N --> ')
            if confirmation == "Y":
                  self.meters(result)
            elif confirmation == "N" :
                print("Please try beign more specific. Include city and country to the search")
                Search()
            else:
                print('Invalid answer. Please try again!')
                Search()
        except Exception as e:
            print('Somethign went wrong, please try again. Verify that inputs are corrrect')
            print('ex',e)
            Search()

    def meters(self, result):
        result = result
        n_input = int(input('\n Please enter the desired range in m² --->'))
        if type(n_input) != int:
            print("Invalid answer. Please try again!")
            self.meters(result)
        elif n_input > 5000:
            print('Sorry, that range is too large, try a smaller one')
            self.meters(result)
        else:
            self.n = n_input
        lat = result.latitude
        lon = result.longitude
        self.coordinates(lat,lon)

    def coordinates(self, lat, lon):
        gps_coo = [lat, lon]
        tgt_srs= osr.SpatialReference()
        tgt_srs.ImportFromEPSG(31370)
        src_srs= osr.SpatialReference()
        src_srs.ImportFromEPSG(4326)
        transform = osr.CoordinateTransformation(src_srs, tgt_srs)
        x,y,z = transform.TransformPoint(lat,lon)
        self.lambert_coo.append([x,y])
        self.tif_files()
        

    def boundries(self):
            xmin = self.lambert_coo[0][0] - math.sqrt(self.n)
            xmax = self.lambert_coo[0][0] + math.sqrt(self.n)
            ymin = self.lambert_coo[0][1] - math.sqrt(self.n)
            ymax = self.lambert_coo[0][1] + math.sqrt(self.n)
            bbox = [xmin,ymax,xmax,ymin]
            return(bbox) 
        
        
    def tif_files(self):
        lambert_coo = self.lambert_coo 
        folder_path = os.path.abspath("/home/becode2/data/GeoTIFF_DSM/")
        for path, dirs, files in os.walk(folder_path):
            for filename in files:
                tif_dsm = f'{folder_path}/{filename}'
                possible_dsm_ds = rasterio.open(tif_dsm)
                b_list = possible_dsm_ds.bounds
                #print(f'{possible_dsm_ds.bounds}, {int(b_list[0])},{int(b_list[3])},{int(lambert_coo[0][0])},{int(lambert_coo[0][1])},')
                if int(b_list[0]) <= int(lambert_coo[0][0]) <= int(b_list[2]) and int(b_list[1]) <= int(lambert_coo[0][1]) <= int(b_list[3]) :
                    ds_dsm = possible_dsm_ds
                    tif_dtm = f'{folder_path.replace("DSM","DTM")}/{filename.replace("DSM","DTM")}'
                    ds_dtm = rasterio.open(tif_dtm)
                    #print(ds_dsm, ds_dtm)
                    self.tif_clipping(ds_dsm, ds_dtm)
                    


    def tif_clipping(self, ds_dsm, ds_dtm):
        gdal.Translate('new_dsm.tif', ds_dsm.name, projWin = self.boundries())
        new_dsm = rasterio.open('new_dsm.tif')
        gdal.Translate('new_dtm.tif', ds_dtm.name, projWin = self.boundries())
        new_dtm = rasterio.open('new_dtm.tif')
        print(ds_dsm.name, ds_dtm.name)
        self.chm(new_dtm, new_dsm)

    def chm(self, new_dtm, new_dsm):
        ds_dsm_read = new_dsm.read(1)
        ds_dtm_read = new_dtm.read(1)
        ds_chm =   ds_dsm_read - ds_dtm_read
        self.final_plot(ds_chm)

    def final_plot(self,ds_chm):
        fig = go.Figure(data=[go.Surface(z=ds_chm)])
        fig.show()
        

