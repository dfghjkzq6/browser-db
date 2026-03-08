#!/usr/bin/env python3
import json
import sqlite3
from datetime import datetime

def convert_cookies_to_storagestate():
    cookies_db = "/home/zam/snap/chromium/common/chromium/Default/Cookies"
    
    conn = sqlite3.connect(cookies_db)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT name, value, host_key, path, expires_utc, is_secure, is_httponly, samesite
        FROM cookies
    """)
    
    cookies_data = cursor.fetchall()
    conn.close()
    
    storage_state = {
        "cookies": [],
        "origins": []
    }
    
    for cookie in cookies_data:
        name, value, domain, path, expires_utc, is_secure, is_httponly, samesite = cookie
        
        if expires_utc:
            webkit_epoch = datetime(1601, 1, 1)
            chrome_timestamp = expires_utc / 1000000
            expires = int((webkit_epoch.timestamp() + chrome_timestamp))
        else:
            expires = -1
        
        sameSite_map = {
            0: "Strict",
            1: "Lax", 
            2: "None",
            -1: None
        }
        sameSite = sameSite_map.get(samesite, None)
        
        storage_state["cookies"].append({
            "name": name,
            "value": value,
            "domain": domain,
            "path": path,
            "expires": expires,
            "httpOnly": bool(is_httponly),
            "secure": bool(is_secure),
            "sameSite": sameSite
        })
    
    with open("/home/zam/storagestate.json", "w") as f:
        json.dump(storage_state, f, indent=2)
    
    print(f"Converted {len(cookies_data)} cookies to storagestate.json")
    print(f"File saved to: /home/zam/storagestate.json")

if __name__ == "__main__":
    convert_cookies_to_storagestate()
