from app import create_app
app = create_app("development")
app.config["TESTING"] = True
client = app.test_client()
resp = client.get("/api/v1/drivers?season=2024")
print(resp.status_code, resp.json)
