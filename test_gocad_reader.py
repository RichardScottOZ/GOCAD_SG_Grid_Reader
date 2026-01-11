#!/usr/bin/env python
"""
Basic tests for the Gocad SG Grid reader.

This test file validates the core functionality without requiring actual
Gocad data files by creating mock data and testing the parsing logic.
"""

import tempfile
import shutil
from pathlib import Path
import numpy as np


def create_mock_sg_file(output_dir: Path) -> Path:
    """
    Create a mock .sg file for testing.
    
    Returns the path to the created .sg file.
    """
    sg_content = """GOCAD SGrid 1
HEADER {
name:Test Grid
}
NAME "Test_Grid"
AXIS_N 10 20 5
AXIS_O 0.0 0.0 0.0
AXIS_U 1000.0 0.0 0.0
AXIS_V 0.0 2000.0 0.0
AXIS_W 0.0 0.0 500.0
AXIS_MIN 0.0 0.0 0.0
AXIS_MAX 10.0 20.0 5.0
PROPERTY 1 "density"
PROP_FILE 1 "test_density@@"
PROP_NO_DATA_VALUE 1 -99999.0
PROPERTY 2 "temperature"
PROP_FILE 2 "test_temperature"
END
"""
    sg_file = output_dir / "test_grid.sg"
    sg_file.write_text(sg_content)
    return sg_file


def create_mock_binary_property(output_dir: Path, dimensions: tuple) -> Path:
    """
    Create a mock binary property file (@@).
    
    Returns the path to the created file.
    """
    # Create test data
    total_cells = np.prod(dimensions)
    data = np.random.random(total_cells).astype(np.float32)
    
    binary_file = output_dir / "test_density@@"
    data.tofile(binary_file)
    return binary_file


def create_mock_ascii_property(output_dir: Path, dimensions: tuple) -> Path:
    """
    Create a mock ASCII property file.
    
    Returns the path to the created file.
    """
    # Create test data
    total_cells = np.prod(dimensions)
    data = np.random.random(total_cells)
    
    ascii_file = output_dir / "test_temperature"
    
    # Write with header (3 rows to skip)
    with open(ascii_file, 'w') as f:
        f.write("# Test temperature data\n")
        f.write("# Generated for testing\n")
        f.write("# Values follow\n")
        for value in data:
            f.write(f"{value}\n")
    
    return ascii_file


