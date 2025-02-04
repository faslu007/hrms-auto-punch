from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


def wait_for_aria_selected_true(driver, element_locator, locator_type, timeout=60):
    try:
        target_type = None
        if locator_type == 'id':
            target_type = By.ID
        elif locator_type == 'class':
            target_type = By.CLASS_NAME
        # Define a custom expected condition
        def aria_selected_true(driver):
            element = driver.find_element(target_type, element_locator)
            return element.get_attribute("aria-selected") == "true"
        
        # Wait until the custom condition is met
        WebDriverWait(driver, timeout).until(aria_selected_true)
        print("The button's 'aria-selected' attribute is now 'true'.")
    except TimeoutException:
        print(f"Timeout: The button's 'aria-selected' attribute did not become 'true' within {timeout} seconds.")
        return "TimeoutException: The attribute did not become 'true' within the given time."
    
def wait_for_element_to_be_visible(driver, element_locator, locator_type, timeout=60):
    try:
        target_type = None
        if locator_type == 'id':
            target_type = By.ID
        elif locator_type == 'class':
            target_type = By.CLASS_NAME 
        elif locator_type == 'xpath':
            target_type = By.XPATH
        elif locator_type == 'css':
            target_type = By.CSS_SELECTOR
            
        WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((target_type, element_locator))
        )
        print(f"Element {element_locator} is now visible.")
    except TimeoutException:
        print(f"Timeout: Element {element_locator} did not become visible within {timeout} seconds.")
        return "TimeoutException: Element did not become visible within the given time."    