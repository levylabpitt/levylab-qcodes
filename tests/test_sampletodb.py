from task_id_to_db import parse_asana_url, upload_task_id_to_db
from levylabinst import LocalDB

# Initialize the database connection
db = LocalDB(user="postgres")

# Test a valid Asana URL
test_url = "https://app.asana.com/0/687756245553298/1207024918366445"

try:
    # Parse the URL to extract the task ID
    task_id = parse_asana_url(test_url)
    print(f"Parsed Task ID: {task_id}")

    # Upload the task ID to the database
    upload_task_id_to_db(task_id, db)
    print("Test completed successfully!")
except Exception as e:
    print(f"Test failed: {e}")
