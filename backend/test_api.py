"""
Test the REST API
=================
Run this after starting: python api_endpoints.py
"""

import requests
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health check endpoint"""
    print("\n" + "="*50)
    print("Testing Health Check...")
    print("="*50)
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    return response.status_code == 200

def test_quality_presets():
    """Test quality presets endpoint"""
    print("\n" + "="*50)
    print("Testing Quality Presets...")
    print("="*50)
    
    response = requests.get(f"{BASE_URL}/api/v1/quality-presets")
    print(f"Status: {response.status_code}")
    print(f"Available presets:")
    for preset, details in response.json()["presets"].items():
        print(f"  - {preset}: {details['quality']} ({details['estimated_time']})")
    
    return response.status_code == 200

def test_virtual_tryon():
    """Test virtual try-on endpoint"""
    print("\n" + "="*50)
    print("Testing Virtual Try-On...")
    print("="*50)
    
    # Check if test images exist
    import os
    person_path = "test_images/test_user.png"
    cloth_path = "test_images/test_cloth.png"
    
    if not os.path.exists(person_path) or not os.path.exists(cloth_path):
        print(f"❌ Test images not found!")
        print(f"   Expected: {person_path} and {cloth_path}")
        return False
    
    # Send request
    print(f"Uploading images...")
    print(f"  Person: {person_path}")
    print(f"  Cloth: {cloth_path}")
    print(f"  Quality: balanced")
    print(f"\nGenerating try-on (this may take 30-60 seconds)...")
    
    start_time = time.time()
    
    with open(person_path, 'rb') as person_file, \
         open(cloth_path, 'rb') as cloth_file:
        
        files = {
            'person': ('person.png', person_file, 'image/png'),
            'cloth': ('cloth.png', cloth_file, 'image/png')
        }
        data = {'quality': 'balanced'}
        
        response = requests.post(
            f"{BASE_URL}/api/v1/try-on",
            files=files,
            data=data,
            timeout=120  # 2 minutes timeout
        )
    
    elapsed = time.time() - start_time
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ Success!")
        print(f"   Processing time: {result['processing_time']:.1f}s")
        print(f"   Total time: {elapsed:.1f}s")
        print(f"   Result ID: {result['result_id']}")
        print(f"   Result URL: {result['result_url']}")
        
        # Download result
        result_url = f"{BASE_URL}{result['result_url']}"
        print(f"\n📥 Downloading result...")
        
        download_response = requests.get(result_url)
        if download_response.status_code == 200:
            output_path = f"test_api_result.png"
            with open(output_path, 'wb') as f:
                f.write(download_response.content)
            print(f"   Saved to: {output_path}")
            
            # Try to open it
            import subprocess
            import sys
            if sys.platform == "win32":
                subprocess.run(['start', output_path], shell=True)
            print(f"\n✅ API Test Complete!")
            return True
        else:
            print(f"❌ Failed to download result")
            return False
    else:
        print(f"\n❌ Failed!")
        print(f"   Status: {response.status_code}")
        print(f"   Error: {response.text}")
        return False

def test_comparison():
    """Test comparison endpoint"""
    print("\n" + "="*50)
    print("Testing Comparison View...")
    print("="*50)
    
    import os
    person_path = "test_images/test_user.png"
    cloth_path = "test_images/test_cloth.png"
    
    if not os.path.exists(person_path) or not os.path.exists(cloth_path):
        print(f"❌ Test images not found!")
        return False
    
    print(f"Generating comparison (this may take 30-60 seconds)...")
    
    with open(person_path, 'rb') as person_file, \
         open(cloth_path, 'rb') as cloth_file:
        
        files = {
            'person': ('person.png', person_file, 'image/png'),
            'cloth': ('cloth.png', cloth_file, 'image/png')
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/comparison",
            files=files,
            timeout=120
        )
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ Success!")
        print(f"   Result ID: {result['result_id']}")
        
        # Download comparison
        comparison_url = f"{BASE_URL}{result['comparison_url']}"
        download_response = requests.get(comparison_url)
        
        if download_response.status_code == 200:
            output_path = f"test_comparison.png"
            with open(output_path, 'wb') as f:
                f.write(download_response.content)
            print(f"   Saved to: {output_path}")
            
            # Try to open it
            import subprocess
            import sys
            if sys.platform == "win32":
                subprocess.run(['start', output_path], shell=True)
            return True
        else:
            print(f"❌ Failed to download comparison")
            return False
    else:
        print(f"\n❌ Failed!")
        print(f"   Status: {response.status_code}")
        print(f"   Error: {response.text}")
        return False

def main():
    print("\n" + "="*70)
    print("🧪 Virtual Try-On API Test Suite")
    print("="*70)
    print("\nMake sure the API server is running:")
    print("  python api_endpoints.py")
    print("\nPress Enter to start tests...")
    input()
    
    results = []
    
    # Run tests
    results.append(("Health Check", test_health()))
    results.append(("Quality Presets", test_quality_presets()))
    results.append(("Virtual Try-On", test_virtual_tryon()))
    results.append(("Comparison View", test_comparison()))
    
    # Summary
    print("\n" + "="*70)
    print("📊 Test Results Summary")
    print("="*70)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {status} - {test_name}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")

if __name__ == "__main__":
    main()
