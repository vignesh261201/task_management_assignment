import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from project.main import app, get_db
from project import models


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

models.Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_database():
    models.Base.metadata.create_all(bind=engine)
    yield
    models.Base.metadata.drop_all(bind=engine)

def test_create_user(setup_database):
    response = client.post("/users/", json={"name": "Vignesh", "email": "vignesh@gmail.com"})
    assert response.status_code == 200
    assert response.json()["name"] == "Vignesh"
    assert response.json()["email"] == "vignesh@gmail.com"

def test_get_user(setup_database):
    response = client.post("/users/", json={"name": "Charan", "email": "charan@gmail.com"})
    user_id = response.json()["id"]
    response = client.get(f"/users/{user_id}/")
    assert response.status_code == 200
    assert response.json()["name"] == "Charan"
    assert response.json()["email"] == "charan@gmail.com"

def test_list_users(setup_database):
    response = client.get("/users/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_task(setup_database):
    response = client.post("/tasks/", json={"title": "Test Task", "description": "Test Description", "user_id": 1})
    assert response.status_code == 200
    assert response.json()["title"] == "Test Task"
    assert response.json()["description"] == "Test Description"

def test_get_task(setup_database):
    response = client.post("/tasks/", json={"title": "Another Task", "description": "Another Description", "user_id": 1})
    task_id = response.json()["id"]
    response = client.get(f"/tasks/{task_id}/")
    assert response.status_code == 200
    assert response.json()["title"] == "Another Task"
    assert response.json()["description"] == "Another Description"

def test_list_tasks(setup_database):
    response = client.get("/tasks/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_update_task(setup_database):
    response = client.post("/tasks/", json={"title": "Update Task", "description": "Update Description", "user_id": 1})
    task_id = response.json()["id"]
    response = client.put(f"/tasks/{task_id}/", json={"title": "Updated Task", "description": "Updated Description"})
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Task"
    assert response.json()["description"] == "Updated Description"

def test_delete_task(setup_database):
    response = client.post("/tasks/", json={"title": "Delete Task", "description": "Delete Description", "user_id": 1})
    task_id = response.json()["id"]
    response = client.delete(f"/tasks/{task_id}/")
    assert response.status_code == 200
    assert response.json()["title"] == "Delete Task"
    assert response.json()["description"] == "Delete Description"