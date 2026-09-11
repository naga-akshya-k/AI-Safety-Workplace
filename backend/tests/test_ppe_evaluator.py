import pytest
from app.services.ppe_evaluator import PPEEvaluator

def test_ppe_evaluator_compliant_worker():
    worker_bbox = [100.0, 100.0, 200.0, 300.0] # w=100, h=200
    # Head region is roughly [100, 100, 200, 150]
    # Torso region is roughly [100, 130, 200, 250]
    
    detected_ppe = [
        {"label": "hardhat", "bbox": [110.0, 100.0, 190.0, 140.0], "confidence": 0.95},
        {"label": "vest", "bbox": [110.0, 140.0, 190.0, 230.0], "confidence": 0.92}
    ]
    
    result = PPEEvaluator.evaluate_worker_ppe(
        track_id=1,
        worker_bbox=worker_bbox,
        detected_ppe_items=detected_ppe,
        required_ppe=["hardhat", "vest"]
    )
    
    assert result.compliant is True
    assert len(result.missing_items) == 0
    assert "hardhat" in result.detected_items
    assert "vest" in result.detected_items

def test_ppe_evaluator_hardhat_carried_in_hand_rejected():
    """
    Industrial edge case:
    Worker is carrying a hardhat in hand (located near hip/leg level [100, 220, 140, 260]).
    Spatial validation must reject it as NOT worn on head!
    """
    worker_bbox = [100.0, 100.0, 200.0, 300.0]
    
    detected_ppe = [
        # Hardhat in hand at bottom-left of worker
        {"label": "hardhat", "bbox": [100.0, 220.0, 140.0, 260.0], "confidence": 0.90},
        {"label": "vest", "bbox": [110.0, 140.0, 190.0, 230.0], "confidence": 0.92}
    ]
    
    result = PPEEvaluator.evaluate_worker_ppe(
        track_id=2,
        worker_bbox=worker_bbox,
        detected_ppe_items=detected_ppe,
        required_ppe=["hardhat", "vest"]
    )
    
    assert result.compliant is False
    assert "hardhat" in result.missing_items
    assert "vest" in result.detected_items
