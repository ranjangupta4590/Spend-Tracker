import pytest


def test_category_insight_increase_by_30_percent_flagged(client):
    # Previous month (August): 1000.00
    client.post("/expenses", json={"amount": 1000.00, "category": "Food", "date": "2026-08-10"})
    # Current month (September): 1300.00 (+30% increase > 20%)
    client.post("/expenses", json={"amount": 1300.00, "category": "Food", "date": "2026-09-10"})

    res = client.get("/summary?year=2026&month=9")
    assert res.status_code == 200
    data = res.json()
    cat_insights = {item["category"]: item for item in data["category_insights"]}

    assert "Food" in cat_insights
    food_insight = cat_insights["Food"]
    assert food_insight["previous_month"] == 1000.00
    assert food_insight["current_month"] == 1300.00
    assert food_insight["change_percent"] == 30.0
    assert food_insight["flagged"] is True


def test_category_insight_increase_by_exactly_20_percent_not_flagged(client):
    # Previous: 1000.00, Current: 1200.00 (+20% exactly) -> NOT flagged
    client.post("/expenses", json={"amount": 1000.00, "category": "Office", "date": "2026-08-10"})
    client.post("/expenses", json={"amount": 1200.00, "category": "Office", "date": "2026-09-10"})

    res = client.get("/summary?year=2026&month=9")
    assert res.status_code == 200
    data = res.json()
    cat_insights = {item["category"]: item for item in data["category_insights"]}

    assert "Office" in cat_insights
    office_insight = cat_insights["Office"]
    assert office_insight["change_percent"] == 20.0
    assert office_insight["flagged"] is False


def test_category_insight_increase_by_10_percent_not_flagged(client):
    # Previous: 1000.00, Current: 1100.00 (+10%) -> NOT flagged
    client.post("/expenses", json={"amount": 1000.00, "category": "Travel", "date": "2026-08-10"})
    client.post("/expenses", json={"amount": 1100.00, "category": "Travel", "date": "2026-09-10"})

    res = client.get("/summary?year=2026&month=9")
    assert res.status_code == 200
    data = res.json()
    cat_insights = {item["category"]: item for item in data["category_insights"]}

    assert "Travel" in cat_insights
    assert cat_insights["Travel"]["change_percent"] == 10.0
    assert cat_insights["Travel"]["flagged"] is False


def test_category_insight_decrease_not_flagged(client):
    # Previous: 1000.00, Current: 800.00 (-20%) -> NOT flagged
    client.post("/expenses", json={"amount": 1000.00, "category": "Marketing", "date": "2026-08-10"})
    client.post("/expenses", json={"amount": 800.00, "category": "Marketing", "date": "2026-09-10"})

    res = client.get("/summary?year=2026&month=9")
    assert res.status_code == 200
    data = res.json()
    cat_insights = {item["category"]: item for item in data["category_insights"]}

    assert "Marketing" in cat_insights
    assert cat_insights["Marketing"]["change_percent"] == -20.0
    assert cat_insights["Marketing"]["flagged"] is False


def test_category_insight_previous_month_zero(client):
    # Previous month = 0, Current month = 500 -> change_percent is None, flagged is False
    client.post("/expenses", json={"amount": 500.00, "category": "Software", "date": "2026-09-10"})

    res = client.get("/summary?year=2026&month=9")
    assert res.status_code == 200
    data = res.json()
    cat_insights = {item["category"]: item for item in data["category_insights"]}

    assert "Software" in cat_insights
    soft_insight = cat_insights["Software"]
    assert soft_insight["previous_month"] == 0.0
    assert soft_insight["current_month"] == 500.00
    assert soft_insight["change_percent"] is None
    assert soft_insight["flagged"] is False


def test_category_insight_multiple_categories_independent(client):
    # Aug: Food 1000, Travel 1000, Office 1000
    client.post("/expenses", json={"amount": 1000.00, "category": "Food", "date": "2026-08-10"})
    client.post("/expenses", json={"amount": 1000.00, "category": "Travel", "date": "2026-08-10"})
    client.post("/expenses", json={"amount": 1000.00, "category": "Office", "date": "2026-08-10"})

    # Sep: Food 1350 (+35% -> flagged), Travel 1080 (+8% -> not flagged), Office 880 (-12% -> not flagged), Books 200 (new -> not flagged)
    client.post("/expenses", json={"amount": 1350.00, "category": "Food", "date": "2026-09-10"})
    client.post("/expenses", json={"amount": 1080.00, "category": "Travel", "date": "2026-09-10"})
    client.post("/expenses", json={"amount": 880.00, "category": "Office", "date": "2026-09-10"})
    client.post("/expenses", json={"amount": 200.00, "category": "Books", "date": "2026-09-10"})

    res = client.get("/summary?year=2026&month=9")
    assert res.status_code == 200
    data = res.json()
    cat_insights = {item["category"]: item for item in data["category_insights"]}

    assert cat_insights["Food"]["flagged"] is True
    assert cat_insights["Food"]["change_percent"] == 35.0

    assert cat_insights["Travel"]["flagged"] is False
    assert cat_insights["Travel"]["change_percent"] == 8.0

    assert cat_insights["Office"]["flagged"] is False
    assert cat_insights["Office"]["change_percent"] == -12.0

    assert cat_insights["Books"]["flagged"] is False
    assert cat_insights["Books"]["change_percent"] is None
