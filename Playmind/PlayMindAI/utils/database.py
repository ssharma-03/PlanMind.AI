import os
from dotenv import load_dotenv
import json
import time
import pandas as pd

# Load environment variables
load_dotenv()

# Try to import Supabase client, but provide fallback
try:
    from supabase import create_client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("Supabase client not available. Using local storage fallback.")

# Local storage location
LOCAL_STORAGE_FILE = "local_storage.json"

def get_supabase_client():
    """Initialize and return Supabase client if available"""
    if not SUPABASE_AVAILABLE:
        return None
        
    try:
        # Supabase credentials
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            print("Supabase credentials not found in environment variables")
            return None
            
        client = create_client(supabase_url, supabase_key)
        return client
    except Exception as e:
        print(f"Error initializing Supabase client: {e}")
        return None

def save_to_database(session_data):
    """Save the strategy session to Supabase or local storage"""
    # Try Supabase first
    client = get_supabase_client()
    if client:
        try:
            # Insert data into the 'strategy_sessions' table
            response = client.table("strategy_sessions").insert(session_data).execute()
            
            if hasattr(response, 'error') and response.error:
                print(f"Error saving to Supabase: {response.error}")
                return save_to_local_storage(session_data)
            
            return True
        except Exception as e:
            print(f"Error saving to Supabase: {e}")
            return save_to_local_storage(session_data)
    else:
        # Fall back to local storage
        return save_to_local_storage(session_data)

def save_to_local_storage(session_data):
    """Save session data to local JSON file"""
    try:
        # Load existing data
        if os.path.exists(LOCAL_STORAGE_FILE):
            with open(LOCAL_STORAGE_FILE, 'r') as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = []
        else:
            data = []
        
        # Add new session data
        data.append(session_data)
        
        # Save data back to file
        with open(LOCAL_STORAGE_FILE, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        return True
    except Exception as e:
        print(f"Error saving to local storage: {e}")
        return False

def get_previous_sessions(user_id, limit=10):
    """Retrieve previous strategy sessions for a user from Supabase or local storage"""
    # Try Supabase first
    client = get_supabase_client()
    if client:
        try:
            # Query the 'strategy_sessions' table
            response = client.table("strategy_sessions") \
                            .select("*") \
                            .eq("user_id", user_id) \
                            .order("timestamp", desc=True) \
                            .limit(limit) \
                            .execute()
            
            if hasattr(response, 'error') and response.error:
                print(f"Error retrieving from Supabase: {response.error}")
                return get_sessions_from_local_storage(user_id, limit)
            
            # Extract the data from the response
            sessions = response.data
            return sessions
        except Exception as e:
            print(f"Error retrieving from Supabase: {e}")
            return get_sessions_from_local_storage(user_id, limit)
    else:
        # Fall back to local storage
        return get_sessions_from_local_storage(user_id, limit)

def get_sessions_from_local_storage(user_id, limit=10):
    """Retrieve session data from local JSON file"""
    try:
        if not os.path.exists(LOCAL_STORAGE_FILE):
            return []
            
        with open(LOCAL_STORAGE_FILE, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                return []
        
        # Filter sessions by user_id
        user_sessions = [session for session in data if session.get("user_id") == user_id]
        
        # Sort by timestamp (newest first)
        user_sessions.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        # Apply limit
        return user_sessions[:limit]
    except Exception as e:
        print(f"Error retrieving from local storage: {e}")
        return [] 