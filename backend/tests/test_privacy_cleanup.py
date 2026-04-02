import pytest
import os
import gc
import psutil
from fastapi.testclient import TestClient
from main import app
from app.core.privacy import PrivacyManager

client = TestClient(app)

def get_process_memory():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)  # MB

def test_memory_cleanup_after_analysis():
    """Verify that memory returns to near-baseline after a large analysis."""
    
    # Baseline
    gc.collect()
    baseline_mem = get_process_memory()
    
    # Generate a medium-sized chat (approx 1MB of text)
    large_chat = ""
    for i in range(10000):
        # Format needs to match Android Whatsapp parsing `dd/mm/yyyy, HH:MM - Sender: message`
        large_chat += f"12/03/24, 10:00:{i%60:02d} - User: This is message number {i}. It adds a bit of weight to the memory.\n"
    
    # Run analysis
    response = client.post("/api/v1/analyze/text", json={"text": large_chat})
    assert response.status_code == 200
    
    # Wait for middleware/gc
    gc.collect()
    post_analysis_mem = get_process_memory()
    
    # Memory should not have leaked significantly (allowing some for Python standard overhead)
    # If it leaked, post_analysis_mem would be much larger than baseline
    # Usually within 5-10MB is fine for overhead/fragmentation
    diff = post_analysis_mem - baseline_mem
    print(f"Memory Diff: {diff:.2f} MB (Baseline: {baseline_mem:.2f}, Post: {post_analysis_mem:.2f})")
    
    assert diff < 20, f"Potential memory leak detected: {diff:.2f} MB"

def test_no_temp_files_left():
    """Verify no temporary files are created or left in the directory."""
    initial_files = set(os.listdir('.'))
    
    # Run a file analysis
    content = b"[12/03/24, 10:00:00] User: Test message\n"
    response = client.post(
        "/api/v1/analyze/file", 
        files={"file": ("test.txt", content, "text/plain")}
    )
    assert response.status_code == 200
    
    final_files = set(os.listdir('.'))
    assert initial_files == final_files, "Temporary files were created and not deleted!"
