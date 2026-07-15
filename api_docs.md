# ApexGrid API Documentation

## Base URL
`/api/v1`

## Authentication
Most endpoints require a JWT token passed in the `Authorization` header:
`Authorization: Bearer <access_token>`

## Endpoints

### Auth (`/auth`)
- `POST /register`: Register a new user. Body: `{"email": "", "password": "", "username": ""}`
- `POST /login`: Authenticate and receive JWT. Body: `{"email": "", "password": ""}`
- `POST /refresh`: Refresh access token (requires `refresh_token` cookie).
- `POST /logout`: Logout and invalidate token.
- `GET /profile`: Get current user profile. Requires Auth.
- `PATCH /profile`: Update profile (username, preferences). Requires Auth.
- `POST /request-password-reset`: Request reset link. Body: `{"email": ""}`
- `POST /reset-password`: Reset password. Body: `{"token": "", "new_password": ""}`
- `DELETE /account`: Delete user account. Requires Auth.

### Dashboards (`/dashboards`)
Requires Auth.
- `GET /`: Get all saved dashboards.
- `POST /`: Create a new dashboard. Body: `{"name": "...", "filters": {}}`
- `GET /<id>`: Get specific dashboard.
- `PATCH /<id>`: Update dashboard.
- `DELETE /<id>`: Delete dashboard.

### Favorites (`/favorites`)
Requires Auth.
- `GET /drivers`: Get favorited drivers.
- `POST /drivers`: Add a favorite driver. Body: `{"driver_number": 1}`
- `DELETE /drivers/<driver_number>`: Remove a favorite driver.
- `GET /teams`: Get favorited teams.
- `POST /teams`: Add a favorite team. Body: `{"team_name": "Red Bull Racing"}`
- `DELETE /teams/<team_name>`: Remove a favorite team.

### OpenF1 Proxy 
- `GET /sessions`: List sessions. Query params: `year`, `country`, `session_type`.
- `GET /sessions/<session_key>`: Get session details.
- `GET /sessions/<session_key>/weather`: Get weather data for session.
- `GET /sessions/<session_key>/pitstops`: Get pitstop data.
- `GET /sessions/<session_key>/intervals`: Get gap intervals.
- `GET /sessions/<session_key>/laps`: Get lap data. Query param: `driver_number` (optional).
- `GET /sessions/<session_key>/racecontrol`: Get race control messages.
- `GET /sessions/<session_key>/telemetry`: Get car telemetry. Query param: `driver_number`.
- `GET /sessions/<session_key>/location`: Get car location. Query param: `driver_number`.
- `GET /teams`: Get all teams for a given year. Query params: `year` (default: 2024).
- `GET /teams/<team_name>`: Get specific team info. Query params: `year` (default: 2024).

### Standings
- `GET /standings/drivers`: Get mocked driver standings.
- `GET /standings/constructors`: Get mocked constructor standings.

### Uploads (`/uploads`)
- `POST /avatars`: Upload a profile picture (multipart/form-data). Requires Auth.
- `GET /avatars/<filename>`: Serve the uploaded avatar.
