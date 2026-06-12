# Firebase Integration Setup Guide

## Overview
This app is now integrated with Firebase for user authentication, profile management, and data persistence. The integration uses the Firebase Admin SDK (Python).

## Project Configuration
- **Project ID**: `aero-lift-and-drag`
- **Database URL**: `https://aero-lift-and-drag-default-rtdb.firebaseio.com`
- **Region**: (auto-determined by Firebase)

## Setup Instructions

### 1. Install Firebase Dependencies
```bash
pip install -r requirements.txt
```

The following packages will be installed:
- `firebase-admin>=6.2.0`
- `google-cloud-firestore>=2.13.0`

### 2. Obtain Firebase Service Account Key

#### Option A: Development (Local)
1. Go to [Firebase Console](https://console.firebase.google.com/project/aero-lift-and-drag)
2. Navigate to **Project Settings** (gear icon)
3. Go to **Service Accounts** tab
4. Click **Generate New Private Key**
5. Save the file as `aero_dashboard/serviceAccountKey.json`
6. **Important**: Add this file to `.gitignore` (it contains sensitive credentials)

#### Option B: Production (Environment Variable)
1. Generate the service account key (steps 1-4 above)
2. Convert the JSON file to a string and set as environment variable:
   ```bash
   export FIREBASE_CREDENTIALS_JSON='{"type":"service_account","project_id":"aero-lift-and-drag",...}'
   ```
3. Or on Windows (PowerShell):
   ```powershell
   $env:FIREBASE_CREDENTIALS_JSON = '{"type":"service_account","project_id":"aero-lift-and-drag",...}'
   ```

### 3. Enable Firestore Database
1. Go to [Firebase Console](https://console.firebase.google.com/project/aero-lift-and-drag)
2. Navigate to **Firestore Database** (or **Realtime Database**)
3. Click **Create Database**
4. Choose **Start in production mode** or **test mode** (for development)
5. Select region (e.g., `us-central1`)

### 4. Set Firestore Security Rules
For development/testing, use these permissive rules:
```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read, write: if true;
    }
  }
}
```

**For production**, implement stricter rules:
```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{userId} {
      allow read, write: if request.auth.uid == userId;
    }
    match /sessions/{document=**} {
      allow read, write: if request.auth != null;
    }
    match /simulator_results/{document=**} {
      allow read, write: if request.auth != null;
    }
  }
}
```

## Firebase Collections

### `users`
Stores user profile information.
```
{
  "username": "string",
  "email": "string (optional)",
  "created_at": "timestamp",
  "last_login": "timestamp",
  "password_hash": "number (hash)"
}
```

### `sessions`
Logs user sign-in and sign-up events.
```
{
  "username": "string",
  "action": "signin" | "signup",
  "remember": "boolean",
  "timestamp": "timestamp"
}
```

### `simulator_results`
Stores aerodynamic simulator run results.
```
{
  "username": "string",
  "aircraft": "string",
  "velocity": "number",
  "lift": "number",
  "drag": "number",
  "lift_off_time": "number (optional)",
  "timestamp": "timestamp"
}
```

## Usage in Code

### Import Firebase Config
```python
from aero_dashboard import firebase_config

# Check if Firebase is initialized
firebase_config.init_firebase()
```

### Save User Profile
```python
firebase_config.save_user_profile(
    username="john_doe",
    email="john@example.com",
    metadata={"aircraft_preference": "Cessna 172"}
)
```

### Get User Profile
```python
profile = firebase_config.get_user_profile("john_doe")
if profile:
    print(f"User created at: {profile.get('created_at')}")
```

### Save Simulator Result
```python
firebase_config.save_simulator_result(
    username="john_doe",
    result_data={
        "aircraft": "Cessna 172",
        "velocity": 150.5,
        "lift": 45000.0,
        "drag": 1200.0,
        "lift_off_time": 12.5,
        "lift_off_distance": 450.0
    }
)
```

### Retrieve User History
```python
results = firebase_config.get_user_simulator_history("john_doe", limit=10)
for result in results:
    print(f"Result on {result['timestamp']}: {result['aircraft']}")
```

## Troubleshooting

### "Firebase initialization error"
- **Cause**: Service account credentials not found
- **Solution**: Ensure `serviceAccountKey.json` exists in `aero_dashboard/` or `FIREBASE_CREDENTIALS_JSON` environment variable is set

### "Permission denied" errors
- **Cause**: Firestore security rules are too restrictive
- **Solution**: Temporarily use development mode rules or verify authentication is working

### "Module 'firebase_admin' not found"
- **Cause**: Firebase Admin SDK not installed
- **Solution**: Run `pip install -r requirements.txt`

## Best Practices

1. **Never commit service account keys** — Always use `.gitignore`
2. **Use environment variables in production** — Don't hardcode credentials
3. **Implement proper security rules** — Don't use permissive rules in production
4. **Rate limit data writes** — Firestore has pricing per operation
5. **Validate data on the client side** — Always validate before sending to Firebase
6. **Use transactions** — For complex multi-document operations

## Next Steps

- Migrate user credentials from mock session state to Firebase Authentication
- Add real-time sync of user preferences
- Implement backup and export features
- Set up Firebase Monitoring and Alerts
