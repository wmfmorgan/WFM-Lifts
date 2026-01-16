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
    assert "3×45" in result
