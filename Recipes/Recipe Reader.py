# -*- coding: utf-8 -*-
"""
Created on Tue Aug 23 09:04:48 2022

@author: elija
"""

import numpy as np
wdir="D:/GitHub/Exfoliator/Recipes"

#n,xsteps,ysteps,zsteps,tsteps
n,x,y,z,t=np.loadtxt("%s/082322_EDSC_V1.txt"%(wdir),dtype=float, delimiter=' ', skiprows=5,usecols=(1,3,5,7,9),unpack=True) 
#gives you step n (from 0), the 3D cartesian step size, and the wait time after the step
# units are in mm and seconds
print(x)