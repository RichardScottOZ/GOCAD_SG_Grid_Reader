#!/usr/bin/env python
"""
Example usage of the improved Gocad SG Grid reader.

This script demonstrates various ways to use the gocad_sg_reader module
for reading and processing Gocad SG grid files.
"""

import sys
from pathlib import Path
import numpy as np

# Import the reader
from gocad_sg_reader import GocadSGReader, read_sg_grid


def example_basic_usage(sg_file):
    """Basic usage example."""
    print("\n" + "=" * 60)
    print("EXAMPLE 1: Basic Usage")
    print("=" * 60)
    
    # Create reader
    reader = GocadSGReader(sg_file)
    
    # Display grid information
    print(reader.info())
    
    # Read a specific property
    if reader.properties:
        first_prop_id = list(reader.properties.keys())[0]
        print(f"\nReading property: {first_prop_id}")
        data = reader.read_property(first_prop_id)
        print(f"Data shape: {data.shape}")
        print(f"Data range: [{np.nanmin(data):.3f}, {np.nanmax(data):.3f}]")


def example_pyvista_grid(sg_file):
    """Example using PyVista for visualization."""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: PyVista Grid Creation")
    print("=" * 60)
    
    try:
        # Quick way to load as PyVista grid
        grid = read_sg_grid(sg_file)
        
        print(f"Created PyVista UniformGrid:")
        print(f"  Dimensions: {grid.dimensions}")
        print(f"  Origin: {grid.origin}")
        print(f"  Spacing: {grid.spacing}")
        print(f"  Number of points: {grid.n_points:,}")
        print(f"  Number of cells: {grid.n_cells:,}")
        print(f"  Properties: {list(grid.array_names)}")
        
        # You can now use PyVista plotting
        # grid.plot() or grid.save('output.vtu')
        
    except ImportError:
        print("PyVista not installed. Install with: pip install pyvista")


def example_property_analysis(sg_file):
    """Example analyzing property data."""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Property Data Analysis")
    print("=" * 60)
    
    reader = GocadSGReader(sg_file)
    
    # Read all properties
    all_data = reader.read_all_properties()
    
    print(f"Loaded {len(all_data)} properties\n")
    
    # Analyze each property
    for prop_id, data in all_data.items():
        prop_name = reader.properties[prop_id]['name']
        
        valid_data = data[~np.isnan(data)]
        
        print(f"{prop_name}:")
        print(f"  Total values: {data.size:,}")
        print(f"  Valid values: {len(valid_data):,}")
        
        if len(valid_data) > 0:
            print(f"  Range: [{np.min(valid_data):.3f}, {np.max(valid_data):.3f}]")
            print(f"  Mean: {np.mean(valid_data):.3f}")
            print(f"  Std: {np.std(valid_data):.3f}")
        print()


def example_export_vtk(sg_file, output_file='output.vtu'):
    """Example exporting to VTK format."""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Export to VTK")
    print("=" * 60)
    
    try:
        from gocad_utils import export_to_vtk
        
        reader = GocadSGReader(sg_file)
        
        # Export to VTU format
        output_path = export_to_vtk(reader, output_file, file_format='vtu')
        
        print(f"Exported grid to: {output_path}")
        print(f"File size: {output_path.stat().st_size / 1024 / 1024:.2f} MB")
        
    except ImportError:
        print("PyVista required for VTK export. Install with: pip install pyvista")


def example_selective_loading(sg_file):
    """Example loading specific properties."""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Selective Property Loading")
    print("=" * 60)
    
    reader = GocadSGReader(sg_file)
    
    # Show available properties
    print("Available properties:")
    for prop_id, prop_info in reader.properties.items():
        print(f"  - {prop_id}: {prop_info['name']}")
    
    # Load only specific properties
    if len(reader.properties) > 0:
        # Get first property ID
        prop_ids = list(reader.properties.keys())
        selected = prop_ids[:min(2, len(prop_ids))]  # Select up to 2 properties
        
        print(f"\nLoading selected properties: {selected}")
        
        for prop_id in selected:
            data = reader.read_property(prop_id)
            print(f"  Loaded {prop_id}: {data.shape}")


def example_statistics(sg_file):
    """Example computing statistics."""
    print("\n" + "=" * 60)
    print("EXAMPLE 6: Grid Statistics")
    print("=" * 60)
    
    try:
        from gocad_utils import summarize_grid_statistics
        
        reader = GocadSGReader(sg_file)
        stats = summarize_grid_statistics(reader)
        
        print("Property Statistics:\n")
        for prop_name, prop_stats in stats.items():
            print(f"{prop_name}:")
            for key, value in prop_stats.items():
                if isinstance(value, float):
                    print(f"  {key}: {value:.6f}")
                else:
                    print(f"  {key}: {value}")
            print()
    
    except ImportError as e:
        print(f"Could not import utilities: {e}")


def main():
    """Main function demonstrating all examples."""
    
    if len(sys.argv) < 2:
        print("Gocad SG Grid Reader - Example Usage")
        print("=" * 60)
        print("\nUsage: python example_usage.py <sg_file> [output_file]")
        print("\nArguments:")
        print("  sg_file      Path to the .sg header file (required)")
        print("  output_file  Path for VTK export (optional, default: output.vtu)")
        print("\nExamples:")
        print("  python example_usage.py data/my_grid.sg")
        print("  python example_usage.py data/my_grid.sg exported_grid.vtu")
        print("\nThis script will demonstrate:")
        print("  1. Basic usage and grid information")
        print("  2. Creating PyVista grids")
        print("  3. Property data analysis")
        print("  4. Exporting to VTK format")
        print("  5. Selective property loading")
        print("  6. Computing grid statistics")
        return
    
    sg_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'output.vtu'
    
    if not Path(sg_file).exists():
        print(f"Error: File not found: {sg_file}")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("GOCAD SG GRID READER - EXAMPLE DEMONSTRATIONS")
    print("=" * 60)
    print(f"\nInput file: {sg_file}")
    print(f"Output file: {output_file}")
    
    try:
        # Run all examples
        example_basic_usage(sg_file)
        example_pyvista_grid(sg_file)
        example_property_analysis(sg_file)
        example_export_vtk(sg_file, output_file)
        example_selective_loading(sg_file)
        example_statistics(sg_file)
        
        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
