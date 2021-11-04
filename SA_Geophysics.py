#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import pyvista as pv

Points = np.loadtxt(r"J:\Richard_Scott\Gravity_Inversion_Constrained SA_Geophysics_Reference_Model_SGrid_ASCIIGravity_Inversion_Constrained__ascii@@", skiprows = 3) #Loading the data only
mesh_points = Points[:,0:3]   ##x, y, z and density

point_cloud = pv.PolyData(mesh_points)
point_cloud['density'] = Points[:,3]

print(Points[:,3].shape)

SARef = pv.UniformGrid()

SARef.dimensions = (333, 378,  29)
SARef.origin = (-180000, 5752000,  -49000)
SARef.spacing = (4000, 4000, 1000)

SARef["density"] = Points[:,3]

SARef.set_active_scalars("density")

SARef["density"].shape

thres = SARef.threshold(value=1.000001, invert=False, preference='point')
print("THRES")
print(thres)

print(SARef['density'].shape)
print(SARef['density'].min())
print(SARef['density'].mean())
print(SARef['density'].max())

print(thres['density'].shape)
print(thres['density'].min())
print(thres['density'].mean())
print(thres['density'].max())
