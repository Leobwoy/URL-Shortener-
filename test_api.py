import requests
import json

BASE_URL = "http://localhost:5000"

def test_api():
    print("=== URL Shortener API Test ===\n")
    
    # 1. Create a short URL
    print("1. Creating short URL...")
    response = requests.post(
        f"{BASE_URL}/shorten",
        json={"long_url": "https://www.github.com"},
        headers={"Content-Type": "application/json"}
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    
    if response.status_code == 201:
        short_code = response.json()["short_url"].split("/")[-1]
        print(f"   Short code: {short_code}\n")
        
        # 2. Get analytics
        print("2. Getting analytics...")
        response = requests.get(f"{BASE_URL}/analytics/{short_code}")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}\n")
        
        # 3. Test redirect
        print("3. Testing redirect...")
        response = requests.get(f"{BASE_URL}/{short_code}", allow_redirects=False)
        print(f"   Status: {response.status_code}")
        print(f"   Location: {response.headers.get('Location', 'No redirect')}\n")
        
        # 4. Get specific URL details
        print("4. Getting URL details...")
        response = requests.get(f"{BASE_URL}/urls/{short_code}")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}\n")
        
        # 5. Update URL
        print("5. Updating URL...")
        response = requests.put(
            f"{BASE_URL}/urls/{short_code}",
            json={"long_url": "https://www.stackoverflow.com"},
            headers={"Content-Type": "application/json"}
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}\n")
        
        # 6. Get all URLs
        print("6. Getting all URLs...")
        response = requests.get(f"{BASE_URL}/urls")
        print(f"   Status: {response.status_code}")
        print(f"   Total URLs: {response.json()['total']}")
        print(f"   URLs: {json.dumps(response.json()['urls'], indent=2)}\n")
        
        # 7. Delete URL
        print("7. Deleting URL...")
        response = requests.delete(f"{BASE_URL}/urls/{short_code}")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}\n")
        
        # 8. Verify deletion
        print("8. Verifying deletion...")
        response = requests.get(f"{BASE_URL}/urls")
        print(f"   Status: {response.status_code}")
        print(f"   Total URLs: {response.json()['total']}")
    
    print("\n=== All tests completed! ===")

if __name__ == "__main__":
    test_api()
