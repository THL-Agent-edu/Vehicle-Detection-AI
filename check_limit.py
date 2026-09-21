from fastapi.testclient import TestClient
from src.backend.app import app

client = TestClient(app)
response = client.get('/settings')
print(response.status_code)
print(response.json()['maxFileSize'])
