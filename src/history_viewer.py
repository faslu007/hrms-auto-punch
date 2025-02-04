from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class HistoryViewer:
    def __init__(self, driver):
        self.driver = driver
        
    def create_history_tab(self, history_data):
        """Creates a new tab and displays attendance history"""
        # Open new tab with JavaScript
        self.driver.execute_script("window.open('about:blank', 'history');")
        
        # Switch to the new tab
        self.driver.switch_to.window("history")
        
        # Create the HTML content
        html_content = self._generate_html_content(history_data)
        
        # Write the HTML content to the new tab
        self.driver.execute_script(f"document.write(`{html_content}`);")
        
    def _generate_html_content(self, history_data):
        """Generates HTML content for the history view"""
        html = """
        <html>
        <head>
            <title>Attendance History</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    background-color: #f5f5f5;
                }
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                    background-color: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                h1 {
                    color: #333;
                    text-align: center;
                    margin-bottom: 30px;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                }
                th, td {
                    padding: 12px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }
                th {
                    background-color: #f8f9fa;
                    font-weight: bold;
                }
                tr:hover {
                    background-color: #f8f9fa;
                }
                .success {
                    color: #28a745;
                }
                .failed {
                    color: #dc3545;
                }
                .date-header {
                    background-color: #e9ecef;
                    padding: 10px;
                    margin: 20px 0 10px;
                    border-radius: 4px;
                    font-weight: bold;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Attendance History</h1>
        """
        
        # Group data by date
        current_date = None
        for action in history_data:
            action_type, timestamp, status, error_message = action
            date = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f').date()
            
            if date != current_date:
                if current_date is not None:
                    html += "</table>"
                current_date = date
                html += f"""
                    <div class="date-header">{date.strftime('%A, %B %d, %Y')}</div>
                    <table>
                        <tr>
                            <th>Time</th>
                            <th>Action</th>
                            <th>Status</th>
                            <th>Details</th>
                        </tr>
                """
            
            time = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f').strftime('%I:%M:%S %p')
            status_class = 'success' if status == 'success' else 'failed'
            
            html += f"""
                <tr>
                    <td>{time}</td>
                    <td>{'Check In' if action_type == 'punch_in' else 'Check Out'}</td>
                    <td class="{status_class}">{status.title()}</td>
                    <td>{error_message if error_message else '-'}</td>
                </tr>
            """
        
        if current_date is not None:
            html += "</table>"
        
        html += """
            </div>
        </body>
        </html>
        """
        
        return html 