"""
Below are utility functions to access Selenium Driver APIs to insert data into the DOM
"""
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.support.wait import WebDriverWait
import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from utils.util_functions import (
    select_single_box_item_using_text_and_js_script,
    reset_single_box_item_using_text_and_js_script
)


def enter_text_input_by_id(driver, target_id, value):
    element = driver.find_element(By.ID, target_id)
    element.send_keys(Keys.CONTROL + "a")  # For Windows/Linux
    element.send_keys(Keys.COMMAND + "a")  # For Mac
    element.send_keys(Keys.BACKSPACE)
    
    if value == "":
        return    
    
    element.send_keys(value)


def enter_text_input_by_id_with_delay(driver, target_id, value, delay=0.1):
    element = driver.find_element(By.ID, target_id)
    # Clear existing text
    element.send_keys(Keys.CONTROL + "a")  # For Windows/Linux
    element.send_keys(Keys.COMMAND + "a")  # For Mac
    element.send_keys(Keys.BACKSPACE)
    
    if value == "":
        return
    
    # Type each character with a delay
    for char in value:
        element.send_keys(char)
        time.sleep(delay)  # 

def enter_text_input_by_name_with_delay(driver, target_name, value, delay=0.1):
    element = driver.find_element(By.NAME, target_name)
    # Clear existing text
    element.send_keys(Keys.CONTROL + "a")  # For Windows/Linux
    element.send_keys(Keys.COMMAND + "a")  # For Mac
    element.send_keys(Keys.BACKSPACE)
    
    if value == "":
        return
    
    # Type each character with a delay
    for char in value:
        element.send_keys(char)
        time.sleep(delay)  #     

def choose_select_box_item_by_id(driver, target_id, value):
    try:
        # Wait for the select box to be clickable
        select_box = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.ID, target_id))
        )
        select_box.click()
        
        time.sleep(1)
        
        if value == 'Select':
            selected_status = driver.execute_script(reset_single_box_item_using_text_and_js_script(value))
        # Execute the script and capture the result
        else:
            selected_status = driver.execute_script(select_single_box_item_using_text_and_js_script(value))
        
        # Handle the selection result
        if selected_status != True:
            raise ValueError(f"{value} not selected")

    except NoSuchElementException:
        raise ValueError(f"Select box with ID '{target_id}' not found.")
    
    except ElementNotInteractableException:
        raise ValueError(f"Select box with ID '{target_id}' is not interactable.")
    
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise
    
    
def click_on_check_box_by_id(driver, id):
    # Wait for the element to be present before attempting to click
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, id)))
    # Check if the element is not null, then click
    driver.execute_script(f"var elem = document.getElementById('{id}'); if(elem) elem.click(); else console.error('Element with ID ' + '{id}' + ' not found.');")
