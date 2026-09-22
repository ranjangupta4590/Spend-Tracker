def test_idempotent_retry_returns_cached_expense(client):
    idempotency_key = "unique-key-12345"
    payload = {
        "amount": 250.00,
        "category": "Travel",
        "note": "Train ticket",
        "date": "2026-09-22",
    }

    # First request creates resource
    res1 = client.post("/expenses", json=payload, headers={"Idempotency-Key": idempotency_key})
    assert res1.status_code == 201
    data1 = res1.json()

    # Second request with identical key and payload replays response
    res2 = client.post("/expenses", json=payload, headers={"Idempotency-Key": idempotency_key})
    assert res2.status_code == 201
    data2 = res2.json()

    assert data1["id"] == data2["id"]
    assert data1["amount"] == data2["amount"]

    # Verify only one expense was created in database
    list_res = client.get("/expenses")
    assert list_res.json()["total"] == 1


def test_idempotent_conflict_with_different_payload(client):
    idempotency_key = "unique-key-conflict-999"
    payload1 = {
        "amount": 100.00,
        "category": "Food",
        "date": "2026-09-22",
    }
    payload2 = {
        "amount": 200.00,  # Different amount!
        "category": "Food",
        "date": "2026-09-22",
    }

    res1 = client.post("/expenses", json=payload1, headers={"Idempotency-Key": idempotency_key})
    assert res1.status_code == 201

    res2 = client.post("/expenses", json=payload2, headers={"Idempotency-Key": idempotency_key})
    assert res2.status_code == 409
    assert "different request payload" in res2.json()["detail"]

    # Only first expense exists
    list_res = client.get("/expenses")
    assert list_res.json()["total"] == 1


def test_idempotency_key_exceeding_max_length(client):
    long_key = "K" * 129
    payload = {
        "amount": 50.00,
        "category": "Food",
        "date": "2026-09-22",
    }
    response = client.post("/expenses", json=payload, headers={"Idempotency-Key": long_key})
    assert response.status_code == 400
    assert "Idempotency-Key must not exceed 128 characters" in response.json()["detail"]
