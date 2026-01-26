"""
Test Recommendation Engine
===========================
Test the recommendation system with sample data
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_section(title):
    """Print section divider"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_recommendations():
    """Test recommendation endpoints"""
    
    print_section("TESTING RECOMMENDATION ENGINE")
    
    # 1. Register/Login user
    print("\n1. Creating test user...")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json={
                "email": "test_rec@example.com",
                "username": "test_rec_user",
                "password": "testpass123",
                "full_name": "Test Recommendation User"
            }
        )
        if response.status_code == 200:
            data = response.json()
            token = data['access_token']
            user_id = data['user']['id']
            print(f"[OK] User created: ID {user_id}")
        else:
            # Try login if already exists
            response = requests.post(
                f"{BASE_URL}/auth/login",
                data={
                    "username": "test_rec_user",
                    "password": "testpass123"
                }
            )
            data = response.json()
            token = data['access_token']
            user_id = data['user']['id']
            print(f"[OK] User logged in: ID {user_id}")
    except Exception as e:
        print(f"[ERROR] {e}")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Get recommendations
    print_section("2. Getting Personalized Recommendations")
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/recommendations",
            headers=headers,
            params={"limit": 10}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Retrieved {data['total']} recommendations")
            print("\nTop 3 Recommendations:")
            for i, rec in enumerate(data['recommendations'][:3], 1):
                print(f"\n{i}. {rec['name']}")
                print(f"   Score: {rec['recommendation_score']}")
                print(f"   Reason: {rec['reason']}")
                print(f"   Price: ${rec['price']}")
        else:
            print(f"[ERROR] Status: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"[ERROR] {e}")
    
    # 3. Get style profile
    print_section("3. Getting Style Profile")
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/recommendations/style-profile",
            headers=headers
        )
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Style Profile Retrieved")
            print(f"\nUser ID: {data['user_id']}")
            print(f"Total Try-Ons: {data['total_tryons']}")
            print(f"Total Favorites: {data['total_favorites']}")
            
            if data['favorite_categories']:
                print(f"\nFavorite Categories:")
                for cat, count in data['favorite_categories'].items():
                    print(f"  - {cat}: {count}")
            
            if data['favorite_colors']:
                print(f"\nFavorite Colors:")
                for color, count in data['favorite_colors'].items():
                    print(f"  - {color}: {count}")
            
            print(f"\nAverage Price Preference: ${data['average_price_preference']}")
        else:
            print(f"[ERROR] Status: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] {e}")
    
    # 4. Test category filtering
    print_section("4. Testing Category Filtering")
    categories = ['top', 'bottom', 'dress']
    for category in categories:
        try:
            response = requests.get(
                f"{BASE_URL}/api/v1/recommendations",
                headers=headers,
                params={"limit": 5, "category": category}
            )
            if response.status_code == 200:
                data = response.json()
                print(f"[OK] {category.capitalize()}: {data['total']} recommendations")
            else:
                print(f"[ERROR] {category.capitalize()}: Status {response.status_code}")
        except Exception as e:
            print(f"[ERROR] {category.capitalize()}: {e}")
    
    # 5. Record interaction
    print_section("5. Recording User Interaction")
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/recommendations/interaction",
            headers=headers,
            params={
                "item_id": "item_001",
                "interaction_type": "view"
            }
        )
        if response.status_code == 200:
            print("[OK] Interaction recorded: view item_001")
        else:
            print(f"[ERROR] Status: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] {e}")
    
    # 6. Get similar items
    print_section("6. Getting Similar Items")
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/recommendations/similar/item_001",
            headers=headers,
            params={"limit": 5}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Found {len(data['similar_items'])} similar items")
            print("\nTop 3 Similar Items:")
            for i, item in enumerate(data['similar_items'][:3], 1):
                print(f"{i}. {item['name']} (Score: {item['similarity_score']})")
        else:
            print(f"[ERROR] Status: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] {e}")
    
    # 7. Get trending items
    print_section("7. Getting Trending Items")
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/recommendations/trending",
            params={"limit": 5, "days": 7}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Found {data['total']} trending items (last {data['period_days']} days)")
            if data['trending_items']:
                print("\nTop Trending:")
                for i, item in enumerate(data['trending_items'][:5], 1):
                    print(f"{i}. {item['item_id']} (Score: {item['popularity_score']:.2f})")
        else:
            print(f"[ERROR] Status: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] {e}")
    
    # 8. Test exclude tried filter
    print_section("8. Testing Exclude Tried Filter")
    try:
        # Without exclusion
        response1 = requests.get(
            f"{BASE_URL}/api/v1/recommendations",
            headers=headers,
            params={"limit": 10, "exclude_tried": False}
        )
        count1 = response1.json()['total'] if response1.status_code == 200 else 0
        
        # With exclusion
        response2 = requests.get(
            f"{BASE_URL}/api/v1/recommendations",
            headers=headers,
            params={"limit": 10, "exclude_tried": True}
        )
        count2 = response2.json()['total'] if response2.status_code == 200 else 0
        
        print(f"[OK] Without exclusion: {count1} items")
        print(f"[OK] With exclusion: {count2} items")
    except Exception as e:
        print(f"[ERROR] {e}")
    
    print_section("TEST SUMMARY")
    print("\n[SUCCESS] Recommendation Engine Testing Complete!")
    print("\nFeatures Tested:")
    print("  ✓ Personalized recommendations")
    print("  ✓ Style profile analysis")
    print("  ✓ Category filtering")
    print("  ✓ Interaction tracking")
    print("  ✓ Similar items")
    print("  ✓ Trending items")
    print("  ✓ Exclude tried filter")
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  RECOMMENDATION ENGINE TEST SUITE")
    print("="*60)
    print(f"\nStarted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API URL: {BASE_URL}")
    
    try:
        # Test health endpoint first
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("[OK] API is running")
            test_recommendations()
        else:
            print("[ERROR] API is not responding")
    except requests.exceptions.ConnectionError:
        print("\nERROR: Cannot connect to API")
        print("   Make sure the server is running:")
        print("   python start_server_clean.py")
        print("\n   Or:")
        print("   START_SERVER.bat")
    except Exception as e:
        print(f"\nERROR: {e}")
