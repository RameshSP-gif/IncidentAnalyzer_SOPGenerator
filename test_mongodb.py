"""Test MongoDB connection and setup"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_mongodb():
    """Test MongoDB connection"""
    print("\n" + "="*60)
    print("Testing MongoDB Connection")
    print("="*60 + "\n")
    
    try:
        from pymongo import MongoClient
        from pymongo.errors import ServerSelectionTimeoutError
        
        # Try to connect
        print("1. Attempting to connect to MongoDB...")
        client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
        
        # Test connection
        print("2. Testing connection...")
        client.admin.command('ping')
        
        print("✅ SUCCESS: MongoDB is running and accessible!")
        print(f"   Server Info: {client.server_info()['version']}")
        
        # Test database operations
        print("\n3. Testing database operations...")
        db = client['incident_analyzer']
        collection = db['incidents']
        
        # Test insert
        test_doc = {"test": "document", "timestamp": "2026-01-12"}
        result = collection.insert_one(test_doc)
        print(f"✅ Insert successful: {result.inserted_id}")
        
        # Test find
        found = collection.find_one({"_id": result.inserted_id})
        print(f"✅ Find successful: {found}")
        
        # Clean up test document
        collection.delete_one({"_id": result.inserted_id})
        print(f"✅ Delete successful")
        
        # Get stats
        count = collection.count_documents({})
        print(f"\n📊 Current incidents in database: {count}")
        
        client.close()
        return True
        
    except ServerSelectionTimeoutError:
        print("❌ ERROR: Cannot connect to MongoDB")
        print("\nPossible reasons:")
        print("  1. MongoDB is not installed")
        print("  2. MongoDB service is not running")
        print("  3. MongoDB is running on a different port")
        print("\n📖 Solutions:")
        print("  Windows: net start MongoDB")
        print("  Or install: choco install mongodb")
        print("  Or use MongoDB Atlas (cloud): https://www.mongodb.com/atlas")
        return False
        
    except ImportError:
        print("❌ ERROR: pymongo not installed")
        print("\n📖 Solution:")
        print("  pip install pymongo")
        return False
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_mongodb()
    sys.exit(0 if success else 1)
