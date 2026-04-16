import pytest
from unittest.mock import patch, MagicMock

from app.github_handler import get_pr_diff
from app.ollama_reviewer import review_code

@patch('app.github_handler.g')
def test_get_pr_diff(mock_g):
    """
    Mock the GitHub API and assert get_pr_diff returns the right format.
    """
    # Setup mocks
    mock_repo = MagicMock()
    mock_pr = MagicMock()
    
    mock_file1 = MagicMock()
    mock_file1.filename = "app/main.py"
    mock_file1.patch = "@@ -1,3 +1,4 @@\n+import os\n"
    
    mock_file2 = MagicMock()
    mock_file2.filename = "README.md"
    mock_file2.patch = None # Simulate binary or renamed file lacking a patch
    
    mock_pr.get_files.return_value = [mock_file1, mock_file2]
    mock_repo.get_pull.return_value = mock_pr
    mock_g.get_repo.return_value = mock_repo

    # Execute
    diff_text = get_pr_diff("Kush05Bhardwaj/PRobot", 42)

    # Assert
    expected_result = "\nFile: app/main.py\n@@ -1,3 +1,4 @@\n+import os\n\nFile: README.md\n"
    assert diff_text == expected_result
    mock_g.get_repo.assert_called_once_with("Kush05Bhardwaj/PRobot")
    mock_repo.get_pull.assert_called_once_with(42)
    mock_pr.get_files.assert_called_once()

@patch('app.ollama_reviewer.requests.post')
def test_review_code(mock_post):
    """
    Mock Ollama's HTTP response and assert review_code parses it correctly.
    """
    # Setup mocks
    mock_response = MagicMock()
    mock_response.json.return_value = {"response": "🤖 PRobot Review\n\nLooks LGTM!"}
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    # Execute
    fake_diff = "\nFile: app/main.py\n+import os\n"
    review = review_code(fake_diff)

    # Assert
    assert review == "🤖 PRobot Review\n\nLooks LGTM!"
    
    mock_post.assert_called_once()
    
    # Assert we sent the correct payload parameters to the mocked Ollama server
    _, kwargs = mock_post.call_args
    assert "json" in kwargs
    assert kwargs["json"]["stream"] is False
    assert fake_diff in kwargs["json"]["prompt"]
    assert "timeout" in kwargs
