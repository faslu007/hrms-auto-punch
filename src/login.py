from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.driver_apis.btn_driver_apis import get_btn_by_id_and_click
from utils.driver_apis.insert_input_driver_apis import enter_text_input_by_id_with_delay, enter_text_input_by_name_with_delay
from utils.util_functions import go_to_desired_page
from utils.driver_apis.wait_apis import wait_for_element_to_be_visible
import sqlite3
from datetime import datetime, timedelta
import os

login_page_element_targets = {
    "username": "user_id",
    "password": "password",
    "login-button": "login",
    "punch_out_button": "checkout",
    "punch_in_button": "checkin"
}


# Get the absolute path to the audio file
audio_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'utils', 'success-1-6297.mp3'))

# Convert file path to proper URL format
audio_url = f"file://{audio_path.replace(os.sep, '/')}"


def initialize_database():
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    
    # Create tables if they don't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action_type TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            status TEXT NOT NULL,
            error_message TEXT
        )
    ''')
    
    conn.commit()
    return conn, cursor

def log_attendance_action(action_type, status, error_message=None):
    try:
        conn, cursor = initialize_database()
        cursor.execute('''
            INSERT INTO attendance_logs (action_type, timestamp, status, error_message)
            VALUES (?, ?, ?, ?)
        ''', (action_type, datetime.now(), status, error_message))
        conn.commit()
    finally:
        conn.close()

def get_last_action():
    try:
        conn, cursor = initialize_database()
        cursor.execute('''
            SELECT action_type, timestamp 
            FROM attendance_logs 
            WHERE status = 'success'
            ORDER BY timestamp DESC 
            LIMIT 1
        ''')
        return cursor.fetchone()
    finally:
        conn.close()

def login(driver, username, password, url):
    try:

        go_to_desired_page(driver, url)
        
        wait_for_element_to_be_visible(driver, login_page_element_targets["username"], "id")
    
        enter_text_input_by_id_with_delay(driver, login_page_element_targets["username"], username, 0.3)

        enter_text_input_by_name_with_delay(driver, login_page_element_targets["password"], password, 0.3)

        get_btn_by_id_and_click(driver, login_page_element_targets["login-button"])
        
        # Wait for the company name text to be present
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Cascade Revenue Management Pvt Ltd')]"))
        )

        return True

    except Exception as e:
        print(f"Login failed: {str(e)}")
        return False


def punch_out(driver):
    try:
        # Check last action to prevent double punch-out
        last_action = get_last_action()
        if last_action and last_action[0] == 'punch_out':
            print("Already punched out. Last punch-out was at:", last_action[1])
            return False
        
        # Wait for the check-out button to be visible
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, login_page_element_targets["punch_out_button"]))
        )
        
        get_btn_by_id_and_click(driver, login_page_element_targets["punch_out_button"])
        
        driver.execute_script("""
            const waitingText = document.createElement('h3');
            waitingText.textContent = 'Waiting for 10 seconds to PUNCH OUT get effective...';
            waitingText.style.textAlign = 'center';
            waitingText.style.color = '#666';
            waitingText.style.backgroundColor = '#fff3cd';
            waitingText.style.padding = '10px';
            waitingText.style.margin = '0';
            document.body.insertBefore(waitingText, document.body.firstChild);
            setTimeout(() => waitingText.remove(), 10000);
        """)
        
        driver.implicitly_wait(10)
        
        # Wait for the check-in button to be visible (confirms successful punch out)
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "checkin"))
        )
        
        driver.implicitly_wait(3)
        
        driver.execute_script("""
            const audio = new Audio(arguments[0]);
            audio.play().catch(e => console.log('Audio play failed:', e));
        """, audio_url)
        
        # Log successful punch out
        log_attendance_action('punch_out', 'success')
        return True
        
    except Exception as e:
        error_message = str(e)
        print(f"Punch out failed: {error_message}")
        # Log failed punch out
        log_attendance_action('punch_out', 'failed', error_message)
        return False

def punch_in(driver):
    try:
        # Check last action to prevent double punch-in
        last_action = get_last_action()
        if last_action and last_action[0] == 'punch_in':
            print("Already punched in. Last punch-in was at:", last_action[1])
            return False
            
        # Wait for the check-in button to be visible
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, login_page_element_targets["punch_in_button"]))
        )
        
        get_btn_by_id_and_click(driver, login_page_element_targets["punch_in_button"])
        driver.execute_script("""
            const waitingText = document.createElement('h3');
            waitingText.textContent = 'Waiting for 10 seconds to PUNCH IN get effective...';
            waitingText.style.textAlign = 'center';
            waitingText.style.color = '#666';
            waitingText.style.backgroundColor = '#fff3cd';
            waitingText.style.padding = '10px';
            waitingText.style.margin = '0';
            document.body.insertBefore(waitingText, document.body.firstChild);
            setTimeout(() => waitingText.remove(), 10000);
        """)
        driver.implicitly_wait(10)
        # Wait for the checkout button to be visible (confirms successful punch in)
        WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.ID, 'checkout'))
        )
        
        driver.execute_script("""
            const audio = new Audio(arguments[0]);
            audio.play().catch(e => console.log('Audio play failed:', e));
        """, audio_url)
        
        driver.implicitly_wait(5)
        
        # Log successful punch in
        log_attendance_action('punch_in', 'success')
        return True
        
    except Exception as e:
        error_message = str(e)
        print(f"Punch in failed: {error_message}")
        # Log failed punch in
        log_attendance_action('punch_in', 'failed', error_message)
        return False

def get_attendance_history(days=7):
    try:
        conn, cursor = initialize_database()
        cursor.execute('''
            SELECT action_type, timestamp, status, error_message
            FROM attendance_logs
            WHERE timestamp >= date('now', ?)
            ORDER BY timestamp DESC
        ''', (f'-{days} days',))
        return cursor.fetchall()
    finally:
        conn.close()

def determine_next_action(driver):
    """
    Determines whether to punch in or out based on last recorded action
    Returns: tuple (action_type, message)
    where action_type is either 'punch_in' or 'punch_out'
    """
    try:
        last_action = get_last_action()
        current_time = datetime.now()
        
        if last_action:
            last_action_type, last_timestamp = last_action
            last_timestamp = datetime.strptime(last_timestamp, '%Y-%m-%d %H:%M:%S.%f')
            
            # If last action was more than 12 hours ago, assume new day
            if current_time - last_timestamp > timedelta(hours=12):
                return ('punch_in', "New day detected, attempting punch in...")
                
            # If last action was punch in, do punch out
            elif last_action_type == 'punch_in':
                return ('punch_out', "Last action was punch in, attempting punch out...")
                
            # If last action was punch out, do punch in
            elif last_action_type == 'punch_out':
                return ('punch_in', "Last action was punch out, attempting punch in...")
        
        # No previous actions found, default to punch in
        return ('punch_in', "No previous actions found, attempting punch in...")
        
    except Exception as e:
        print(f"Error determining next action: {str(e)}")
        return None

def execute_attendance_action(driver):
    """
    Executes the appropriate attendance action (punch in/out)
    Returns: bool indicating success/failure
    """
    try:
        next_action, message = determine_next_action(driver)
        print(message)
        
        success = False
        if next_action == 'punch_in':
            success = punch_in(driver)
        else:
            success = punch_out(driver)
            if success:
                # Get and display the duration after successful action
                duration = get_todays_time_difference()
                duration_str = format_duration(duration)
                hours = duration[0][0] if duration and duration[0] else 0
                
                # JavaScript to create and show modal with conditional styling
                js_code = """
                    const badge = document.createElement('div');
                    badge.style.position = 'fixed';
                    badge.style.top = '20px';
                    badge.style.left = '50%';
                    badge.style.transform = 'translateX(-50%)';
                    badge.style.backgroundColor = 'white';
                    badge.style.padding = '10px 20px';
                    badge.style.borderRadius = '5px';
                    badge.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)';
                    badge.style.zIndex = '1000';

                    const duration = document.createElement('h1');
                    duration.style.fontWeight = 'bold';
                    duration.style.color = arguments[1] < 8 ? '#ff0000' : '#000000';
                    duration.style.margin = '0';
                    duration.textContent = 'Your work hours for today: ' + arguments[0];

                    badge.appendChild(duration);
                    document.body.insertBefore(badge, document.body.firstChild);

                    setTimeout(() => {
                        badge.remove();
                    }, 10000);
                """
                driver.execute_script(js_code, duration_str, hours)
                driver.implicitly_wait(5)
            
        return success
            
    except Exception as e:
        print(f"Error executing attendance action: {str(e)}")
        return False

def get_todays_time_difference():
    """
    Calculate time difference between punch-in and punch-out for the current day
    Returns: tuple (hours, minutes) or None if no complete pair found
    """
    try:
        conn, cursor = initialize_database()
        
        # Get today's date at midnight
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Get all successful actions for today
        cursor.execute('''
            SELECT action_type, timestamp 
            FROM attendance_logs 
            WHERE status = 'success'
            AND timestamp >= ?
            ORDER BY timestamp ASC
        ''', (today_start,))
        
        actions = cursor.fetchall()
        
        if not actions:
            return None, "No attendance records found for today"
            
        # Initialize variables
        last_punch_in = None
        total_duration = timedelta()
        
        # Process all actions chronologically
        for action_type, timestamp in actions:
            timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')
            
            if action_type == 'punch_in':
                last_punch_in = timestamp
            elif action_type == 'punch_out' and last_punch_in:
                duration = timestamp - last_punch_in
                total_duration += duration
                last_punch_in = None
        
        # If there's an ongoing session (punch-in without punch-out)
        if last_punch_in:
            current_duration = datetime.now() - last_punch_in
            total_duration += current_duration
            status_message = "Current session is ongoing"
        else:
            status_message = "Last session completed"
            
        # Convert total duration to hours and minutes
        total_seconds = total_duration.total_seconds()
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        
        return (hours, minutes), status_message
        
    except Exception as e:
        print(f"Error calculating time difference: {str(e)}")
        return None, f"Error: {str(e)}"
    finally:
        conn.close()

def format_duration(duration_tuple):
    """
    Format the duration tuple into a readable string
    """
    if not duration_tuple or duration_tuple[0] is None:
        return "No duration available"
        
    (hours, minutes), status = duration_tuple
    duration_str = f"{hours} hours and {minutes} minutes"
    return f"{duration_str} ({status})"