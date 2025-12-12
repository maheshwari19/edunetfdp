import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# =====================================================
# DATABASE CONFIGURATION
# =====================================================

# Database file name
DATABASE = "data.db"

# Initialize database connection and create table if it doesn't exist
def init_database():
    """
    Create a connection to the SQLite database and initialize the table.
    If the table doesn't exist, it will be created with the following schema:
    - id: Primary key (auto-increment)
    - name: Text field
    - email: Text field
    - phone: Text field
    - created_at: Timestamp
    """
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Create table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            age INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

# =====================================================
# CRUD OPERATIONS
# =====================================================

def get_connection():
    """Get a database connection."""
    return sqlite3.connect(DATABASE)

def insert_record(name, email, phone, age):
    """
    INSERT operation: Add a new record to the database.
    
    Args:
        name (str): User's name
        email (str): User's email
        phone (str): User's phone number
        age (int): User's age
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (name, email, phone, age)
            VALUES (?, ?, ?, ?)
        """, (name, email, phone, age))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error inserting record: {e}")
        return False

def view_all_records():
    """
    READ operation: Fetch all records from the database.
    
    Returns:
        pd.DataFrame: DataFrame containing all records
    """
    try:
        conn = get_connection()
        query = "SELECT id, name, email, phone, age, created_at FROM users ORDER BY id DESC"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error reading records: {e}")
        return pd.DataFrame()

def view_record_by_id(record_id):
    """
    Fetch a single record by ID.
    
    Args:
        record_id (int): The ID of the record to fetch
    
    Returns:
        tuple: Record data (name, email, phone, age) or None
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name, email, phone, age FROM users WHERE id = ?
        """, (record_id,))
        record = cursor.fetchone()
        conn.close()
        return record
    except Exception as e:
        st.error(f"Error fetching record: {e}")
        return None

