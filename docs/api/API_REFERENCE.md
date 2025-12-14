# API Documentation

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

All protected endpoints require JWT authentication via Bearer token.

### Get Token

```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=yourpassword
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

### Use Token

Include in headers for protected endpoints:

```
Authorization: Bearer eyJhbGc...
```

## Endpoints

### Authentication

#### Register New User

```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "full_name": "John Doe",
  "password": "SecurePass123!@#"
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "registered",
  "is_active": true,
  "is_verified": false,
  "mfa_enabled": false,
  "created_at": "2025-01-01T00:00:00Z"
}
```

#### Get Current User

```http
GET /auth/me
Authorization: Bearer {token}
```

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "audit_lead",
  "is_active": true,
  "created_at": "2025-01-01T00:00:00Z"
}
```

### Audits

#### Create Audit

```http
POST /audits
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "National Hip Fracture Audit 2025",
  "description": "Annual audit of hip fracture care quality",
  "clinical_domain": "orthopaedics",
  "population": "Adults 65+ with hip fracture",
  "start_date": "2025-01-01T00:00:00Z",
  "end_date": "2025-12-31T23:59:59Z",
  "governance_body": "Royal College of Surgeons",
  "data_protection_level": "no_pii",
  "is_public": false,
  "require_consent": false,
  "retention_days": 3650
}
```

**Response:** `201 Created`
```json
{
  "id": "audit-uuid",
  "title": "National Hip Fracture Audit 2025",
  "status": "draft",
  "owner_id": "user-uuid",
  "total_episodes": 0,
  "created_at": "2025-01-01T00:00:00Z",
  ...
}
```

#### List Audits

```http
GET /audits?skip=0&limit=50
Authorization: Bearer {token}
```

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "title": "National Hip Fracture Audit 2025",
    "status": "active",
    "clinical_domain": "orthopaedics",
    "total_episodes": 1247,
    "created_at": "2025-01-01T00:00:00Z"
  },
  ...
]
```

#### Get Audit Details

```http
GET /audits/{audit_id}
Authorization: Bearer {token}
```

#### Update Audit

```http
PATCH /audits/{audit_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "status": "active",
  "description": "Updated description"
}
```

#### Delete Audit

```http
DELETE /audits/{audit_id}
Authorization: Bearer {token}
```

**Note:** Can only delete audits in `draft` status.

### Questionnaires

#### Create Questionnaire

```http
POST /questionnaires/{audit_id}/questionnaires
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "Hip Fracture Data Collection Form v1",
  "description": "Initial data collection questionnaire",
  "questions": [
    {
      "question_code": "Q1",
      "question_text": "Primary anaesthetic technique used",
      "question_type": "categorical_single",
      "required": true,
      "options": {
        "choices": ["Spinal", "General", "Combined", "Not documented"]
      },
      "variable_name": "anaesthetic_technique",
      "variable_type": "categorical",
      "help_text": "Select the primary technique used",
      "clinical_guidance": "Spinal anaesthesia is recommended for hip fracture surgery"
    },
    {
      "question_code": "Q2",
      "question_text": "Time from admission to surgery (hours)",
      "question_type": "numeric",
      "required": true,
      "validation": {
        "min": 0,
        "max": 168,
        "decimal_places": 1
      },
      "variable_name": "time_to_surgery_hours",
      "variable_type": "numeric",
      "help_text": "Enter in hours (e.g., 36.5)",
      "clinical_guidance": "NICE guideline: surgery within 36 hours"
    }
  ]
}
```

**Response:** `201 Created`
```json
{
  "id": "questionnaire-uuid",
  "audit_id": "audit-uuid",
  "version": 1,
  "title": "Hip Fracture Data Collection Form v1",
  "is_published": false,
  "methodological_quality_score": 85.5,
  "analysability_score": 92.3,
  "questions": [...],
  "created_at": "2025-01-01T00:00:00Z"
}
```

#### List Questionnaires

```http
GET /questionnaires/{audit_id}/questionnaires
Authorization: Bearer {token}
```

#### Get Specific Version

```http
GET /questionnaires/{audit_id}/questionnaires/{version}
Authorization: Bearer {token}
```

### Episodes (Data Entry)

#### Submit Episode

```http
POST /episodes/{audit_id}/episodes?site_id={site_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "episode_code": "SITE001-2025-001",
  "responses": {
    "Q1": "Spinal",
    "Q2": 28.5,
    "Q3": "2025-06-10",
    "Q4": true
  },
  "consent_obtained": true,
  "consent_date": "2025-06-10T00:00:00Z"
}
```

**Response:** `201 Created`
```json
{
  "id": "episode-uuid",
  "audit_id": "audit-uuid",
  "questionnaire_version": 1,
  "site_id": "site-uuid",
  "submitted_at": "2025-06-10T14:30:00Z",
  "is_validated": true,
  "responses": {...}
}
```

#### List Episodes

```http
GET /episodes/{audit_id}/episodes?skip=0&limit=50
Authorization: Bearer {token}
```

**Note:** Only audit owners and authorized users can view episodes.

#### Get Episode Details

```http
GET /episodes/{audit_id}/episodes/{episode_id}
Authorization: Bearer {token}
```

### Users

#### List Users (Admin Only)

```http
GET /users?skip=0&limit=50
Authorization: Bearer {token}
```

#### Get User

```http
GET /users/{user_id}
Authorization: Bearer {token}
```

#### Update User

```http
PATCH /users/{user_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "full_name": "Updated Name",
  "mfa_enabled": true
}
```

## Data Models

### Audit

```typescript
{
  id: string (UUID)
  title: string
  description?: string
  clinical_domain: string
  population: string
  start_date: datetime
  end_date?: datetime
  status: "draft" | "under_review" | "approved" | "active" | "paused" | "closed"
  data_protection_level: "no_pii" | "pseudonymised" | "pii_required"
  governance_body?: string
  owner_id: string (UUID)
  is_public: boolean
  total_episodes: number
  created_at: datetime
  updated_at: datetime
}
```

### Question Types

- `categorical_single`: Single choice from options
- `categorical_multiple`: Multiple choices allowed
- `ordinal`: Ordered scale (e.g., Likert)
- `numeric`: Number with optional constraints
- `date`: Date picker
- `time`: Time picker
- `datetime`: Date and time
- `text_short`: Short text (discouraged)
- `text_long`: Long text (discouraged)
- `boolean`: Yes/No

### Validation Rules

```typescript
{
  min?: number          // Minimum value (numeric)
  max?: number          // Maximum value (numeric)
  minLength?: number    // Minimum length (text)
  maxLength?: number    // Maximum length (text)
  pattern?: string      // Regex pattern
  decimal_places?: number
  required?: boolean
}
```

### Conditional Logic

```typescript
{
  show_if: {
    question: "Q1",
    operator: "equals" | "not_equals" | "greater_than" | "less_than",
    value: any
  }
}
```

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message"
}
```

