import firebase_admin
from firebase_admin import credentials, auth, db, firestore
import streamlit as st
import json
import os

# Firebase configuration dictionary
FIREBASE_CONFIG = {
    "apiKey": "AIzaSyAc78EEFh6SexbOPlDuu_6_tlbXG4yyHXo",
    "authDomain": "aero-lift-and-drag.firebaseapp.com",
    "projectId": "aero-lift-and-drag",
    "storageBucket": "aero-lift-and-drag.firebasestorage.app",
    "messagingSenderId": "63312586755",
    "appId": "1:63312586755:web:4d8f5ad73f6053479f4636",
    "measurementId": "G-E2HLZ0Q3WE",
    "databaseURL": "https://aero-lift-and-drag-default-rtdb.firebaseio.com"
}


def init_firebase() -> bool:
    """Initialize Firebase Admin SDK.
    
    Returns True if already initialized or successfully initialized,
    False if credentials are not available.
    """
    if firebase_admin._apps:
        return True
    
    try:
        # Try to get credentials from environment variable (for production)
        firebase_creds_json = os.environ.get("FIREBASE_CREDENTIALS_JSON")
        if firebase_creds_json:
            creds_dict = json.loads(firebase_creds_json)
            creds = credentials.Certificate(creds_dict)
            firebase_admin.initialize_app(creds, {"databaseURL": FIREBASE_CONFIG["databaseURL"]})
            return True
        
        # Try to load from local service account file (for development)
        service_account_path = "aero_dashboard/serviceAccountKey.json"
        if os.path.exists(service_account_path):
            creds = credentials.Certificate(service_account_path)
            firebase_admin.initialize_app(creds, {"databaseURL": FIREBASE_CONFIG["databaseURL"]})
            return True
        
        return False
    except Exception as e:
        st.error(f"Firebase initialization error: {e}")
        return False


def get_firestore_client() -> firestore.client | None:
    """Get Firestore client if available."""
    try:
        if not firebase_admin._apps:
            if not init_firebase():
                return None
        return firestore.client()
    except Exception:
        return None


def save_user_profile(username: str, email: str | None = None, metadata: dict | None = None) -> bool:
    """Save or update user profile in Firestore.
    
    Args:
        username: The username
        email: Optional email address
        metadata: Optional additional user metadata
    
    Returns:
        True if successful, False otherwise
    """
    try:
        db = get_firestore_client()
        if not db:
            return False
        
        profile = {
            "username": username,
            "created_at": firestore.SERVER_TIMESTAMP,
            "last_login": firestore.SERVER_TIMESTAMP,
        }
        
        if email:
            profile["email"] = email
        
        if metadata:
            profile.update(metadata)
        
        db.collection("users").document(username).set(profile, merge=True)
        return True
    except Exception as e:
        st.error(f"Error saving user profile: {e}")
        return False


def get_user_profile(username: str) -> dict | None:
    """Retrieve user profile from Firestore.
    
    Args:
        username: The username to look up
    
    Returns:
        User profile dict if found, None otherwise
    """
    try:
        db = get_firestore_client()
        if not db:
            return None
        
        doc = db.collection("users").document(username).get()
        if doc.exists:
            return doc.to_dict()
        return None
    except Exception:
        return None


def save_user_session(username: str, session_data: dict) -> bool:
    """Save user session data to Firestore.
    
    Args:
        username: The username
        session_data: Session metadata to save
    
    Returns:
        True if successful, False otherwise
    """
    try:
        db = get_firestore_client()
        if not db:
            return False
        
        session_record = {
            "username": username,
            "timestamp": firestore.SERVER_TIMESTAMP,
            **session_data
        }
        
        db.collection("sessions").add(session_record)
        return True
    except Exception as e:
        st.error(f"Error saving session: {e}")
        return False


def save_simulator_result(username: str, result_data: dict) -> bool:
    """Save simulator results to Firestore.
    
    Args:
        username: The username
        result_data: Simulator result metadata
    
    Returns:
        True if successful, False otherwise
    """
    try:
        db = get_firestore_client()
        if not db:
            return False
        
        result_record = {
            "username": username,
            "timestamp": firestore.SERVER_TIMESTAMP,
            **result_data
        }
        
        db.collection("simulator_results").add(result_record)
        return True
    except Exception as e:
        st.error(f"Error saving simulator result: {e}")
        return False


def get_user_simulator_history(username: str, limit: int = 10) -> list[dict]:
    """Retrieve user's recent simulator runs from Firestore.
    
    Args:
        username: The username
        limit: Maximum number of results to return
    
    Returns:
        List of simulator result dicts
    """
    try:
        db = get_firestore_client()
        if not db:
            return []
        
        docs = (
            db.collection("simulator_results")
            .where("username", "==", username)
            .order_by("timestamp", direction=firestore.Query.DESCENDING)
            .limit(limit)
            .stream()
        )
        
        return [doc.to_dict() for doc in docs]
    except Exception:
        return []