def update_record(record_id, name, email, phone, age):
    """
    UPDATE operation: Update an existing record.
    
    Args:
        record_id (int): The ID of the record to update
        name (str): Updated name
        email (str): Updated email
        phone (str): Updated phone
        age (int): Updated age
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users SET name = ?, email = ?, phone = ?, age = ?
            WHERE id = ?
        """, (name, email, phone, age, record_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error updating record: {e}")
        return False

def delete_record(record_id):
    """
    DELETE operation: Remove a record from the database.
    
    Args:
        record_id (int): The ID of the record to delete
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (record_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error deleting record: {e}")
        return False

# =====================================================
# STREAMLIT UI
# =====================================================

# Initialize database on app startup
init_database()

# Set page configuration
st.set_page_config(
    page_title="SQLite CRUD App",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title
st.title("📊 SQLite Database CRUD Application")
st.markdown("A clean and simple interface to manage user records with full CRUD operations.")

# Sidebar navigation
st.sidebar.header("Navigation")
operation = st.sidebar.radio(
    "Choose an operation:",
    ["📖 View Records", "➕ Add Record", "✏️ Update Record", "🗑️ Delete Record"]
)

# =====================================================
# OPERATION: VIEW RECORDS
# =====================================================
if operation == "📖 View Records":
    st.header("📖 View All Records")
    st.markdown("---")
    
    df = view_all_records()
    
    if df.empty:
        st.info("No records found. Start by adding a new record!")
    else:
        st.subheader(f"Total Records: {len(df)}")
        # Display records in a dataframe
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "id": st.column_config.NumberColumn("ID", width="small"),
                "name": st.column_config.TextColumn("Name", width="medium"),
                "email": st.column_config.TextColumn("Email", width="large"),
                "phone": st.column_config.TextColumn("Phone", width="medium"),
                "created_at": st.column_config.TextColumn("Created At", width="medium")
            }
        )
        
        # Option to export data
        st.markdown("---")
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name=f"users_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

# =====================================================
# OPERATION: ADD RECORD
# =====================================================
elif operation == "➕ Add Record":
    st.header("➕ Add a New Record")
    st.markdown("---")
    
    # Create a form for adding a new record
    with st.form(key="add_form", clear_on_submit=True):
        st.subheader("Enter New User Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input(
                "Full Name",
                placeholder="e.g., John Doe",
                help="Enter the user's full name"
            )
        
        with col2:
            age = st.number_input(
                "Age",
                min_value=1,
                max_value=120,
                value=25,
                help="Enter the user's age"
            )
        
        email = st.text_input(
            "Email Address",
            placeholder="e.g., john@example.com",
            help="Enter a valid email address"
        )
        
        phone = st.text_input(
            "Phone Number",
            placeholder="e.g., +91 XXXXXXXXXX",
            help="Enter the phone number"
        )
        
        # Submit button
        submit_button = st.form_submit_button(
            label="➕ Add Record",
            use_container_width=True,
            type="primary"
        )
        
        # Handle form submission
        if submit_button:
            # Validation
            if not name.strip():
                st.error("❌ Name cannot be empty!")
            elif not email.strip():
                st.error("❌ Email cannot be empty!")
            elif not phone.strip():
                st.error("❌ Phone cannot be empty!")
            elif "@" not in email:
                st.error("❌ Please enter a valid email address!")
            elif age < 1:
                st.error("❌ Age must be at least 1!")
            else:
                # Insert record
                if insert_record(name, email, phone, age):
                    st.success(f"✅ Record added successfully! Name: {name}, Age: {age}")
                else:
                    st.error("❌ Failed to add record.")

# =====================================================
# OPERATION: UPDATE RECORD
# =====================================================
elif operation == "✏️ Update Record":
    st.header("✏️ Update an Existing Record")
    st.markdown("---")
    
    df = view_all_records()
    
    if df.empty:
        st.info("No records available to update.")
    else:
        # Let user select which record to update
        selected_id = st.selectbox(
            "Select a record to update:",
            options=df["id"].tolist(),
            format_func=lambda x: f"ID: {x} - {df[df['id'] == x]['name'].values[0]} ({df[df['id'] == x]['email'].values[0]})"
        )
        
        st.markdown("---")
        
        # Fetch the selected record
        record = view_record_by_id(selected_id)
        
        if record:
            name, email, phone, age = record
            
            st.subheader(f"Updating Record ID: {selected_id}")
            
            # Create a form for updating the record
            with st.form(key="update_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    updated_name = st.text_input(
                        "Full Name",
                        value=name,
                        help="Edit the user's full name"
                    )
                
                with col2:
                    updated_age = st.number_input(
                        "Age",
                        min_value=1,
                        max_value=120,
                        value=age if age else 25,
                        help="Edit the user's age"
                    )
                
                updated_email = st.text_input(
                    "Email Address",
                    value=email,
                    help="Edit the email address"
                )
                
                updated_phone = st.text_input(
                    "Phone Number",
                    value=phone,
                    help="Edit the phone number"
                )
                
                # Submit button
                update_button = st.form_submit_button(
                    label="✏️ Update Record",
                    use_container_width=True,
                    type="primary"
                )
                
                # Handle update submission
                if update_button:
                    # Validation
                    if not updated_name.strip():
                        st.error("❌ Name cannot be empty!")
                    elif not updated_email.strip():
                        st.error("❌ Email cannot be empty!")
                    elif not updated_phone.strip():
                        st.error("❌ Phone cannot be empty!")
                    elif "@" not in updated_email:
                        st.error("❌ Please enter a valid email address!")
                    elif updated_age < 1:
                        st.error("❌ Age must be at least 1!")
                    else:
                        # Update record
                        if update_record(selected_id, updated_name, updated_email, updated_phone, updated_age):
                            st.success(f"✅ Record updated successfully!")
                        else:
                            st.error("❌ Failed to update record.")

# =====================================================
# OPERATION: DELETE RECORD
# =====================================================
elif operation == "🗑️ Delete Record":
    st.header("🗑️ Delete a Record")
    st.markdown("---")
    
    df = view_all_records()
    
    if df.empty:
        st.info("No records available to delete.")
    else:
        # Let user select which record to delete
        selected_id = st.selectbox(
            "Select a record to delete:",
            options=df["id"].tolist(),
            format_func=lambda x: f"ID: {x} - {df[df['id'] == x]['name'].values[0]} ({df[df['id'] == x]['email'].values[0]})"
        )
        
        st.markdown("---")
        
        # Show record details before deleting
        record = view_record_by_id(selected_id)
        
        if record:
            name, email, phone, age = record
            
            st.warning(f"⚠️ You are about to delete the following record:")
            st.info(f"""
            **ID:** {selected_id}  
            **Name:** {name}  
            **Age:** {age}  
            **Email:** {email}  
            **Phone:** {phone}
            """)
            
            # Delete confirmation button
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button(
                    label="🗑️ Delete Record",
                    use_container_width=True,
                    type="primary"
                ):
                    if delete_record(selected_id):
                        st.success(f"✅ Record deleted successfully! ID: {selected_id}")
                        st.rerun()
                    else:
                        st.error("❌ Failed to delete record.")
            
            with col2:
                st.button("❌ Cancel", use_container_width=True)

# =====================================================
# FOOTER
# =====================================================
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #888; font-size: 0.9em;'>
    📊 SQLite CRUD Application | Built with Streamlit and SQLite3<br>
    © 2025 | Simple Database Management
    </div>
    """,
    unsafe_allow_html=True
)
