from fastapi.testclient import TestClient
from unittest.mock import patch
from app import app

client = TestClient(app)

def test_generate_quiz_validation():
    # Mock response with invalid correct_index
    from app import app
    
    mock_data = {
        "questions": [
            {
                "question": "Test Q1",
                "options": ["A", "B", "C"],
                "correct_index": 5, # Invalid index
                "topic": "Test"
            },
            {
                "question": "Test Q2",
                "options": ["X", "Y"],
                "correct_index": 1, # Valid index
                "topic": "Test"
            }
        ]
    }

    with patch('app.call_ollama', return_value=mock_data):
        response = client.post("/generate-quiz", json={"text": "dummy text"})
        assert response.status_code == 200
        data = response.json()
        
        # Check validation
        assert len(data) == 2
        
        # Q1 should be fixed (index 5 -> 0). Wait, my logic sets it to 0.
        assert data[0]["correct_index"] == 0
        
        # Q2 should remain same
        assert data[1]["correct_index"] == 1
        
        print("Test Passed: Invalid correct_index was fixed!")

if __name__ == "__main__":
    test_generate_quiz_validation()
