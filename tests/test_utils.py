import pytest
from app.utils import calculate_plates, calculate_warmups

def test_calculate_plates_135():
    # Target 135 -> 45 per side -> one 45 plate
    # Expected output should NOT include "2x45"
    result = calculate_plates(135.0, [45, 35, 25, 10, 5, 2.5])
    print(f"Result for 135: {result}")
    assert "2×45" not in result
    assert "45" in result 
    # Exact format is "bar \n 45"

def test_calculate_plates_225():
    # Target 225 -> 90 per side -> two 45 plates
    result = calculate_plates(225.0, [45, 25, 10, 5, 2.5])
    assert "2×45" in result

def test_calculate_plates_315():
    # Target 315 -> 135 per side -> three 45 plates
    result = calculate_plates(315.0, [45, 25, 10, 5, 2.5])
    print(f"Result for 315: {result}")
    assert "3×45" in result

def test_calculate_plates_405():
    # Target 405 -> 180 per side -> four 45 plates
    result = calculate_plates(405.0, [45, 25, 10, 5, 2.5])
    print(f"Result for 405: {result}")
    assert "4×45" in result

def test_calculate_plates_inventory_insufficient():
    # Target 315 -> 135 per side -> three 45 plates
    # BUT user only has ONE pair of 45s
    inventory = {45: 1, 25: 2, 10: 2, 5: 2, 2.5: 2}
    result = calculate_plates(315.0, inventory)
    # The math should still show 3x45 but flag what's missing
    # Format choice: "3×45 (MISSING 2)"
    assert "3×45" in result
    assert "MISSING 2" in result
