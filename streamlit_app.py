import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURATION ---
DB_FILE = "master_database.csv"

USERS = {
    "Admin": {"pass": "admin123", "role": "admin", "school": "ALL"},
    "User 1": {"pass": "p1", "role": "user", "school": "School_A"},
    "User 2": {"pass": "p2", "role": "user", "school": "School_B"},
    "User 3": {"pass": "p3", "role": "user", "school": "School_C"},
    "User 4": {"pass": "p4", "role": "user", "school": "School_D"},
    "User 5": {"pass": "p5", "role": "user", "school": "School_E"},
    "User 6": {"pass": "p6", "role": "user", "school": "School_F"},
    "User 7": {"pass": "p7", "role": "user", "school": "School_G"},
    "User 8": {"pass": "p8", "role": "user", "school": "School_H"},
}

# --- DATABASE FUNCTIONS ---
def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=['UAN', 'Name', 'School', 'Basic', 'Status'])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

# --- UI SETUP ---
st.set_page_config(page_title="EPF Portal", layout="centered")
st.title("🛡️ EPF Multi-User Secure Portal")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- LOGIN SECTION ---
if not st.session_state.logged_in:
    with st.form("Login"):
        user_choice = st.selectbox("Apna Naam Chunein", list(USERS.keys()))
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if USERS[user_choice]['pass'] == password:
                st.session_state.logged_in = True
                st.session_state.user = user_choice
                st.session_state.role = USERS[user_choice]['role']
                st.session_state.school = USERS[user_choice]['school']
                st.rerun()
            else:
                st.error("Galat Password!")
else:
    # --- LOGGED IN AREA ---
    df = load_data()
    user_name = st.session_state.user
    st.sidebar.success(f"Logged in: {user_name}")
    
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    tab1, tab2 = st.tabs(["Data Entry", "Master View"])

    with tab1:
        st.subheader("Employee Data Management")
        uan = st.text_input("UAN Number")
        
        if uan:
            # Search record
            existing_rec = df[df['UAN'].astype(str) == uan]
            
            if not existing_rec.empty:
                emp_data = existing_rec.iloc[0]
                
                # Check Lock Status
                if emp_data['Status'] == 'Locked' and st.session_state.role != 'admin':
                    st.warning("⚠️ Yeh record LOCKED hai. Badlav ke liye Admin se sampark karein.")
                else:
                    with st.form("Edit Form"):
                        name = st.text_input("Name", value=emp_data['Name'])
                        school = st.text_input("School Name", value=emp_data['School'])
                        basic = st.number_input("Basic Salary", value=float(emp_data['Basic']))
                        save = st.form_submit_button("Update Record")
                        
                        if save:
                            df.loc[df['UAN'].astype(str) == uan, ['Name', 'School', 'Basic']] = [name, school, basic]
                            save_data(df)
                            st.success("Data Update ho gaya!")
            else:
                with st.form("New Entry"):
                    st.info("Naya Employee Mila!")
                    name = st.text_input("Name")
                    school = st.text_input("School Name", value=st.session_state.school if st.session_state.role != 'admin' else "")
                    basic = st.number_input("Basic Salary", min_value=0.0)
                    add = st.form_submit_button("Save New Entry")
                    
                    if add:
                        new_row = {'UAN': uan, 'Name': name, 'School': school, 'Basic': basic, 'Status': 'Unlocked'}
                        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                        save_data(df)
                        st.success("Naya Data Save ho gaya!")

    with tab2:
        st.subheader("Master Database")
        if st.session_state.role == 'admin':
            st.dataframe(df)
            if st.button("🔒 Sabhi Records Lock Karein"):
                df['Status'] = 'Locked'
                save_data(df)
                st.rerun()
        else:
            # User sirf apne school ka data dekh payega
            user_school_data = df[df['School'] == st.session_state.school]
            st.dataframe(user_school_data)
