from hdbcli import dbapi
import os

# Connection parameters
connection_params = {
    'address': '***************************-us10.hanacloud.ondemand.com',           #### Adjust your Host name
    'port': 443,  # Default port, adjust as needed
    'user': '*************',      ### Replace your Username
    'password': '******************'       #### Replace your password
}

# Establish connection
try:
    conn = dbapi.connect(**connection_params)
    cursor = conn.cursor()
    print("Connection to the database established successfully.")
except dbapi.Error as e:
    print(f"Error connecting to the database: {e}")
    
'''    
create_table_sql = """
CREATE TABLE FILE_STORAGE (
    FILE_ID INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    FILE_NAME NVARCHAR(256),
    FILE_TYPE NVARCHAR(100),
    FILE_SIZE INTEGER,
    FILE_CONTENT BLOB,
    UPLOAD_DATE TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

cursor.execute(create_table_sql)
conn.commit()    
'''

###############################################################################
def store_file(file_path):
    try:
        # Get file information
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        file_type = os.path.splitext(file_name)[1]
        
        # Read file content
        with open(file_path, 'rb') as file:
            file_content = file.read()
        
        # Insert file into database
        insert_sql = """
        INSERT INTO FILE_STORAGE 
        (FILE_NAME, FILE_TYPE, FILE_SIZE, FILE_CONTENT)
        VALUES (?, ?, ?, ?)
        """
        
        cursor.execute(insert_sql, (file_name, file_type, file_size, file_content))
        conn.commit()

        # Retrieve the last inserted ID
        cursor.execute("SELECT CURRENT_IDENTITY_VALUE() FROM DUMMY")
        file_id = cursor.fetchone()[0]        
        print(file_id)
        return file_id
        
    except Exception as e:
        print(f"Error storing file: {str(e)}")
        conn.rollback()
        return None
    

# Store a file
file_path = "my_data.csv"                 #### Update your path
file_id = store_file(file_path)

if file_id:
    print(f"File stored successfully with ID: {file_id}")
###############################################################################

def retrieve_file(file_id, output_directory):
    try:
        # Query file data
        select_sql = """
        SELECT FILE_NAME, FILE_CONTENT 
        FROM FILE_STORAGE 
        WHERE FILE_ID = ?
        """
        
        cursor.execute(select_sql, (file_id,))
        result = cursor.fetchone()
        
        if result:
            file_name, file_content = result
            output_path = os.path.join(output_directory, file_name)
            
            # Write file to disk
            with open(output_path, 'wb') as file:
                file.write(file_content)
            
            return output_path
        else:
            print(f"No file found with ID: {file_id}")
            return None
            
    except Exception as e:
        print(f"Error retrieving file: {str(e)}")
        return None

# Retrieve a file
output_dir = "hana_cloud_output/"       #### Update your path
retrieved_file_path = retrieve_file(file_id, output_dir)

if retrieved_file_path:
    print(f"File retrieved successfully to: {retrieved_file_path}")        



###############################################################################
def list_stored_files():
    try:
        select_sql = """
        SELECT FILE_ID, FILE_NAME, FILE_TYPE, FILE_SIZE, UPLOAD_DATE 
        FROM FILE_STORAGE 
        ORDER BY UPLOAD_DATE DESC
        """
        
        cursor.execute(select_sql)
        files = cursor.fetchall()
        
        print("\nStored Files:")
        print("ID | Name | Type | Size (bytes) | Upload Date")
        print("-" * 60)
        
        for file in files:
            print(f"{file[0]} | {file[1]} | {file[2]} | {file[3]} | {file[4]}")
            
    except Exception as e:
        print(f"Error listing files: {str(e)}")
        
list_stored_files()


# Close database connections when done
def cleanup():
    cursor.close()
    conn.close()
