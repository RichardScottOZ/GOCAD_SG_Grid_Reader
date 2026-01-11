# GOCAD_SG_Grid_Reader
Comprehensive Python library to read GOCAD SG (Structured Grid) files in both ASCII and binary formats.

## Overview

This repository provides a user-friendly, efficient Python extractor for Gocad SG grids that handles:
- **Binary files** (@@) - with proper byte order detection and data type handling
- **ASCII files** - improved from basic numpy loading
- **Multiple properties** per grid with automatic detection
- **Integration with PyVista** for visualization and VTK export
- **Robust error handling** and validation

This implementation addresses issues found in other tools (e.g., OpenGeoSys C++ reader) and provides a pure Python solution that's easy to use and extend.

## Installation

```bash
# Clone the repository
git clone https://github.com/RichardScottOZ/GOCAD_SG_Grid_Reader.git
cd GOCAD_SG_Grid_Reader

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### Basic Usage

```python
from gocad_sg_reader import GocadSGReader

# Load a Gocad SG grid
reader = GocadSGReader('path/to/your_grid.sg')

# Display grid information
print(reader.info())

# Read a specific property
data = reader.read_property('density')

# Read all properties
all_data = reader.read_all_properties()
```

### PyVista Integration

```python
from gocad_sg_reader import read_sg_grid

# Quick load as PyVista UniformGrid
grid = read_sg_grid('path/to/your_grid.sg')

# Visualize (requires PyVista)
grid.plot()

# Export to VTK format
grid.save('output.vtu')
```

### Using Utilities

```python
from gocad_utils import export_to_vtk, summarize_grid_statistics

# Export to VTK
export_to_vtk(reader, 'output.vtu', file_format='vtu')

# Get statistics
stats = summarize_grid_statistics(reader)
```

## Features

### Binary File Support

The reader automatically detects and handles binary property files (@@) with:
- Multiple data types (float32, float64)
- Both byte orders (little-endian, big-endian)
- Proper validation against expected grid dimensions
- Graceful handling of malformed files

### User-Friendly API

```python
# Simple convenience function
grid = read_sg_grid('data.sg')

