def test_summary_empty(client):
    response = client.get("/summary?year=2026&month=9")
    assert response.status_code == 200
    data = response.json()
    assert data["total_spend"] == 0.0
    assert data["transaction_count"] == 0
    assert data["spend_by_category"] == {}
    assert data["month_over_month"]["current_month"] == 0.0
    assert data["month_over_month"]["previous_month"] == 0.0
    assert data["month_over_month"]["change_percent"] == 0.0


def test_summary_current_month_aggregation(client):
    client.post("/expenses", json={"amount": 4000.00, "category": "Food", "date": "2026-09-05"})
    client.post("/expenses", json={"amount": 3000.00, "category": "Transport", "date": "2026-09-12"})
    client.post("/expenses", json={"amount": 5000.00, "category": "Shopping", "date": "2026-09-20"})

    response = client.get("/summary?year=2026&month=9")
    assert response.status_code == 200
    data = response.json()
    assert data["total_spend"] == 12000.00
    assert data["transaction_count"] == 3
    assert data["spend_by_category"]["Food"] == 4000.00
    assert data["spend_by_category"]["Transport"] == 3000.00
    assert data["spend_by_category"]["Shopping"] == 5000.00
    assert data["category_percentages"]["Food"] == 33.3
    assert data["category_percentages"]["Transport"] == 25.0
    assert data["category_percentages"]["Shopping"] == 41.7


def test_summary_mom_calculation(client):
    # Previous month (August 2026)
    client.post("/expenses", json={"amount": 10000.00, "category": "Operations", "date": "2026-08-15"})
    # Current month (September 2026)
    client.post("/expenses", json={"amount": 12000.00, "category": "Operations", "date": "2026-09-15"})

    response = client.get("/summary?year=2026&month=9")
    assert response.status_code == 200
    data = response.json()
    mom = data["month_over_month"]
    assert mom["previous_month"] == 10000.00
    assert mom["current_month"] == 12000.00
    assert mom["change_percent"] == 20.0


def test_summary_previous_month_zero_safe(client):
    # Only current month has expenses, previous month has $0
    client.post("/expenses", json={"amount": 5000.00, "category": "Software", "date": "2026-09-10"})

    response = client.get("/summary?year=2026&month=9")
    assert response.status_code == 200
    data = response.json()
    mom = data["month_over_month"]
    assert mom["previous_month"] == 0.00
    assert mom["current_month"] == 5000.00
    # Undefined growth represented as None / null, zero division prevented
    assert mom["change_percent"] is None


def test_summary_category_increase_insight(client):
    # August: Marketing spent 1000.00
    client.post("/expenses", json={"amount": 1000.00, "category": "Marketing", "date": "2026-08-10"})
    # September: Marketing spent 1500.00 (+50% increase > 20% threshold)
    client.post("/expenses", json={"amount": 1500.00, "category": "Marketing", "date": "2026-09-10"})

    response = client.get("/summary?year=2026&month=9")
    assert response.status_code == 200
    data = response.json()
    assert len(data["insights"]) == 1
    insight = data["insights"][0]
    assert insight["category"] == "Marketing"
    assert insight["increase_percent"] == 50.0
    assert "Marketing spending increased by 50.0%" in insight["message"]
