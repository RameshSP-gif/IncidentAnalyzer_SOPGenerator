#!/usr/bin/env python3
"""
Test web application endpoints
"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_homepage():
    """Test if homepage loads"""
    print("\n" + "="*70)
    print("TEST 1: Homepage")
    print("="*70)
    try:
        response = requests.get(BASE_URL)
        print(f"Status Code: {response.status_code}")
        print(f"Content Length: {len(response.text)} bytes")
        if response.status_code == 200:
            print("[OK] Homepage loads successfully")
            if "<title>" in response.text:
                title = response.text.split("<title>")[1].split("</title>")[0]
                print(f"Page Title: {title}")
        return True
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def test_get_stats():
    """Test stats endpoint"""
    print("\n" + "="*70)
    print("TEST 2: Get Statistics")
    print("="*70)
    try:
        response = requests.get(f"{BASE_URL}/get_stats")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Total Incidents: {data.get('total', 0)}")
            print(f"Categories: {data.get('categories', [])}")
            print("[OK] Stats endpoint working")
        return True
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def test_single_incident_sop():
    """Test single incident SOP generation"""
    print("\n" + "="*70)
    print("TEST 3: Single Incident SOP Generation")
    print("="*70)
    
    test_incident = {
        "number": "TEST001",
        "category": "Financial",
        "priority": "4 - Medium",
        "short_description": "Invoice amount incorrect - transport charges error",
        "description": "In invoice 405025, the transport was charged in error. The customer was charged 99 EUR for transport but should only be 49 EUR according to the order. Customer is requesting immediate correction and credit note.",
        "resolution_notes": "Issue - Invoice 405025 transport charged in error. Resolution - Resolved by RIMS and they confirmed that Credit note and debit note will be created by tomorrow. Correct invoice will be generated once night batch runs. User confirmed resolution and ticket closed."
    }
    
    try:
        print("Sending incident data...")
        response = requests.post(
            f"{BASE_URL}/generate_single_sop",
            json=test_incident,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("[OK] SOP generated successfully")
                sop = result.get('sop', '')
                print(f"\nSOP Preview (first 500 chars):")
                print(sop[:500])
                print("...")
                return True
            else:
                print(f"[ERROR] {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"[ERROR] Status {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

def test_batch_sop():
    """Test batch SOP generation"""
    print("\n" + "="*70)
    print("TEST 4: Batch SOP Generation")
    print("="*70)
    
    test_incidents = [
        {
            "short_description": "Invoice 442794 incorrect service amount charged",
            "category": "Financial",
            "description": "The invoice amount is incorrect as the service amount shown is 69.90 but the system has deducted the 10% discount twice. Customer requesting corrected invoice with proper discount calculation.",
            "resolution_notes": "Issue - Invoice 442794 double discount applied in error. Resolution - As per RIMS team update, Credit note has been created. Kindly release it from RIMS UI application. Correct invoice will be created once night batch runs. User confirmed and ticket resolved."
        },
        {
            "short_description": "Invoice missing customer reference and delivery address",
            "category": "Financial",
            "description": "OnDemand invoice is missing customer reference number and the delivery address information. Customer cannot process payment without complete invoice details.",
            "resolution_notes": "Issue - Invoice missing customer reference and delivery address. Resolution - Updated invoice template with missing customer reference from order system. Added complete delivery address from shipping records. Regenerated invoice and sent to customer. User confirmed receipt of corrected invoice."
        }
    ]
    
    try:
        print(f"Sending {len(test_incidents)} incidents...")
        response = requests.post(
            f"{BASE_URL}/generate_batch_sops",
            json={"incidents": test_incidents},
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                sops = result.get('sops', [])
                print(f"[OK] Generated {len(sops)} SOP(s)")
                for i, sop_data in enumerate(sops, 1):
                    print(f"\nSOP {i}:")
                    print(f"  Cluster: {sop_data.get('cluster_id')}")
                    print(f"  Incidents: {sop_data.get('incident_count')}")
                    print(f"  Preview: {sop_data.get('sop', '')[:200]}...")
                return True
            else:
                print(f"[ERROR] {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"[ERROR] Status {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n" + "="*70)
    print("WEB APPLICATION TESTING")
    print("="*70)
    print(f"Testing: {BASE_URL}")
    
    results = []
    results.append(("Homepage", test_homepage()))
    results.append(("Statistics", test_get_stats()))
    results.append(("Single SOP", test_single_incident_sop()))
    results.append(("Batch SOP", test_batch_sop()))
    
    print("\n" + "="*70)
    print("TEST RESULTS SUMMARY")
    print("="*70)
    
    for test_name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {test_name}")
    
    total_passed = sum(1 for _, passed in results if passed)
    print(f"\nPassed: {total_passed}/{len(results)}")
    
    if total_passed == len(results):
        print("\n[SUCCESS] All tests passed!")
    else:
        print("\n[WARNING] Some tests failed. Check the output above for details.")
