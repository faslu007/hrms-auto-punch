from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException



def get_btn_by_id_and_click(driver, target_id):
    """Wait for button to be clickable and click it"""
    element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, target_id))
    )
    element.click()


def get_btn_by_class_and_click_first_target(driver, target_class_name):
    try:
        # Wait for the element to be present in the DOM
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CLASS_NAME, target_class_name))
        )
        # Locate the element
        btn = driver.find_element(By.CLASS_NAME, target_class_name)
        # Click the button
        btn.click()
    except TimeoutException:
        print(f"Error: Timeout while waiting for element with class name '{target_class_name}' to be present.")
        return "TimeoutException: Element was not found within the given time."
    except NoSuchElementException:
        print(f"Error: Element with class name '{target_class_name}' was not found in the DOM.")
        return "NoSuchElementException: Element was not found in the DOM."
    except WebDriverException as e:
        print(f"Error: WebDriver exception occurred while interacting with element with class name '{target_class_name}': {str(e)}")
        return f"WebDriverException: {str(e)}"
    except Exception as e:
        print(f"Unexpected error occurred: {str(e)}")
        return f"UnexpectedException: {str(e)}"




def get_btn_by_id_and_trigger_click(driver, id):
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, id)))
    btn = driver.find_element(By.ID, id)
    btn.click()

def click_on_export_csv_menu_option(driver):
    btn = driver.find_element(By.XPATH, "//a[contains(.,'Export CSV')]")
    btn.click()
    
def click_on_add_new_patient_btn(driver):
    btn = driver.find_element(By.XPATH, "//button[contains(@id, 'addNewPatient')]")
    btn.click()
    
def click_on_patient_save_parent_btn(driver):
    btn = driver.find_element(By.XPATH, "//button[@id='common-btn']")
    btn.click() 