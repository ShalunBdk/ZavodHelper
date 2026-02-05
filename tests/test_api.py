"""API tests."""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, engine

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    """Setup test database."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_health_check():
    """Test health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_get_empty_items():
    """Test getting items when DB is empty."""
    response = client.get("/api/items")
    assert response.status_code == 200
    assert response.json() == []


def test_create_incident():
    """Test creating an incident."""
    data = {
        "title": "Test Incident",
        "item_type": "incident",
        "pages": [
            {
                "title": "Page 1",
                "time": "5 minutes",
                "image": "",
                "actions": ["Action 1", "Action 2"]
            }
        ]
    }
    response = client.post("/api/items", json=data)
    assert response.status_code == 201
    result = response.json()
    assert result["title"] == "Test Incident"
    assert result["item_type"] == "incident"
    assert len(result["pages"]) == 1


def test_create_instruction():
    """Test creating an instruction."""
    data = {
        "title": "Test Instruction",
        "item_type": "instruction",
        "pages": [
            {
                "title": "Step 1",
                "time": "10 minutes",
                "image": "",
                "actions": ["Do this", "Then that"]
            }
        ]
    }
    response = client.post("/api/items", json=data)
    assert response.status_code == 201
    result = response.json()
    assert result["item_type"] == "instruction"


def test_get_item():
    """Test getting a single item."""
    # Create first
    data = {
        "title": "Get Test",
        "item_type": "incident",
        "pages": [{"title": "P1", "time": "1m", "actions": ["A1"]}]
    }
    create_response = client.post("/api/items", json=data)
    item_id = create_response.json()["id"]

    # Get
    response = client.get(f"/api/items/{item_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Get Test"


def test_update_item():
    """Test updating an item."""
    # Create
    data = {
        "title": "Original",
        "item_type": "incident",
        "pages": [{"title": "P1", "time": "1m", "actions": ["A1"]}]
    }
    create_response = client.post("/api/items", json=data)
    item_id = create_response.json()["id"]

    # Update
    update_data = {"title": "Updated"}
    response = client.put(f"/api/items/{item_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["title"] == "Updated"


def test_delete_item():
    """Test deleting an item."""
    # Create
    data = {
        "title": "To Delete",
        "item_type": "incident",
        "pages": [{"title": "P1", "time": "1m", "actions": ["A1"]}]
    }
    create_response = client.post("/api/items", json=data)
    item_id = create_response.json()["id"]

    # Delete
    response = client.delete(f"/api/items/{item_id}")
    assert response.status_code == 200

    # Verify deleted
    get_response = client.get(f"/api/items/{item_id}")
    assert get_response.status_code == 404


def test_search_items():
    """Test searching items."""
    # Create items
    client.post("/api/items", json={
        "title": "Alpha Incident",
        "item_type": "incident",
        "pages": [{"title": "P1", "time": "1m", "actions": ["A1"]}]
    })
    client.post("/api/items", json={
        "title": "Beta Instruction",
        "item_type": "instruction",
        "pages": [{"title": "P1", "time": "1m", "actions": ["A1"]}]
    })

    # Search
    response = client.get("/api/items/search?q=Alpha")
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["title"] == "Alpha Incident"


def test_export_import():
    """Test export and import functionality."""
    # Create data
    client.post("/api/items", json={
        "title": "Export Test",
        "item_type": "incident",
        "pages": [{"title": "P1", "time": "1m", "actions": ["A1"]}]
    })

    # Export
    export_response = client.get("/api/export")
    assert export_response.status_code == 200
    export_data = export_response.json()
    assert len(export_data["incidents"]) == 1

    # Clear
    client.delete("/api/clear?confirm=true")

    # Import
    import_response = client.post("/api/import", json=export_data)
    assert import_response.status_code == 200

    # Verify
    items_response = client.get("/api/items")
    assert len(items_response.json()) == 1


def test_get_incidents():
    """Test getting only incidents."""
    client.post("/api/items", json={
        "title": "Inc1",
        "item_type": "incident",
        "pages": [{"title": "P1", "time": "1m", "actions": ["A1"]}]
    })
    client.post("/api/items", json={
        "title": "Ins1",
        "item_type": "instruction",
        "pages": [{"title": "P1", "time": "1m", "actions": ["A1"]}]
    })

    response = client.get("/api/incidents")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Inc1"


def test_get_instructions():
    """Test getting only instructions."""
    client.post("/api/items", json={
        "title": "Inc1",
        "item_type": "incident",
        "pages": [{"title": "P1", "time": "1m", "actions": ["A1"]}]
    })
    client.post("/api/items", json={
        "title": "Ins1",
        "item_type": "instruction",
        "pages": [{"title": "P1", "time": "1m", "actions": ["A1"]}]
    })

    response = client.get("/api/instructions")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Ins1"