def test_header_parsing():
    """Test parsing of .sg header file."""
    print("\n" + "=" * 60)
    print("TEST 1: Header Parsing")
    print("=" * 60)
    
    temp_dir = Path(tempfile.mkdtemp())
    
    try:
        # Create mock files
        sg_file = create_mock_sg_file(temp_dir)
        
        # Import here to avoid issues if module has errors
        from gocad_sg_reader import GocadSGReader
        
        # Create reader
        reader = GocadSGReader(sg_file)
        
        # Validate header parsing
        assert reader.dimensions == (10, 20, 5), f"Expected dimensions (10, 20, 5), got {reader.dimensions}"
        assert reader.origin == (0.0, 0.0, 0.0), f"Expected origin (0.0, 0.0, 0.0), got {reader.origin}"
        assert len(reader.properties) == 2, f"Expected 2 properties, got {len(reader.properties)}"
        assert '1' in reader.properties, "Property '1' not found"
        assert '2' in reader.properties, "Property '2' not found"
        assert reader.properties['1']['name'] == 'density', "Property name mismatch"
        
        print("✓ Header parsed correctly")
        print(f"✓ Dimensions: {reader.dimensions}")
        print(f"✓ Origin: {reader.origin}")
        print(f"✓ Properties: {len(reader.properties)}")
        
        return True
    
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_binary_reading():
    """Test reading binary property files."""
    print("\n" + "=" * 60)
    print("TEST 2: Binary Property Reading")
    print("=" * 60)
    
    temp_dir = Path(tempfile.mkdtemp())
    
    try:
        # Create mock files
        dimensions = (10, 20, 5)
        sg_file = create_mock_sg_file(temp_dir)
        binary_file = create_mock_binary_property(temp_dir, dimensions)
        
        from gocad_sg_reader import GocadSGReader
        
        # Create reader
        reader = GocadSGReader(sg_file)
        
        # Read binary property
        data = reader.read_property('1')
        
        # Validate
        expected_size = np.prod(dimensions)
        assert data is not None, "Binary data is None"
        assert len(data) == expected_size, f"Expected {expected_size} values, got {len(data)}"
        assert data.dtype in [np.float32, np.float64], f"Unexpected data type: {data.dtype}"
        
        print("✓ Binary file read successfully")
        print(f"✓ Data shape: {data.shape}")
        print(f"✓ Data type: {data.dtype}")
        print(f"✓ Data range: [{np.min(data):.6f}, {np.max(data):.6f}]")
        
        return True
    
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_ascii_reading():
    """Test reading ASCII property files."""
    print("\n" + "=" * 60)
    print("TEST 3: ASCII Property Reading")
    print("=" * 60)
    
    temp_dir = Path(tempfile.mkdtemp())
    
    try:
        # Create mock files
        dimensions = (10, 20, 5)
        sg_file = create_mock_sg_file(temp_dir)
        ascii_file = create_mock_ascii_property(temp_dir, dimensions)
        
        from gocad_sg_reader import GocadSGReader
        
        # Create reader
        reader = GocadSGReader(sg_file)
        
        # Read ASCII property
        data = reader.read_property('2')
        
        # Validate
        expected_size = np.prod(dimensions)
        assert data is not None, "ASCII data is None"
        assert len(data) == expected_size, f"Expected {expected_size} values, got {len(data)}"
        
        print("✓ ASCII file read successfully")
        print(f"✓ Data shape: {data.shape}")
        print(f"✓ Data type: {data.dtype}")
        print(f"✓ Data range: [{np.min(data):.6f}, {np.max(data):.6f}]")
        
        return True
    
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_info_method():
    """Test the info() method."""
    print("\n" + "=" * 60)
    print("TEST 4: Info Method")
    print("=" * 60)
    
    temp_dir = Path(tempfile.mkdtemp())
    
    try:
        # Create mock files
        sg_file = create_mock_sg_file(temp_dir)
        
        from gocad_sg_reader import GocadSGReader
        
        # Create reader
        reader = GocadSGReader(sg_file)
        
        # Get info
        info_str = reader.info()
        
        # Validate
        assert info_str is not None, "Info string is None"
        assert len(info_str) > 0, "Info string is empty"
        assert "Test_Grid" in info_str or "Test Grid" in info_str, "Grid name not in info"
        assert "10 x 20 x 5" in info_str, "Dimensions not in info"
        
        print("✓ Info method works correctly")
        print("\nGenerated info:")
        print(info_str)
        
        return True
    
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_pyvista_integration():
    """Test PyVista integration (if available)."""
    print("\n" + "=" * 60)
    print("TEST 5: PyVista Integration")
    print("=" * 60)
    
    try:
        import pyvista as pv
    except ImportError:
        print("⊘ PyVista not installed - skipping this test")
        return True
    
    temp_dir = Path(tempfile.mkdtemp())
    
    try:
        # Create mock files
        dimensions = (10, 20, 5)
        sg_file = create_mock_sg_file(temp_dir)
        binary_file = create_mock_binary_property(temp_dir, dimensions)
        
        from gocad_sg_reader import GocadSGReader
        
        # Create reader
        reader = GocadSGReader(sg_file)
        
        # Convert to PyVista
        grid = reader.to_pyvista(properties_to_load=['1'])
        
        # Validate
        assert grid is not None, "PyVista grid is None"
        assert isinstance(grid, pv.UniformGrid), f"Expected UniformGrid, got {type(grid)}"
        assert grid.dimensions == (10, 20, 5), f"Expected dimensions (10, 20, 5), got {grid.dimensions}"
        assert 'density' in grid.array_names, "Property 'density' not in grid"
        
        print("✓ PyVista integration works correctly")
        print(f"✓ Grid type: {type(grid).__name__}")
        print(f"✓ Grid dimensions: {grid.dimensions}")
        print(f"✓ Number of points: {grid.n_points:,}")
        print(f"✓ Number of cells: {grid.n_cells:,}")
        print(f"✓ Properties: {grid.array_names}")
        
        return True
    
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("GOCAD SG GRID READER - TEST SUITE")
    print("=" * 60)
    
    tests = [
        test_header_parsing,
        test_binary_reading,
        test_ascii_reading,
        test_info_method,
        test_pyvista_integration,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n✗ Test {test.__name__} crashed: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nTests passed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ All tests passed!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(run_all_tests())
