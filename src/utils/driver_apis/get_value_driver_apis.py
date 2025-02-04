"""
Below are utility functions to access Selenium Driver APIs to target 
And get data from the DOM
"""
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

def get_text_input_value_by_id(driver, target_id):
    input_element = driver.find_element(By.ID, target_id)
    return input_element.get_attribute("value")


def get_selected_option_value_by_id(driver, target_id):
    # Wait for the select element to be present and visible by ID
    select_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, target_id))
    )
    
    # Locate the div containing the selected value within the select element
    selected_option = select_element.find_element(By.XPATH, ".//div[@style and not(@style='display: none;')]")
    
    # Return the text of the selected option
    return selected_option.text


def get_text_input_value_by_name(self, target_name):
    input_element = self.driver.find_element(By.NAME, target_name)
    return input_element.get_attribute("value")