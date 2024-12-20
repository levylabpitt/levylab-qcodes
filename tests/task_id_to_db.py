import os
from urllib.parse import urlparse
from datetime import datetime
from levylabinst import LocalDB

db = LocalDB(user="postgres")

def parse_asana_url(url):
    """
    Parse the Asana task URL to extract the project ID and task ID.
    Example URL: https://app.asana.com/0/project_id/task_id
    """
    try:
        path_parts = urlparse(url).path.split('/')
        task_id = path_parts[3]
        return task_id
    except (IndexError, ValueError):
        raise ValueError("Invalid Asana URL format.")

# Send data to database
def upload_task_id_to_db(task_id, db):
    test_datetime = datetime.now()

    # Example insert query
    sql_insert_string = """
        INSERT INTO sample_taskid (datetime, task_id)
        VALUES (%s, %s)
    """
    try:
        db.cursor.execute(sql_insert_string, (test_datetime, task_id))
        db.conn.commit()
        print(f"Task ID {task_id} inserted successfully!")
    except Exception as e:
        db.conn.rollback()
        print(f"Failed to insert task ID {task_id}. Error: {e}")

def main():
    """
    Main function to input Asana task URL and save task ID to the database.
    """
    print("\nEnter the Asana task URL:")
    task_url = input().strip()

    try:
        task_id = parse_asana_url(task_url)
        print(f"Parsed Task ID: {task_id}")
        upload_task_id_to_db(task_id, db)
    except ValueError as ve:
        print(f"Error: {ve}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()

