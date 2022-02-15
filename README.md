# GOCAD_SG_Grid_Reader
Simple routine to read a GOCAD SG Grid in ASCII

## Basic Idea

```python
for root, dirs, files in os.walk(r'C:\AusAEM\AusAEM_East_Resources_Corridor_ GA_layer_earth_inversion\GA_gocad_sgrids'):
    for file in files:
        print(file)
        if '.sg.data' in file:
            Grid = np.loadtxt(os.path.join(root,file), skiprows = 3) #Loading the data
            Points = Grid[:,0:3] #getting coords
            Triangles = Grid[:,4:7] #getting topology
            Triangles = Triangles.astype(np.int32) # making sure the ndarray is an integer:
            meshvista = pv.make_tri_mesh(Points, Triangles)
            meshvista['conductivity'] = Grid[:,3]
            meshvista['logCon'] = np.log(Grid[:,3])
            
            filename  = file
            filename = filename.replace('.sg.data','')
 ```

## Useful libraries

- PyVista
- PyMeshLAB

## Voxet Reader
Note script here :- https://github.com/elygeo/coseis/blob/main/cst/gocad.py
- junk = voxet(hfile)
- junk = voxet(hfile, load_props=['1'])
- junk['1']['PROP']['1']['DATA'].shape

## OpenGeoSys

- Can download a Window executable version
- Compiling for unix - tested on ubuntu - https://discourse.opengeosys.org/t/steps-to-build-ogs-cli-and-ogs-gui-on-ubuntu-20-04/878/3
- https://gitlab.opengeosys.org/RichardScottOZ/ogs [with some fixes/notes]

```bash
ubuntu@ip-112-12-12-112:~/build/release/bin$ ./GocadSGridReader -s SA_Geophysics_Reference_Model_SGrid.sg  -o SA2.vtu  
[2022-01-26 22:33:45.987] [ogs] [info] Start reading Gocad SGrid.
[2022-01-26 22:33:53.510] [ogs] [info] End reading Gocad SGrid.lags@@ums ZPOSITIVE END COORDAXIS_N 383 428 50
[2022-01-26 22:34:43.447] [ogs] [info] There are 11 properties in the mesh:
[2022-01-26 22:34:43.458] [ogs] [info]  Gravity_Inversion_Constrained: (7992586 values) [-99999, 3.2188799381256104]
[2022-01-26 22:34:43.469] [ogs] [info]  Gravity_Inversion_Unconstrained: (7992586 values) [-99999, 3.0738370418548584]
[2022-01-26 22:34:43.480] [ogs] [info]  Magnetic_Inversion_Constrained: (7992586 values) [-99999, 0.11462300270795822]
[2022-01-26 22:34:43.492] [ogs] [info]  Magnetic_Inversion_Unconstrained: (7992586 values) [-99999, 0.09801190346479416]
[2022-01-26 22:34:43.499] [ogs] [info]  RegionFlags: (7992586 values) [-1, 1427]
[2022-01-26 22:34:43.506] [ogs] [info]  Rock_Unit: (7992586 values) [-99999, 6]
[2022-01-26 22:34:43.514] [ogs] [info]  SA_Geophysics_AWAGS_Log_Resistivity: (7992586 values) [-99999, 3.7394332885742188]
[2022-01-26 22:34:43.522] [ogs] [info]  SA_Geophysics_AusREM_Crust_Vp: (7992586 values) [-99999, 8.297428131103516]
[2022-01-26 22:34:43.530] [ogs] [info]  SA_Geophysics_AusREM_Crust_Vsv: (7992586 values) [-99999, 4.777806758880615]
[2022-01-26 22:34:43.537] [ogs] [info]  SA_Geophysics_AusREM_Crust_rho: (7992586 values) [-99999, 3.4011118412017822]
[2022-01-26 22:34:43.546] [ogs] [info]  SA_Geophysics_Magnetotellurics_Gawler_Resistivity: (7992586 values) [-99999, 5.930550575256348]
[2022-01-26 22:34:43.546] [ogs] [info] Writing mesh to 'SA2.vtu'.
```
