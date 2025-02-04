
def scroll_into_view_by_id(driver, target_id):
    driver.execute_script(
            f"""
                document.getElementById('{target_id}').scrollIntoView({{
                    behavior: 'smooth', 
                    block: 'center', 
                    inline: 'nearest'
                }});
            """
        )