from login import login, execute_attendance_action
from history_viewer import HistoryViewer
from history_data import AttendanceHistory
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import sqlite3
import getpass
from cryptography.fernet import Fernet
import os
import time

def initialize_database():
    # Create a database connection
    conn = sqlite3.connect('credentials.db')
    cursor = conn.cursor()
    
    # Create table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS credentials
        (id INTEGER PRIMARY KEY,
         username TEXT NOT NULL,
         password TEXT NOT NULL,
         url TEXT NOT NULL,
         key TEXT NOT NULL)
    ''')
    conn.commit()
    return conn, cursor

def get_credentials():
    conn, cursor = initialize_database()
    
    try:
        # Check if credentials exist
        cursor.execute('SELECT username, password, url, key FROM credentials LIMIT 1')
        result = cursor.fetchone()
        
        
        if result:
            # Decrypt existing credentials
            username, encrypted_password, url, key = result
            f = Fernet(key.encode())
            password = f.decrypt(encrypted_password.encode()).decode()
            return username, password, url
        else:
            # Get new credentials from user
            print("No stored credentials found. Please enter your login details.")
            username = input("Username: ")
            password = getpass.getpass("Password: ")
            url = input("URL: ")
            # Generate encryption key
            key = Fernet.generate_key()
            f = Fernet(key)
            
            # Encrypt password
            encrypted_password = f.encrypt(password.encode()).decode()
            
            # Store credentials
            cursor.execute('''
                INSERT INTO credentials (username, password, url, key)
                VALUES (?, ?, ?, ?)
            ''', (username, encrypted_password, url, key.decode()))
            conn.commit()
            
            return username, password, url
    finally:
        conn.close()

def main():
    try:
        # Get credentials
        username, password, url = get_credentials()
        
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument('--start-minimized')
        chrome_options.add_argument('--use-fake-ui-for-media-stream')
        chrome_options.add_argument('--allow-geolocation')
        chrome_options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.geolocation": 1
        })
        
        # Initialize the Chrome WebDriver
        driver = webdriver.Chrome(options=chrome_options)
        
        portal_login_success = login(driver, username, password, url)
        
        if portal_login_success:
            print("Login successful")
            success = execute_attendance_action(driver)
            if success:
                print("Attendance action completed successfully")
                # Show attendance history
                history = AttendanceHistory()
                viewer = HistoryViewer(driver)
                viewer.create_history_tab(history.get_history())
                # Switch back to main tab
                driver.switch_to.window(driver.window_handles[0])
            else:
                print("Attendance action failed")
        else:
            print("Login failed")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    
    finally:
        if 'driver' in locals():
            try:
                
                
                # Add a close button to the page
                driver.execute_script("""
                    const closeDiv = document.createElement('div');
                    closeDiv.style.position = 'fixed';
                    closeDiv.style.bottom = '20px';
                    closeDiv.style.left = '50%';
                    closeDiv.style.transform = 'translateX(-50%)';
                    closeDiv.style.zIndex = '10000';
                    
                    const closeButton = document.createElement('button');
                    closeButton.textContent = 'Close Browser';
                    closeButton.style.padding = '10px 20px';
                    closeButton.style.fontSize = '16px';
                    closeButton.style.cursor = 'pointer';
                    closeButton.style.backgroundColor = '#dc3545';
                    closeButton.style.color = 'white';
                    closeButton.style.border = 'none';
                    closeButton.style.borderRadius = '5px';
                    
                    closeButton.onclick = function() {
                        window.localStorage.setItem('browserClose', 'true');
                    };
                    
                    closeDiv.appendChild(closeButton);
                    document.body.appendChild(closeDiv);
                """)
                
                # Wait for either user input or 1 hour timeout
                start_time = time.time()
                one_hour = 3600  # 1 hour in seconds
                
                while time.time() - start_time < one_hour:
                    result = driver.execute_script("return window.localStorage.getItem('browserClose');")
                    if result == 'true':
                        break
                    time.sleep(1)  # Check every second
                
                driver.quit()
            except Exception as e:
                print(f"Error during browser closure: {str(e)}")
                driver.quit()

if __name__ == "__main__":
    main()