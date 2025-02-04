import os
import shutil
from datetime import datetime
import logging
import json

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By



def clean_or_create_default_download_directory():
    # Gets the home directory of the system
    home_dir = os.path.expanduser('~')
    download_dir = os.path.join(home_dir, 'automation_downloads')

    # Delete all files in the download directory before the test initializes
    if os.path.exists(download_dir):
        for filename in os.listdir(download_dir):
            file_path = os.path.join(download_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')

    # Ensure the download directory exists
    os.makedirs(download_dir, exist_ok=True)
    return download_dir


def format_date(date_str, desired_format="%m/%d/%Y"):
    # Define possible input formats
    possible_formats = ["%Y%m%d", "%m%d%Y", "%m%d%y", "%Y-%m-%d", "%m-%d-%Y", "%m-%d-%y", "%Y/%m/%d", "%m/%d/%Y", "%m/%d/%y"]

    for input_format in possible_formats:
        try:
            # Try to parse the date string to a datetime object
            date_obj = datetime.strptime(date_str, input_format)
            # Format the datetime object to the desired format
            return date_obj.strftime(desired_format)
        except ValueError:
            # If parsing fails, continue to try the next format
            continue
    
    # If none of the formats matched, raise an error
    raise ValueError(f"Unsupported date format: {date_str}")


def get_required_fields(*element_classes):
    required_fields = []
    
    for element_class in element_classes:
        for name, element in element_class.__members__.items():
            if element.value.required:
                required_fields.append(element)
    
    return required_fields


def go_to_desired_page(driver, page_url):
    try:
        if driver.current_url != page_url:
            driver.get(page_url)

            # Wait until the URL is updated
            WebDriverWait(driver, 30).until(EC.url_to_be(page_url))

            # Wait until the page is completely loaded
            WebDriverWait(driver, 30).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            
        # Wait for the "Loading..." element to become invisible
        WebDriverWait(driver, 60).until(
            EC.invisibility_of_element_located((By.XPATH, "//p[text()='Loading...']"))
        )
        # Wait until the document is fully loaded and ready for interaction
        WebDriverWait(driver, 60).until(
            lambda driver: driver.execute_script("return document.readyState") == "complete"
        )
        return True
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"An error occurred while getting the page with url {page_url}")
        return False


def load_patient_data_from_file(file_path):
    """Load patient data from a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Failed to load patient data from {file_path}: {e}")
        return None

def get_mock_data(data_type):
    """Load mock data from a JSON file.

    Args:
        data_type (str): Type of data needed to pull from the local directory. Currently, only "patient_mock" is supported.

    Returns:
        dict or None: Returns the mock data as a dictionary if successful, or None if an error occurs.
    
    Raises:
        ValueError: If the provided data_type does not match any supported types.
    """
    root_dir = os.path.dirname(os.path.abspath(__file__))

    try:
        if data_type == "patient_mock":
            patient_data_file = os.path.join(root_dir, 'mock_data/patient_mock.json')
            return load_patient_data_from_file(patient_data_file)
        else:
            raise ValueError(f"Unsupported data type: {data_type}. Supported types are: 'patient_mock', 'claim_mock'.")
    except Exception as e:
        print(f"An error occurred while getting mock data: {e}")
        return None


remove_selection_from_select_box_js_script = """
    // Construct the selector to match the element with specific attributes
    const selector = 'li[data-value=""][role="option"]';

    // Use querySelector to get the element based on the constructed selector
    const element = document.querySelector(selector);

    // Check if the element exists and contains the exact text 'Select'
    if (element && element.textContent.trim() === 'Select') {
        // Trigger a click event on the element
        element.click();
        console.log("cleared")
    } else {
        console.error('Element not found or does not match the specified text.');
    }
"""


def select_single_box_item_using_text_and_js_script(text_value):
    script = f"""
    // Construct the selector to match the element with the exact text
    const selector = 'li[role="option"] > div';
    
    // Use querySelectorAll to get all matching elements
    const elements = document.querySelectorAll(selector);
    
    // Iterate over the elements to find the one with the exact text
    for (let element of elements) {{
        if (element.textContent.trim() === '{text_value}') {{
            // Trigger a click event on the parent element (li)
            element.parentElement.click();
            
            // Validate if the correct item is selected
            if (element.parentElement.getAttribute('aria-selected') === 'true') {{
                console.log('{text_value} option selected.');
                return true;
            }} else {{
                console.error('{text_value} option not selected correctly.');
                return false;
            }}
        }}
    }}
    
    // If no matching element is found, return false
    console.error('Element not found with the specified text.');
    return false;
    """
    return script


def reset_single_box_item_using_text_and_js_script(text_value):
    script = f"""
    // Construct the selector to match the element with the exact text
    const selector = 'li[role="option"]';
    
    // Use querySelectorAll to get all matching elements
    const elements = document.querySelectorAll(selector);
    
    // Iterate over the elements to find the one with the exact text
    for (let element of elements) {{
        if (element.innerText.trim() === '{text_value}') {{
            // Trigger a click event on the parent element (li)
            element.click();
            
            // Validate if the correct item is selected
            if (element.getAttribute('aria-selected') === 'true') {{
                console.log('{text_value} option selected.');
                return true;
            }} else {{
                console.error('{text_value} option not selected correctly.');
                return false;
            }}
        }}
    }}
    
    // If no matching element is found, return false
    console.error('Element not found with the specified text.');
    return false;
    """
    return script
