"""
Utility functions for working with Gocad SG grids.

This module provides helper functions for:
- Format conversions (VTK, VTU, VTR, etc.)
- Data export and visualization
- Batch processing of multiple grids
"""

import os
from pathlib import Path
from typing import Union, List, Optional
import numpy as np
import warnings


def export_to_vtk(reader, output_file: Union[str, Path], 
                  properties: Optional[List[str]] = None,
                  file_format: str = 'vtu'):
    """
    Export Gocad SG grid to VTK format.
    
    Parameters
    ----------
    reader : GocadSGReader
        The reader object with loaded grid
    output_file : str or Path
        Output file path
    properties : list of str, optional
        Properties to export. If None, exports all.
    file_format : str, default='vtu'
        VTK file format: 'vtu' (unstructured), 'vtr' (rectilinear), or 'vti' (image)
    
    Returns
    -------
    Path
        Path to the created file
    """
    try:
        import pyvista as pv
    except ImportError:
        raise ImportError(
            "PyVista is required for VTK export. "
            "Install it with: pip install pyvista"
        )
    
    # Convert to PyVista grid
    grid = reader.to_pyvista(properties_to_load=properties)
    
    # Export based on format
    output_path = Path(output_file)
    
    if file_format.lower() == 'vtu':
        grid.save(output_path, binary=True)
    elif file_format.lower() == 'vtr':
        # Convert to rectilinear grid if possible
        grid.save(output_path, binary=True)
    elif file_format.lower() == 'vti':
        # Save as image data
        grid.save(output_path, binary=True)
    else:
        raise ValueError(f"Unsupported format: {file_format}")
    
    return output_path


def batch_convert(input_dir: Union[str, Path], 
                  output_dir: Union[str, Path],
                  file_format: str = 'vtu',
                  properties: Optional[List[str]] = None):
    """
    Batch convert all .sg files in a directory to VTK format.
    
    Parameters
    ----------
    input_dir : str or Path
        Directory containing .sg files
    output_dir : str or Path
        Directory for output files
    file_format : str, default='vtu'
        VTK file format
    properties : list of str, optional
        Properties to export
    
    Returns
    -------
    list of Path
        Paths to created files
    """
    from gocad_sg_reader import GocadSGReader
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Find all .sg files
    sg_files = list(input_path.glob('*.sg'))
    
    if not sg_files:
        warnings.warn(f"No .sg files found in {input_dir}")
        return []
    
    created_files = []
    
    for sg_file in sg_files:
        try:
            print(f"Processing {sg_file.name}...")
            reader = GocadSGReader(sg_file)
            
            output_file = output_path / f"{sg_file.stem}.{file_format}"
            export_to_vtk(reader, output_file, properties=properties, file_format=file_format)
            
            created_files.append(output_file)
            print(f"  -> Created {output_file.name}")
        
        except Exception as e:
            warnings.warn(f"Failed to process {sg_file.name}: {e}")
    
    return created_files


def create_point_cloud(reader, property_name: str, threshold: Optional[float] = None):
    """
    Create a point cloud from grid data with optional thresholding.
    
    Parameters
    ----------
    reader : GocadSGReader
        The reader object
    property_name : str
        Property to use for point cloud
    threshold : float, optional
        Minimum value threshold
    
    Returns
    -------
    pyvista.PolyData
        Point cloud
    """
    try:
        import pyvista as pv
    except ImportError:
        raise ImportError(
            "PyVista is required. Install it with: pip install pyvista"
        )
    
    # Get the property data
    prop_data = None
    for prop_id, prop_info in reader.properties.items():
        if prop_info['name'] == property_name or prop_id == property_name:
            prop_data = reader.read_property(prop_id)
            break
    
    if prop_data is None:
        raise ValueError(f"Property {property_name} not found")
    
    # Create grid to get coordinates
    grid = reader.to_pyvista(properties_to_load=[])
    points = grid.points
    
    # Flatten the property data if needed
    if prop_data.size != len(points):
        # Property might be cell data, need to interpolate to points
        prop_data = prop_data.flatten()[:len(points)]
    
    # Apply threshold if specified
    if threshold is not None:
        mask = prop_data >= threshold
        points = points[mask]
        prop_data = prop_data[mask]
    
    # Create point cloud
    point_cloud = pv.PolyData(points)
    point_cloud[property_name] = prop_data
    
    return point_cloud


