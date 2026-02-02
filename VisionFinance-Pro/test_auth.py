from quant_core.auth.user_manager import UserManager
import os

def test_auth():
    print("Testing Auth...")
    db_path = "test_users.db"
    if os.path.exists(db_path):
        os.remove(db_path)
        
    um = UserManager(db_path=db_path)
    
    # Test Register
    ok, msg = um.register("testuser", "password123")
    print(f"Register: {ok} - {msg}")
    
    # Test Duplicate
    ok, msg = um.register("testuser", "password123")
    print(f"Duplicate: {not ok} - {msg}")
    
    # Test Login Success
    logged_in = um.login("testuser", "password123")
    print(f"Login Success: {logged_in}")
    
    # Test Login Fail
    logged_in = um.login("testuser", "wrongpass")
    print(f"Login Fail: {not logged_in}")

    # Cleanup
    if os.path.exists(db_path):
        os.remove(db_path)

if __name__ == "__main__":
    test_auth()
