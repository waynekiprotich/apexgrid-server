def test_unsupported_media_type(client):
    # Send a request with no Content-Type to a JSON-expecting endpoint
    response = client.post("/api/v1/auth/register", data="not-json")
    
    assert response.status_code == 415
    data = response.get_json()
    assert data["error"]["code"] == "UNSUPPORTED_MEDIA_TYPE"
    assert data["error"]["status"] == 415

def test_bad_request(client):
    # Send malformed JSON to trigger 400 Bad Request
    response = client.post("/api/v1/auth/register", data="{bad-json", headers={"Content-Type": "application/json"})
    
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"]["code"] == "BAD_REQUEST"
    assert data["error"]["status"] == 400
