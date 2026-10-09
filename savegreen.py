
import streamlit as st
import sqlite3
import pandas as pd

# -------------------------------
# PAGE CONFIGURATION
# -------------------------------
st.set_page_config(
    page_title="Savegreen",
    page_icon="🌱",
    layout="wide"
)

# -------------------------------
# DATABASE CONNECTION
# -------------------------------
conn = sqlite3.connect("savegreen.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT,
    budget REAL,
    status TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    role TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS csr_partners (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company TEXT NOT NULL,
    email TEXT,
    contribution REAL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS donations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    donor TEXT NOT NULL,
    amount REAL,
    project TEXT
)
""")

conn.commit()

# -------------------------------
# SIDEBAR NAVIGATION
# -------------------------------
st.sidebar.title("🌱 Savegreen")
st.sidebar.caption("NGO & CSR Management")

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

pages = [
    "Dashboard",
    "Projects",
    "Users",
    "CSR Partners",
    "Donations"
]

for item in pages:
    if st.sidebar.button(item, use_container_width=True):
        st.session_state.page = item

page = st.session_state.page

# -------------------------------
# DASHBOARD
# -------------------------------
if page == "Dashboard":

    st.title("🌱 Savegreen Dashboard")
    st.write("Manage environmental projects, donors and CSR activities.")

    total_projects = cursor.execute(
        "SELECT COUNT(*) FROM projects"
    ).fetchone()[0]

    total_users = cursor.execute(
        "SELECT COUNT(*) FROM users"
    ).fetchone()[0]

    total_partners = cursor.execute(
        "SELECT COUNT(*) FROM csr_partners"
    ).fetchone()[0]

    total_donations = cursor.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM donations"
    ).fetchone()[0]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Projects", total_projects)
    col2.metric("Registered Users", total_users)
    col3.metric("CSR Partners", total_partners)
    col4.metric("Total Donations", f"₹{total_donations:,.2f}")

    st.subheader("Recent Projects")

    df = pd.read_sql_query(
        "SELECT * FROM projects ORDER BY id DESC",
        conn
    )

    st.dataframe(df, use_container_width=True)

    st.subheader("Donation Summary")

    donation_df = pd.read_sql_query(
        """SELECT project, SUM(amount) AS total
        FROM donations GROUP BY project""",
        conn
    )

    if not donation_df.empty:
        st.bar_chart(
            donation_df,
            x="project",
            y="total"
        )
    else:
        st.info("No donations recorded yet.")

# -------------------------------
# PROJECT MANAGEMENT
# -------------------------------
elif page == "Projects":

    st.title("🌳 Project Management")

    with st.form("project_form", clear_on_submit=True):

        name = st.text_input("Project Name")

        category = st.selectbox(
            "Project Category",
            [
                "Tree Plantation",
                "Waste Management",
                "Water Conservation",
                "Community Welfare",
                "Other"
            ]
        )

        budget = st.number_input(
            "Project Budget (₹)",
            min_value=0.0,
            step=1000.0
        )

        status = st.selectbox(
            "Project Status",
            ["Planned", "In Progress", "Completed"]
        )

        submitted = st.form_submit_button("Save Project")

        if submitted:
            if name.strip():
                cursor.execute(
                    """INSERT INTO projects
                    (name, category, budget, status)
                    VALUES (?, ?, ?, ?)""",
                    (name.strip(), category, budget, status)
                )
                conn.commit()
                st.success("Project saved successfully!")
            else:
                st.warning("Please enter a project name.")

    st.subheader("All Projects")

    df = pd.read_sql_query(
        "SELECT * FROM projects ORDER BY id DESC",
        conn
    )

    st.dataframe(df, use_container_width=True)

# -------------------------------
# USER MANAGEMENT
# -------------------------------
elif page == "Users":

    st.title("👥 User Registration")

    with st.form("user_form", clear_on_submit=True):

        name = st.text_input("Full Name")
        email = st.text_input("Email Address")

        role = st.selectbox(
            "User Role",
            ["Volunteer", "Donor", "NGO Admin", "CSR Representative"]
        )

        submitted = st.form_submit_button("Register User")

        if submitted:
            if name.strip() and email.strip():
                cursor.execute(
                    """INSERT INTO users (name, email, role)
                    VALUES (?, ?, ?)""",
                    (name.strip(), email.strip(), role)
                )
                conn.commit()
                st.success("User registered successfully!")
            else:
                st.warning("Please enter the name and email.")

    st.subheader("Registered Users")

    df = pd.read_sql_query(
        "SELECT * FROM users ORDER BY id DESC",
        conn
    )

    st.dataframe(df, use_container_width=True)

# -------------------------------
# CSR PARTNERS
# -------------------------------
elif page == "CSR Partners":

    st.title("🏢 CSR Partner Management")

    with st.form("csr_form", clear_on_submit=True):

        company = st.text_input("Company Name")
        email = st.text_input("Contact Email")

        contribution = st.number_input(
            "Contribution Amount (₹)",
            min_value=0.0,
            step=1000.0
        )

        submitted = st.form_submit_button("Save CSR Partner")

        if submitted:
            if company.strip() and email.strip():
                cursor.execute(
                    """INSERT INTO csr_partners
                    (company, email, contribution)
                    VALUES (?, ?, ?)""",
                    (company.strip(), email.strip(), contribution)
                )
                conn.commit()
                st.success("CSR partner saved successfully!")
            else:
                st.warning("Enter the company name and email.")

    st.subheader("Registered CSR Partners")

    df = pd.read_sql_query(
        "SELECT * FROM csr_partners ORDER BY id DESC",
        conn
    )

    st.dataframe(df, use_container_width=True)

# -------------------------------
# DONATION MANAGEMENT
# -------------------------------
elif page == "Donations":

    st.title("💚 Donation Management")

    projects = [
        row[0]
        for row in cursor.execute(
            "SELECT name FROM projects ORDER BY name"
        ).fetchall()
    ]

    with st.form("donation_form", clear_on_submit=True):

        donor = st.text_input("Donor Name")

        amount = st.number_input(
            "Donation Amount (₹)",
            min_value=0.0,
            step=100.0
        )

        if projects:
            project = st.selectbox("Select Project", projects)
        else:
            project = None
            st.info("Please create a project first.")

        submitted = st.form_submit_button("Record Donation")

        if submitted:
            if not donor.strip():
                st.warning("Please enter the donor name.")
            elif not projects:
                st.warning("Create a project before recording a donation.")
            elif amount <= 0:
                st.warning("Donation must be greater than zero.")
            else:
                cursor.execute(
                    """INSERT INTO donations
                    (donor, amount, project)
                    VALUES (?, ?, ?)""",
                    (donor.strip(), amount, project)
                )
                conn.commit()
                st.success("Donation recorded successfully!")

    st.subheader("Donation History")

    df = pd.read_sql_query(
        "SELECT * FROM donations ORDER BY id DESC",
        conn
    )

    st.dataframe(df, use_container_width=True)

conn.close()
