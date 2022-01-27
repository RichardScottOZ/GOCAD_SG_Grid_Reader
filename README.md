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
