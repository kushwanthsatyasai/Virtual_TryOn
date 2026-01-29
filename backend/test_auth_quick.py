"""
Quick Authentication Test Script
Run this to test registration, login, and authenticated endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_auth():
    print("\n" + "="*70)
    print("AUTHENTICATION TEST - Virtue Try-On")
    print("="*70)
    
    # Test 1: Register
    print("\n[1/4] Registering new user...")
    try:
        register_data = {
            "email": "demo@example.com",
            "username": "demouser",
            "password": "Demo123456",
            "full_name": "Demo User",
            "age": 22,
            "phone": "9999999999",
            "gender": "male"
        }
        
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        
        if response.status_code == 200:
            data = response.json()
            token = data['access_token']
            user = data['user']
            
            print(f"Success! User registered:")
            print(f"  - Username: {user['username']}")
            print(f"  - Email: {user['email']}")
            print(f"  - Token: {token[:40]}...")
            
            # Test 2: Get Profile
            print("\n[2/4] Testing authenticated endpoint (GET /auth/me)...")
            headers = {"Authorization": f"Bearer {token}"}
            profile_response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
            
            if profile_response.status_code == 200:
                print("Success! Authentication working correctly")
                print(f"  Profile data: {json.dumps(profile_response.json(), indent=2)}")
            else:
                print(f"Failed: {profile_response.status_code} - {profile_response.text}")
            
            # Test 3: Chat Endpoint
            print("\n[3/4] Testing AI chat endpoint...")
            chat_response = requests.post(
                f"{BASE_URL}/api/v1/chat/send",
                headers=headers,
                json={"message": "Hello! What colors look good together?"}
            )
            
            if chat_response.status_code == 200:
                chat_data = chat_response.json()
                print("Success! Chat endpoint working")
                print(f"  AI Response: {chat_data.get('message', 'N/A')[:150]}...")
            else:
                print(f"Note: Chat requires AI provider setup")
                print(f"  Status: {chat_response.status_code}")
                if chat_response.status_code == 500:
                    print("  (Set OPENAI_API_KEY or ANTHROPIC_API_KEY in .env to enable)")
            
            # Test 4: Recommendations
            print("\n[4/4] Testing recommendations endpoint...")
            rec_response = requests.get(
                f"{BASE_URL}/api/v1/recommendations",
                headers=headers
            )
            
            if rec_response.status_code == 200:
                rec_data = rec_response.json()
                print(f"Success! Got {len(rec_data)} recommendations")
            else:
                print(f"Note: {rec_response.status_code}")
            
            print("\n" + "="*70)
            print("AUTHENTICATION TEST COMPLETE!")
            print("="*70)
            print(f"\nYour token for API testing:")
            print(f"Bearer {token}")
            print("\nUse this in Swagger UI (http://localhost:8000/docs):")
            print("1. Click the Authorize button")
            print(f"2. Paste: Bearer {token}")
            print("3. Click Authorize")
            print("\nOr use in code:")
            print(f'headers = {{"Authorization": "Bearer {token}"}}')
            
        else:
            error = response.json() if response.status_code != 500 else response.text
            if response.status_code == 400 and "already exists" in str(error):
                print("\nUser already exists! Testing login instead...")
                
                # Try login
                print("\n[1/4] Logging in with existing user...")
                login_response = requests.post(
                    f"{BASE_URL}/auth/login",
                    data={"username": "demouser", "password": "Demo123456"}
                )
                
                if login_response.status_code == 200:
                    data = login_response.json()
                    token = data['access_token']
                    print(f"Success! Logged in")
                    print(f"  Token: {token[:40]}...")
                    
                    print("\n" + "="*70)
                    print(f"\nYour token:")
                    print(f"Bearer {token}")
                else:
                    print(f"Login failed: {login_response.text}")
            else:
                print(f"Registration failed: {response.status_code}")
                print(f"Error: {error}")
    
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to server!")
        print("Make sure the server is running:")
        print("  cd backend")
        print("  python start_server_clean.py")
    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    test_auth()