def compare_grids(reader1, reader2, property_name: str):
    """
    Compare the same property from two different grids.
    
    Parameters
    ----------
    reader1 : GocadSGReader
        First grid reader
    reader2 : GocadSGReader
        Second grid reader
    property_name : str
        Property to compare
    
    Returns
    -------
    dict
        Statistics about the differences
    """
    # Read properties from both grids
    data1 = None
    data2 = None
    
    for prop_id, prop_info in reader1.properties.items():
        if prop_info['name'] == property_name or prop_id == property_name:
            data1 = reader1.read_property(prop_id)
            break
    
    for prop_id, prop_info in reader2.properties.items():
        if prop_info['name'] == property_name or prop_id == property_name:
            data2 = reader2.read_property(prop_id)
            break
    
    if data1 is None or data2 is None:
        raise ValueError(f"Property {property_name} not found in one or both grids")
    
    if data1.shape != data2.shape:
        raise ValueError(
            f"Grid dimensions don't match: {data1.shape} vs {data2.shape}"
        )
    
    # Calculate statistics
    diff = data1 - data2
    
    # Mask out NaN values
    valid_mask = ~(np.isnan(data1) | np.isnan(data2))
    
    if not np.any(valid_mask):
        return {
            'mean_diff': np.nan,
            'max_diff': np.nan,
            'min_diff': np.nan,
            'rmse': np.nan,
            'correlation': np.nan,
            'valid_count': 0
        }
    
    valid_diff = diff[valid_mask]
    valid_data1 = data1[valid_mask]
    valid_data2 = data2[valid_mask]
    
    stats = {
        'mean_diff': np.mean(valid_diff),
        'max_diff': np.max(np.abs(valid_diff)),
        'min_diff': np.min(valid_diff),
        'rmse': np.sqrt(np.mean(valid_diff**2)),
        'correlation': np.corrcoef(valid_data1, valid_data2)[0, 1],
        'valid_count': np.sum(valid_mask),
        'total_count': data1.size
    }
    
    return stats


def extract_slice(reader, axis: str, index: int, properties: Optional[List[str]] = None):
    """
    Extract a 2D slice from the 3D grid.
    
    Parameters
    ----------
    reader : GocadSGReader
        The reader object
    axis : str
        Axis to slice along: 'x', 'y', or 'z'
    index : int
        Index along the axis
    properties : list of str, optional
        Properties to include in the slice
    
    Returns
    -------
    dict
        Dictionary with slice data and coordinates
    """
    # Load the grid
    grid = reader.to_pyvista(properties_to_load=properties)
    
    # Extract slice based on axis
    axis_map = {'x': 0, 'y': 1, 'z': 2}
    if axis.lower() not in axis_map:
        raise ValueError(f"Invalid axis: {axis}. Must be 'x', 'y', or 'z'")
    
    axis_idx = axis_map[axis.lower()]
    
    # Get grid dimensions
    dims = grid.dimensions
    
    if index < 0 or index >= dims[axis_idx]:
        raise ValueError(
            f"Index {index} out of range for axis {axis} (0 to {dims[axis_idx]-1})"
        )
    
    # Create index arrays for slicing
    if axis_idx == 0:  # x-axis
        i_range = [index, index + 1]
        j_range = [0, dims[1]]
        k_range = [0, dims[2]]
    elif axis_idx == 1:  # y-axis
        i_range = [0, dims[0]]
        j_range = [index, index + 1]
        k_range = [0, dims[2]]
    else:  # z-axis
        i_range = [0, dims[0]]
        j_range = [0, dims[1]]
        k_range = [index, index + 1]
    
    # Extract the slice
    try:
        import pyvista as pv
        slice_grid = grid.extract_subset(i_range, j_range, k_range)
        return slice_grid
    except Exception as e:
        warnings.warn(f"Could not extract slice: {e}")
        return None


def get_value_at_point(reader, x: float, y: float, z: float, 
                       property_name: str) -> float:
    """
    Get property value at a specific point using interpolation.
    
    Parameters
    ----------
    reader : GocadSGReader
        The reader object
    x, y, z : float
        Coordinates of the point
    property_name : str
        Property to query
    
    Returns
    -------
    float
        Interpolated value at the point
    """
    try:
        import pyvista as pv
    except ImportError:
        raise ImportError(
            "PyVista is required. Install it with: pip install pyvista"
        )
    
    # Load the grid with the property
    for prop_id, prop_info in reader.properties.items():
        if prop_info['name'] == property_name or prop_id == property_name:
            grid = reader.to_pyvista(properties_to_load=[prop_id])
            
            # Sample at the point
            point = np.array([[x, y, z]])
            sampled = grid.sample(pv.PolyData(point))
            
            return sampled[prop_info['name']][0]
    
    raise ValueError(f"Property {property_name} not found")


def summarize_grid_statistics(reader, properties: Optional[List[str]] = None):
    """
    Generate statistical summary for grid properties.
    
    Parameters
    ----------
    reader : GocadSGReader
        The reader object
    properties : list of str, optional
        Properties to summarize. If None, summarizes all.
    
    Returns
    -------
    dict
        Dictionary of statistics for each property
    """
    if properties is None:
        properties = list(reader.properties.keys())
    
    stats = {}
    
    for prop_id in properties:
        try:
            data = reader.read_property(prop_id)
            prop_name = reader.properties[prop_id]['name']
            
            # Calculate statistics, ignoring NaN values
            valid_data = data[~np.isnan(data)]
            
            if len(valid_data) == 0:
                stats[prop_name] = {
                    'count': 0,
                    'valid_count': 0,
                    'min': np.nan,
                    'max': np.nan,
                    'mean': np.nan,
                    'median': np.nan,
                    'std': np.nan
                }
            else:
                stats[prop_name] = {
                    'count': data.size,
                    'valid_count': len(valid_data),
                    'min': np.min(valid_data),
                    'max': np.max(valid_data),
                    'mean': np.mean(valid_data),
                    'median': np.median(valid_data),
                    'std': np.std(valid_data),
                    'percentile_25': np.percentile(valid_data, 25),
                    'percentile_75': np.percentile(valid_data, 75)
                }
        
        except Exception as e:
            warnings.warn(f"Could not compute statistics for {prop_id}: {e}")
    
    return stats
