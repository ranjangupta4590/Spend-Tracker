from datetime import date
import pytest


def test_create_valid_expense(client):
    payload = {
        "amount": 450.50,
        "category": "Food",
        "note": "Lunch with team",
        "date": "2026-09-22",
    }
    response = client.post("/expenses", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["amount"] == 450.50
    assert data["category"] == "Food"
    assert data["note"] == "Lunch with team"
    assert data["date"] == "2026-09-22"
    assert "created_at" in data


def test_create_expense_zero_amount(client):
    payload = {
        "amount": 0.00,
        "category": "Food",
        "note": "Free lunch",
        "date": "2026-09-22",
    }
    response = client.post("/expenses", json=payload)
    assert response.status_code == 422


def test_create_expense_negative_amount(client):
    payload = {
        "amount": -15.00,
        "category": "Food",
        "date": "2026-09-22",
    }
    response = client.post("/expenses", json=payload)
    assert response.status_code == 422


def test_create_expense_missing_category(client):
    payload = {
        "amount": 50.00,
        "date": "2026-09-22",
    }
    response = client.post("/expenses", json=payload)
    assert response.status_code == 422


def test_create_expense_empty_or_whitespace_category(client):
    payload = {
        "amount": 50.00,
        "category": "   ",
        "date": "2026-09-22",
    }
    response = client.post("/expenses", json=payload)
    assert response.status_code == 422


def test_create_expense_invalid_date(client):
    payload = {
        "amount": 50.00,
        "category": "Travel",
        "date": "2026-02-31",
    }
    response = client.post("/expenses", json=payload)
    assert response.status_code == 422


def test_create_expense_category_length_exceeded(client):
    payload = {
        "amount": 50.00,
        "category": "A" * 51,
        "date": "2026-09-22",
    }
    response = client.post("/expenses", json=payload)
    assert response.status_code == 422


def test_create_expense_note_length_exceeded(client):
    payload = {
        "amount": 50.00,
        "category": "Office",
        "note": "X" * 256,
        "date": "2026-09-22",
    }
    response = client.post("/expenses", json=payload)
    assert response.status_code == 422


def test_list_expenses_empty(client):
    response = client.get("/expenses")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0
    assert data["page"] == 1
    assert data["total_pages"] == 1


def test_list_expenses_deterministic_ordering(client):
    client.post("/expenses", json={"amount": 10.0, "category": "A", "date": "2026-09-01"})
    client.post("/expenses", json={"amount": 20.0, "category": "B", "date": "2026-09-03"})
    client.post("/expenses", json={"amount": 30.0, "category": "C", "date": "2026-09-02"})

    response = client.get("/expenses")
    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) == 3
    # Most recent date first
    assert items[0]["date"] == "2026-09-03"
    assert items[1]["date"] == "2026-09-02"
    assert items[2]["date"] == "2026-09-01"


def test_filter_by_category(client):
    client.post("/expenses", json={"amount": 10.0, "category": "Food", "date": "2026-09-01"})
    client.post("/expenses", json={"amount": 20.0, "category": "Travel", "date": "2026-09-02"})
    client.post("/expenses", json={"amount": 30.0, "category": "Food", "date": "2026-09-03"})

    response = client.get("/expenses?category=Food")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert all(item["category"] == "Food" for item in data["items"])


def test_filter_by_date_range(client):
    client.post("/expenses", json={"amount": 10.0, "category": "Food", "date": "2026-08-25"})
    client.post("/expenses", json={"amount": 20.0, "category": "Food", "date": "2026-09-10"})
    client.post("/expenses", json={"amount": 30.0, "category": "Food", "date": "2026-09-20"})
    client.post("/expenses", json={"amount": 40.0, "category": "Food", "date": "2026-10-01"})

    response = client.get("/expenses?start_date=2026-09-01&end_date=2026-09-30")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert {item["amount"] for item in data["items"]} == {20.0, 30.0}


def test_filter_invalid_date_range(client):
    response = client.get("/expenses?start_date=2026-09-30&end_date=2026-09-01")
    assert response.status_code == 400
    assert "start_date must be on or before end_date" in response.json()["detail"]


def test_pagination(client):
    for i in range(1, 26):
        client.post("/expenses", json={
            "amount": float(i * 10),
            "category": "Office",
            "date": "2026-09-15",
            "note": f"Item {i}",
        })

    # Page 1
    p1 = client.get("/expenses?page=1&page_size=10").json()
    assert len(p1["items"]) == 10
    assert p1["total"] == 25
    assert p1["total_pages"] == 3

    # Page 2
    p2 = client.get("/expenses?page=2&page_size=10").json()
    assert len(p2["items"]) == 10

    # Page 3
    p3 = client.get("/expenses?page=3&page_size=10").json()
    assert len(p3["items"]) == 5
