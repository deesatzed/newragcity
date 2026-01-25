# Medical API Documentation

## Overview

This API provides secure, HIPAA-compliant access to medical records and patient management functionality. All endpoints implement medical-grade authentication and audit logging.

## Authentication

### JWT Token Authentication

All API endpoints require JWT authentication with medical professional credentials.

#### Login Endpoint

```
POST /auth/login
Content-Type: application/json

{
  "email": "doctor@hospital.com",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900,
  "user_info": {
    "id": "prof_123",
    "name": "Dr. Jane Smith",
    "specialty": "Internal Medicine",
    "license_number": "MD123456"
  }
}
```

#### Token Refresh

```
POST /auth/refresh
Authorization: Bearer <refresh_token>
```

### Security Requirements

- All requests must include `Authorization: Bearer <access_token>` header
- Access tokens expire in 15 minutes for security
- Refresh tokens expire in 7 days
- Failed authentication attempts are logged and rate-limited

## Patient Management

### Get Patient Information

```
GET /patients/{patient_id}
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "id": "pat_456",
  "medical_record_number": "MRN789012",
  "name": {
    "first": "John",
    "last": "Doe"
  },
  "date_of_birth": "1980-05-15",
  "contact": {
    "phone": "555-0123",
    "email": "john.doe@email.com"
  },
  "medical_info": {
    "blood_type": "A+",
    "allergies": ["Penicillin", "Shellfish"],
    "chronic_conditions": ["Hypertension", "Type 2 Diabetes"]
  },
  "insurance": {
    "primary": "Blue Cross Blue Shield",
    "member_id": "BCB123456789"
  }
}
```

### Create New Patient

```
POST /patients
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "first_name": "Jane",
  "last_name": "Smith",
  "date_of_birth": "1985-03-20",
  "phone_number": "555-0456",
  "email": "jane.smith@email.com",
  "address": {
    "street": "123 Main St",
    "city": "Anytown",
    "state": "CA",
    "zip": "90210"
  },
  "emergency_contact": {
    "name": "John Smith",
    "relationship": "Spouse",
    "phone": "555-0789"
  },
  "insurance": {
    "primary": "Aetna",
    "member_id": "AET987654321"
  }
}
```

### Update Patient Information

```
PUT /patients/{patient_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "phone_number": "555-0999",
  "allergies": ["Penicillin", "Shellfish", "Latex"]
}
```

## Appointment Management

### Schedule Appointment

```
POST /appointments
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "patient_id": "pat_456",
  "provider_id": "prof_123",
  "appointment_date": "2024-02-15T14:30:00Z",
  "duration_minutes": 30,
  "appointment_type": "consultation",
  "chief_complaint": "Follow-up for hypertension",
  "insurance_authorization": "AUTH123456"
}
```

### Get Appointments

```
GET /appointments?date=2024-02-15&provider_id=prof_123
Authorization: Bearer <access_token>
```

### Update Appointment Status

```
PATCH /appointments/{appointment_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "status": "completed",
  "appointment_notes": "Patient responded well to treatment. Continue current medications."
}
```

## Medical Records

### Create Medical Record

```
POST /medical-records
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "patient_id": "pat_456",
  "appointment_id": "apt_789",
  "record_type": "progress_note",
  "subjective": "Patient reports improved energy levels since starting new medication.",
  "objective": "BP: 130/80, HR: 72, Temp: 98.6°F. Patient appears well.",
  "assessment": "Hypertension well-controlled on current regimen. Type 2 diabetes stable.",
  "plan": "Continue current medications. Follow-up in 3 months. Order HbA1c.",
  "vital_signs": {
    "blood_pressure": "130/80",
    "heart_rate": 72,
    "temperature": 98.6,
    "respiratory_rate": 16,
    "oxygen_saturation": 98
  },
  "icd10_codes": ["I10", "E11.9"],
  "medications_prescribed": [
    {
      "name": "Lisinopril",
      "dosage": "10mg",
      "frequency": "once daily",
      "duration": "90 days"
    }
  ]
}
```

### Get Medical Records

```
GET /medical-records?patient_id=pat_456&limit=10
Authorization: Bearer <access_token>
```

## Error Handling

### HTTP Status Codes

- `200` - Success
- `201` - Created successfully
- `400` - Bad request (invalid data)
- `401` - Unauthorized (invalid or expired token)
- `403` - Forbidden (insufficient permissions)
- `404` - Resource not found
- `409` - Conflict (duplicate resource)
- `422` - Validation error
- `500` - Internal server error

### Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The provided data failed validation",
    "details": {
      "field": "email",
      "issue": "Invalid email format"
    },
    "timestamp": "2024-02-15T10:30:00Z",
    "request_id": "req_abc123"
  }
}
```

## Rate Limiting

API requests are rate-limited to ensure system stability:

- Authentication endpoints: 5 requests per minute per IP
- Patient data endpoints: 100 requests per minute per user
- Medical record endpoints: 50 requests per minute per user

Rate limit headers are included in responses:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Requests remaining in window
- `X-RateLimit-Reset`: Time when limit resets

## HIPAA Compliance

### Audit Logging

All API access is logged for HIPAA compliance:

- User identification and authentication
- Date and time of access
- Type of action performed
- Patient records accessed
- Success or failure of access attempt

### Data Security

- All data transmitted over HTTPS
- Patient data encrypted at rest
- Access controls based on minimum necessary principle
- Automatic session timeout after inactivity

### Access Controls

Different user roles have different permissions:

- **Medical Professionals**: Full access to assigned patients
- **Nurses**: Read/write access to clinical data
- **Administrative Staff**: Access to scheduling and demographics
- **Patients**: Read-only access to own records

## Development Environment

### Base URLs

- Development: `https://api-dev.hospital.com/v1`
- Staging: `https://api-staging.hospital.com/v1`
- Production: `https://api.hospital.com/v1`

### API Versioning

The API uses URL-based versioning. Current version is `v1`. All endpoints are prefixed with `/v1/`.

### Testing

Use the following test credentials in development:

```json
{
  "email": "test.doctor@hospital.com",
  "password": "TestPassword123!"
}
```

**Note**: Test credentials only work in development environment and provide access to anonymized test data.