### HTTP Status Codes

- `200` - Success
- `201` - Created
- `204` - No Content (deletion)
- `400` - Bad Request (validation error)
- `401` - Unauthorized (authentication required)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `422` - Unprocessable Entity (validation error)
- `500` - Internal Server Error

## Rate Limiting

- Default: 60 requests per minute per user
- Exceeded: `429 Too Many Requests`

## Pagination

List endpoints support pagination:

```
GET /audits?skip=0&limit=50
```

- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum records to return (default: 50, max: 1000)

## Filtering and Sorting

Coming in future versions:

```
GET /audits?status=active&sort=-created_at
```

## Webhooks

Coming in future versions for:
- Episode submission
- Audit status changes
- Export completion

## SDK Examples

### Python

```python
import requests

API_BASE = "http://localhost:8000/api/v1"

# Login
response = requests.post(
    f"{API_BASE}/auth/login",
    data={"username": "user@example.com", "password": "password"}
)
token = response.json()["access_token"]

# Create audit
headers = {"Authorization": f"Bearer {token}"}
audit = {
    "title": "My Audit",
    "clinical_domain": "cardiology",
    "population": "Adult patients",
    "start_date": "2025-01-01T00:00:00Z"
}
response = requests.post(
    f"{API_BASE}/audits",
    json=audit,
    headers=headers
)
print(response.json())
```

### JavaScript

```javascript
const API_BASE = 'http://localhost:8000/api/v1';

// Login
const loginResponse = await fetch(`${API_BASE}/auth/login`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: new URLSearchParams({
    username: 'user@example.com',
    password: 'password'
  })
});
const { access_token } = await loginResponse.json();

// Create audit
const audit = {
  title: 'My Audit',
  clinical_domain: 'cardiology',
  population: 'Adult patients',
  start_date: '2025-01-01T00:00:00Z'
};
const auditResponse = await fetch(`${API_BASE}/audits`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${access_token}`
  },
  body: JSON.stringify(audit)
});
console.log(await auditResponse.json());
```

## Interactive Documentation

Visit http://localhost:8000/api/v1/docs for interactive Swagger UI documentation where you can test all endpoints directly.