# Or use the class for more control
reader = GocadSGReader('data.sg')
print(reader.info())  # Human-readable summary
data = reader.read_property('property_name')
```

### Comprehensive Examples

See `example_usage.py` for detailed examples demonstrating:
1. Basic usage and grid information
2. Creating PyVista grids
3. Property data analysis
4. Exporting to VTK format
5. Selective property loading
6. Computing grid statistics

Run examples:
```bash
python example_usage.py path/to/your_grid.sg
```

## Key Improvements Over Other Tools

### vs. OpenGeoSys C++ Reader

The OpenGeoSys reader had several issues (see below for examples):
- Binary file reading errors due to incorrect byte order assumptions
- Poor handling of different data types
- Missing values causing crashes

This Python implementation:
- ✅ Automatically detects byte order and data type
- ✅ Handles malformed files gracefully
- ✅ Provides clear error messages and warnings
- ✅ Pure Python - no compilation needed

### vs. Basic numpy.loadtxt

Basic approach (old way):
```python
Grid = np.loadtxt(file, skiprows=3)  # ASCII only, no metadata
```

New approach:
```python
reader = GocadSGReader('grid.sg')  # Handles ASCII, binary, metadata
grid = reader.to_pyvista()  # Full 3D grid with all properties
```

## API Reference

### GocadSGReader

Main class for reading Gocad SG grids.

**Methods:**
- `__init__(sg_file)` - Initialize reader with .sg header file
- `read_property(property_id)` - Read a specific property
- `read_all_properties()` - Read all properties
- `to_pyvista(properties_to_load)` - Convert to PyVista UniformGrid
- `info()` - Get human-readable grid information

**Attributes:**
- `dimensions` - Grid dimensions (nx, ny, nz)
- `origin` - Grid origin (x, y, z)
- `spacing` - Grid spacing (dx, dy, dz)
- `properties` - Dictionary of available properties
- `header` - Grid metadata from .sg file

### Utility Functions

From `gocad_utils.py`:
- `export_to_vtk(reader, output_file, properties, file_format)` - Export to VTK
- `batch_convert(input_dir, output_dir, file_format)` - Batch process multiple grids
- `summarize_grid_statistics(reader, properties)` - Compute statistics
- `extract_slice(reader, axis, index, properties)` - Extract 2D slice
- `compare_grids(reader1, reader2, property_name)` - Compare two grids

## File Format Support

### Supported Formats

- **.sg** - Header file with grid metadata (required)
- **@@** - Binary property files (IEEE float32/float64, little/big endian)
- **ASCII** - Text-based property files

### Example File Structure

```
my_grid.sg                    # Header file
my_grid_density@@            # Binary property
my_grid_susceptibility@@     # Binary property
my_grid_temperature          # ASCII property (optional)
```

## Requirements

- Python >= 3.7
- numpy >= 1.20.0
- pyvista >= 0.38.0 (optional, for visualization and VTK export)

## Old Documentation (Historical Reference)

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

## ASCI Reader class here: -
- https://gist.github.com/T4mmi/b0545c0dfd7b60f3e4f15f3b4e54f7e8

## OpenGeoSys
- discussion thread https://discourse.opengeosys.org/t/sgrid-reader-error-understanding/893/20
- Can download a Window executable version - doesn't work on Windows 10, anyway, for me - some datatype size error, need to work out why, recompile
e.g.
```bash
(gemgis) J:\ogs-6.4.1-107-gbf7c7494de-Windows-10.0.19043-python-3.8.2-utils\bin>GocadSGridReader.exe -s Cloncurry_inversions.sg -o Clonucrry_inversions.vtu
[2022-02-15 17:58:03.899] [ogs] [info] Start reading Gocad SGrid.
[2022-02-15 17:58:04.619] [ogs] [error] readBinaryArray(): Error while reading from file 'Cloncurry_inversions_unconst_sus@@'.
[2022-02-15 17:58:04.619] [ogs] [error] Read different number of values. Expected 1673917, got 517085.
[2022-02-15 17:58:04.620] [ogs] [error] Reading of element properties file 'Cloncurry_inversions_unconst_sus@@' failed.
[2022-02-15 17:58:04.736] [ogs] [error] readBinaryArray(): Error while reading from file 'Cloncurry_inversions_unconst_den@@'.
[2022-02-15 17:58:04.737] [ogs] [error] Read different number of values. Expected 1673917, got 518617.
[2022-02-15 17:58:04.738] [ogs] [error] Reading of element properties file 'Cloncurry_inversions_unconst_den@@' failed.
[2022-02-15 17:58:04.739] [ogs] [error] readRegionFlagsBinary(): Could not open file '' for input.

[2022-02-15 17:58:04.759] [ogs] [info] End reading Gocad SGrid.
[2022-02-15 17:58:20.566] [ogs] [info] There are 3 properties in the mesh:
[2022-02-15 17:58:20.570] [ogs] [info]  RegionFlags: (1673917 values) [-1, -1]
[2022-02-15 17:58:20.571] [ogs] [info] Mesh property vector 'unconst_den' is empty.
[2022-02-15 17:58:20.572] [ogs] [info]  unconst_den: Could not get value bounds for property vector.
[2022-02-15 17:58:20.572] [ogs] [info] Mesh property vector 'unconst_sus' is empty.
[2022-02-15 17:58:20.574] [ogs] [info]  unconst_sus: Could not get value bounds for property vector.
[2022-02-15 17:58:20.575] [ogs] [info] Writing mesh to 'Cloncurry_inversions.vtu'.
```

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

- AuScope geomodel repository converts all sorts of GOCAD stuff
- SGRid example here:- https://github.com/RichardScottOZ/geomodel-2-3dweb - see notebook and changed gocad_importer.py file for example - dump out their work, turn into vtr [or whatever you like]
