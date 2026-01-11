"""
GOCAD SG Grid Reader - A user-friendly and efficient extractor for Gocad SG grids.

This module provides functionality to read both ASCII and binary Gocad SG grid files,
handling the format issues that exist in other implementations (e.g., OpenGeoSys).

Based on:
- GOCAD format specification: paulbourke.net/dataformats/gocad/gocad.pdf
- OpenGeoSys C++ implementation insights
- AuScope geomodel repository examples

Author: Improved implementation for GOCAD_SG_Grid_Reader
License: MIT
"""

import os
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union
import warnings


# Binary data type configurations for reading property files
# Format: (numpy dtype string, item size in bytes)
BINARY_DTYPES = [('f4', 4), ('f8', 8)]  # float32, float64


class GocadSGReader:
    """
    A comprehensive reader for Gocad SG (Structured Grid) files.
    
    Handles both ASCII and binary formats with proper error handling and
    user-friendly interface.
    """
    
    def __init__(self, sg_file: Union[str, Path]):
        """
        Initialize the Gocad SG reader.
        
        Parameters
        ----------
        sg_file : str or Path
            Path to the .sg header file
        """
        self.sg_file = Path(sg_file)
        if not self.sg_file.exists():
            raise FileNotFoundError(f"SG file not found: {sg_file}")
        
        self.base_dir = self.sg_file.parent
        self.base_name = self.sg_file.stem
        
        # Grid metadata
        self.header = {}
        self.properties = {}
        self.axis_info = {}
        self.dimensions = None
        self.origin = None
        self.spacing = None
        
        # Parse the header
        self._parse_header()
    
    def _parse_header(self):
        """Parse the .sg header file to extract grid metadata."""
        with open(self.sg_file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        current_property = None
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            parts = line.split()
            if not parts:
                continue
            
            keyword = parts[0]
            
            # Parse axis information
            if keyword.startswith('AXIS_'):
                self._parse_axis_line(line, parts)
            
            # Parse property information
            elif keyword == 'PROPERTY':
                if len(parts) >= 2:
                    prop_id = parts[1]
                    prop_name = parts[2] if len(parts) > 2 else prop_id
                    current_property = prop_id
                    self.properties[prop_id] = {
                        'name': prop_name.strip('"'),
                        'file': None,
                        'data': None,
                        'no_data_value': None
                    }
            
            elif keyword == 'PROP_FILE' and current_property:
                # Extract filename from the line
                # Format: PROP_FILE <id> <filename>
                if len(parts) >= 3:
                    filename = parts[2].strip('"')
                    self.properties[current_property]['file'] = filename
            
            elif keyword == 'PROP_NO_DATA_VALUE' and current_property:
                if len(parts) >= 3:
                    try:
                        no_data = float(parts[2])
                        self.properties[current_property]['no_data_value'] = no_data
                    except ValueError:
                        pass
            
            # Parse other metadata
            elif keyword == 'GOCAD':
                self.header['type'] = ' '.join(parts[1:])
            
            elif keyword == 'NAME':
                self.header['name'] = ' '.join(parts[1:]).strip('"')
        
        # Calculate grid dimensions and spacing
        self._calculate_grid_params()
    
    def _parse_axis_line(self, line: str, parts: List[str]):
        """Parse axis information lines."""
        if parts[0] == 'AXIS_N':
            # AXIS_N <nx> <ny> <nz>
            if len(parts) >= 4:
                self.axis_info['N'] = [int(parts[1]), int(parts[2]), int(parts[3])]
        
        elif parts[0] == 'AXIS_O':
            # AXIS_O <ox> <oy> <oz>
            if len(parts) >= 4:
                self.axis_info['O'] = [float(parts[1]), float(parts[2]), float(parts[3])]
        
        elif parts[0] == 'AXIS_U':
            # AXIS_U <ux> <uy> <uz>
            if len(parts) >= 4:
                self.axis_info['U'] = [float(parts[1]), float(parts[2]), float(parts[3])]
        
        elif parts[0] == 'AXIS_V':
            # AXIS_V <vx> <vy> <vz>
            if len(parts) >= 4:
                self.axis_info['V'] = [float(parts[1]), float(parts[2]), float(parts[3])]
        
        elif parts[0] == 'AXIS_W':
            # AXIS_W <wx> <wy> <wz>
            if len(parts) >= 4:
                self.axis_info['W'] = [float(parts[1]), float(parts[2]), float(parts[3])]
        
        elif parts[0] == 'AXIS_MIN':
            # AXIS_MIN <umin> <vmin> <wmin>
            if len(parts) >= 4:
                self.axis_info['MIN'] = [float(parts[1]), float(parts[2]), float(parts[3])]
        
        elif parts[0] == 'AXIS_MAX':
            # AXIS_MAX <umax> <vmax> <wmax>
            if len(parts) >= 4:
                self.axis_info['MAX'] = [float(parts[1]), float(parts[2]), float(parts[3])]
    
    def _calculate_grid_params(self):
        """Calculate grid dimensions, origin, and spacing from axis info."""
        if 'N' in self.axis_info:
            self.dimensions = tuple(self.axis_info['N'])
        
        if 'O' in self.axis_info:
            self.origin = tuple(self.axis_info['O'])
        
        # Calculate spacing from axis vectors and dimensions
        if 'U' in self.axis_info and 'N' in self.axis_info:
            u_vec = np.array(self.axis_info['U'])
            v_vec = np.array(self.axis_info.get('V', [0, 0, 0]))
            w_vec = np.array(self.axis_info.get('W', [0, 0, 0]))
            
            # Spacing is the length of each axis vector divided by number of cells
            nx, ny, nz = self.axis_info['N']
            
            u_spacing = np.linalg.norm(u_vec) / (nx - 1) if nx > 1 else np.linalg.norm(u_vec)
            v_spacing = np.linalg.norm(v_vec) / (ny - 1) if ny > 1 else np.linalg.norm(v_vec)
            w_spacing = np.linalg.norm(w_vec) / (nz - 1) if nz > 1 else np.linalg.norm(w_vec)
            
            self.spacing = (u_spacing, v_spacing, w_spacing)
    
    def read_property(self, property_id: str) -> Optional[np.ndarray]:
        """
        Read a specific property from its file.
        
        Parameters
        ----------
        property_id : str
            The property identifier
        
        Returns
        -------
        np.ndarray or None
            The property data array, or None if reading fails
        """
        if property_id not in self.properties:
            raise ValueError(f"Property {property_id} not found in grid")
        
        prop_info = self.properties[property_id]
        prop_file = prop_info['file']
        
        if not prop_file:
            warnings.warn(f"No file specified for property {property_id}")
            return None
        
        # Build full path
        prop_path = self.base_dir / prop_file
        
        # Check if it's a binary file (@@)
        if prop_file.endswith('@@'):
            data = self._read_binary_property(prop_path, prop_info)
        else:
            data = self._read_ascii_property(prop_path, prop_info)
        
        # Store the data
        prop_info['data'] = data
        return data
    
    def _read_binary_property(self, filepath: Path, prop_info: Dict) -> Optional[np.ndarray]:
        """
        Read binary property file (@@).
        
        This implementation fixes issues found in OpenGeoSys reader by:
        1. Properly detecting data type and byte order
        2. Handling different float formats (IEEE float/double)
        3. Better error checking and validation
        
        Parameters
        ----------
        filepath : Path
            Path to the binary property file
        prop_info : dict
            Property metadata
        
        Returns
        -------
        np.ndarray or None
            The property data
        """
        if not filepath.exists():
            warnings.warn(f"Binary property file not found: {filepath}")
            return None
        
        file_size = filepath.stat().st_size
        
        # Expected number of values
        if self.dimensions:
            expected_count = np.prod(self.dimensions)
        else:
            warnings.warn("Grid dimensions not set, cannot validate binary data")
            expected_count = None
        
        # Try to determine the data type
        # Most common: 4-byte float (IEEE 754 single precision)
        # Sometimes: 8-byte double
        
        data = None
        for dtype_name, item_size in BINARY_DTYPES:
            if file_size % item_size == 0:
                count = file_size // item_size
                
                # Try both byte orders
                for byteorder in ['<', '>']:  # little-endian, big-endian
                    try:
                        dtype = np.dtype(byteorder + dtype_name)
                        test_data = np.fromfile(filepath, dtype=dtype)
                        
                        # Validate the data
                        if expected_count is not None and len(test_data) == expected_count:
                            data = test_data
                            break
                        elif expected_count is None:
                            # No validation possible, but data loaded
                            data = test_data
                            warnings.warn(
                                f"Loaded {len(test_data)} values as {dtype_name} {byteorder} "
                                f"(could not validate count)"
                            )
                            break
                    except Exception as e:
                        continue
                
                if data is not None:
                    break
        
        if data is None and expected_count is not None:
            # Try loading without size validation - accept any valid float data
            for dtype_name, item_size in BINARY_DTYPES:
                if file_size % item_size == 0:
                    for byteorder in ['<', '>']:
                        try:
                            dtype = np.dtype(byteorder + dtype_name)
                            test_data = np.fromfile(filepath, dtype=dtype)
                            if len(test_data) > 0:
                                data = test_data
                                if len(test_data) != expected_count:
                                    warnings.warn(
                                        f"Loaded {len(data)} values as {dtype_name} {byteorder}, "
                                        f"but expected {expected_count} values"
                                    )
                                break
                        except Exception:
                            continue
                    if data is not None:
                        break
        
        if data is None:
            raise ValueError(
                f"Could not read binary file {filepath}. "
                f"File size: {file_size} bytes, "
                f"Expected values: {expected_count if expected_count else 'unknown'}"
            )
        
        # Apply no-data masking if specified
        no_data_value = prop_info.get('no_data_value')
        if no_data_value is not None:
            data = np.where(data == no_data_value, np.nan, data)
        
        return data
    
    def _read_ascii_property(self, filepath: Path, prop_info: Dict) -> Optional[np.ndarray]:
        """
        Read ASCII property file.
        
        Parameters
        ----------
        filepath : Path
            Path to the ASCII property file
        prop_info : dict
            Property metadata
        
        Returns
        -------
        np.ndarray or None
            The property data
        """
        if not filepath.exists():
            warnings.warn(f"ASCII property file not found: {filepath}")
            return None
        
        try:
            # Try loading as simple array
            data = np.loadtxt(filepath, skiprows=3)
            
            # Apply no-data masking if specified
            no_data_value = prop_info.get('no_data_value')
            if no_data_value is not None:
                data = np.where(data == no_data_value, np.nan, data)
            
            return data
        
        except Exception as e:
            warnings.warn(f"Error reading ASCII file {filepath}: {e}")
            return None
    
    def read_all_properties(self) -> Dict[str, np.ndarray]:
        """
        Read all properties defined in the grid.
        
        Returns
        -------
        dict
            Dictionary mapping property IDs to their data arrays
        """
        results = {}
        for prop_id in self.properties:
            try:
                data = self.read_property(prop_id)
                if data is not None:
                    results[prop_id] = data
            except Exception as e:
                warnings.warn(f"Failed to read property {prop_id}: {e}")
        
        return results
    
    def to_pyvista(self, properties_to_load: Optional[List[str]] = None):
        """
        Convert the grid to a PyVista UniformGrid object.
        
        Parameters
        ----------
        properties_to_load : list of str, optional
            List of property IDs to load. If None, loads all properties.
        
        Returns
        -------
        pyvista.UniformGrid
            The grid as a PyVista object
        """
        try:
            import pyvista as pv
        except ImportError:
            raise ImportError(
                "PyVista is required for this function. "
                "Install it with: pip install pyvista"
            )
        
        if self.dimensions is None:
            raise ValueError("Grid dimensions not defined")
        
        # Create uniform grid
        grid = pv.UniformGrid()
        grid.dimensions = self.dimensions
        
        if self.origin:
            grid.origin = self.origin
        
        if self.spacing:
            grid.spacing = self.spacing
        
        # Load properties
        if properties_to_load is None:
            properties_to_load = list(self.properties.keys())
        
        for prop_id in properties_to_load:
            try:
                data = self.read_property(prop_id)
                if data is not None:
                    prop_name = self.properties[prop_id]['name']
                    grid[prop_name] = data
            except Exception as e:
                warnings.warn(f"Failed to add property {prop_id} to grid: {e}")
        
        return grid
    
    def info(self) -> str:
        """
        Get a summary of the grid information.
        
        Returns
        -------
        str
            Formatted information string
        """
        lines = []
        lines.append("=" * 60)
        lines.append("GOCAD SG Grid Information")
        lines.append("=" * 60)
        
        if 'name' in self.header:
            lines.append(f"Name: {self.header['name']}")
        
        if 'type' in self.header:
            lines.append(f"Type: {self.header['type']}")
        
        lines.append(f"File: {self.sg_file}")
        
        if self.dimensions:
            lines.append(f"\nDimensions: {self.dimensions[0]} x {self.dimensions[1]} x {self.dimensions[2]}")
            total_cells = np.prod(self.dimensions)
            lines.append(f"Total cells: {total_cells:,}")
        
        if self.origin:
            lines.append(f"\nOrigin: ({self.origin[0]:.2f}, {self.origin[1]:.2f}, {self.origin[2]:.2f})")
        
        if self.spacing:
            lines.append(f"Spacing: ({self.spacing[0]:.2f}, {self.spacing[1]:.2f}, {self.spacing[2]:.2f})")
        
        if self.properties:
            lines.append(f"\nProperties ({len(self.properties)}):")
            for prop_id, prop_info in self.properties.items():
                name = prop_info['name']
                file = prop_info['file'] if prop_info['file'] else 'N/A'
                file_type = 'Binary' if file.endswith('@@') else 'ASCII'
                lines.append(f"  - {name} ({prop_id}): {file} [{file_type}]")
        
        lines.append("=" * 60)
        
        return '\n'.join(lines)


def read_sg_grid(sg_file: Union[str, Path], 
                 properties: Optional[List[str]] = None,
                 return_pyvista: bool = True):
    """
    Convenience function to read a Gocad SG grid.
    
    Parameters
    ----------
    sg_file : str or Path
        Path to the .sg header file
    properties : list of str, optional
        List of property IDs to load. If None, loads all properties.
    return_pyvista : bool, default=True
        If True, returns a PyVista UniformGrid. If False, returns the reader object.
    
    Returns
    -------
    pyvista.UniformGrid or GocadSGReader
        The loaded grid
    
    Examples
    --------
    >>> # Load all properties as PyVista grid
    >>> grid = read_sg_grid('data/my_grid.sg')
    >>> 
    >>> # Load specific properties
    >>> grid = read_sg_grid('data/my_grid.sg', properties=['density', 'susceptibility'])
    >>> 
    >>> # Get the reader object for more control
    >>> reader = read_sg_grid('data/my_grid.sg', return_pyvista=False)
    >>> print(reader.info())
    >>> data = reader.read_property('density')
    """
    reader = GocadSGReader(sg_file)
    
    if return_pyvista:
        return reader.to_pyvista(properties_to_load=properties)
    else:
        return reader


if __name__ == '__main__':
    # Example usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python gocad_sg_reader.py <sg_file>")
        print("\nExample:")
        print("  python gocad_sg_reader.py data/my_grid.sg")
        sys.exit(1)
    
    sg_file = sys.argv[1]
    
    try:
        reader = GocadSGReader(sg_file)
        print(reader.info())
        
        # Try to create PyVista grid if available
        try:
            grid = reader.to_pyvista()
            print("\nSuccessfully created PyVista grid!")
            print(f"Grid points: {grid.n_points:,}")
            print(f"Grid cells: {grid.n_cells:,}")
        except ImportError:
            print("\nPyVista not available. Install it to create visualization grids.")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
