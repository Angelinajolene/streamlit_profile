import streamlit as st
from PIL import Image
import os

import PyPDF2
from docx import Document
import pandas as pd


st.set_page_config(
    page_title="Employee Dashboard",
    page_icon="💼",
    layout="wide"
)

st.markdown("""
<style>

.main {
    background-color: #f5f7fa;
}

.title {
    text-align: center;
    color: #1f3c88;
    font-size: 40px;
    font-weight: bold;
    margin-bottom: 20px;
}

.box {
    background-color: white;
    padding: 25px;
    border-radius: 15px;
    box-shadow: 0px 2px 12px rgba(0,0,0,0.1);
    margin-bottom: 20px;
}

.stButton > button {
    width: 100%;
    border-radius: 10px;
    height: 45px;
    font-size: 16px;
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)

USERNAME = "admin"
PASSWORD = "1234"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():

    st.markdown("<h1 class='title'>💼 Employee Login Portal</h1>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])

    with col2:

        st.markdown("<div class='box'>", unsafe_allow_html=True)

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):

            if username == USERNAME and password == PASSWORD:
                st.session_state.logged_in = True
                st.success("Login Successful")
                st.rerun()

            else:
                st.error("Invalid Username or Password")

        st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------
# PDF TEXT EXTRACTION
# -------------------------------------------------
def extract_pdf_text(file):

    pdf_reader = PyPDF2.PdfReader(file)

    text = ""

    for page in pdf_reader.pages:

        extracted = page.extract_text()

        if extracted:
            text += extracted

    return text

# -------------------------------------------------
# DOCX TEXT EXTRACTION
# -------------------------------------------------
def extract_docx_text(file):

    doc = Document(file)

    text = ""

    for para in doc.paragraphs:
        text += para.text + "\n"

    return text

# -------------------------------------------------
# DASHBOARD
# -------------------------------------------------
def employee_dashboard():

    # SIDEBAR
    st.sidebar.title("📌 Navigation")

    menu = st.sidebar.radio(
        "Select Option",
        ["Dashboard", "Employee Registration"]
    )

    st.sidebar.success("Logged in as Admin")

    # -------------------------------------------------
    # DASHBOARD PAGE
    # -------------------------------------------------
    if menu == "Dashboard":

        st.markdown("<h1 class='title'>📊 HR Employee Dashboard</h1>", unsafe_allow_html=True)

        # METRICS
        m1, m2, m3 = st.columns(3)

        m1.metric("Total Employees", "120")
        m2.metric("Departments", "8")
        m3.metric("Uploaded Resumes", "95")

        st.divider()

        # SAMPLE TABLE
        data = {
            "Employee ID": [101, 102, 103],
            "Name": ["John", "Emma", "David"],
            "Department": ["IT", "HR", "Finance"]
        }

        df = pd.DataFrame(data)

        st.subheader("Employee Records")

        st.dataframe(df, use_container_width=True)

        # LINE CHART
        chart_data = pd.DataFrame({
            "Months": ["Jan", "Feb", "Mar", "Apr", "May"],
            "Employees Joined": [5, 8, 6, 10, 7]
        })

        st.subheader("Employee Growth")

        st.line_chart(
            chart_data.set_index("Months")
        )

    # -------------------------------------------------
    # EMPLOYEE REGISTRATION PAGE
    # -------------------------------------------------
    elif menu == "Employee Registration":

        st.markdown("<h1 class='title'>📝 Employee Registration Form</h1>", unsafe_allow_html=True)

        col1, col2 = st.columns([1,2])

        # -------------------------------------------------
        # LEFT SIDE - PROFILE IMAGE
        # -------------------------------------------------
        with col1:

            st.markdown("<div class='box'>", unsafe_allow_html=True)

            st.subheader("Profile Picture")

            uploaded_image = st.file_uploader(
                "Upload JPG/JPEG Image",
                type=["jpg", "jpeg"]
            )

            if uploaded_image is not None:

                file_size = uploaded_image.size / (1024 * 1024)

                if file_size > 2:
                    st.error("Image size should be below 2 MB")

                else:
                    image = Image.open(uploaded_image)

                    st.image(
                        image,
                        caption="Profile Preview",
                        width=250
                    )

            st.markdown("</div>", unsafe_allow_html=True)

        # -------------------------------------------------
        # RIGHT SIDE - FORM
        # -------------------------------------------------
        with col2:

            st.markdown("<div class='box'>", unsafe_allow_html=True)

            st.subheader("Employee Details")

            first_name = st.text_input("First Name")
            last_name = st.text_input("Last Name")
            department = st.selectbox(
                "Department",
                ["IT", "HR", "Finance", "Marketing"]
            )

            email = st.text_input("Email")

            # -------------------------------------------------
            # RESUME UPLOAD
            # -------------------------------------------------
            st.subheader("Resume Upload")

            uploaded_resume = st.file_uploader(
                "Upload Resume",
                type=["pdf", "docx"]
            )

            extracted_text = ""

            if uploaded_resume is not None:

                # PDF
                if uploaded_resume.type == "application/pdf":

                    extracted_text = extract_pdf_text(
                        uploaded_resume
                    )

                # DOCX
                elif uploaded_resume.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":

                    extracted_text = extract_docx_text(
                        uploaded_resume
                    )

                st.text_area(
                    "Extracted Resume Text",
                    extracted_text,
                    height=250
                )

                # DOWNLOAD BUTTON
                st.download_button(
                    label="⬇ Download Resume Text",
                    data=extracted_text,
                    file_name="resume_text.txt",
                    mime="text/plain"
                )

            # -------------------------------------------------
            # SUBMIT BUTTON
            # -------------------------------------------------
            if st.button("Register Employee"):

                # VALIDATION
                if first_name == "" or last_name == "" or email == "":
                    st.error("Please fill all required fields")

                else:

                    # CREATE FOLDERS
                    if not os.path.exists("profile_pics"):
                        os.makedirs("profile_pics")

                    if not os.path.exists("resumes"):
                        os.makedirs("resumes")

                    # SAVE IMAGE
                    if uploaded_image is not None:

                        image_path = os.path.join(
                            "profile_pics",
                            uploaded_image.name
                        )

                        with open(image_path, "wb") as f:
                            f.write(uploaded_image.getbuffer())

                    # SAVE RESUME
                    if uploaded_resume is not None:

                        resume_path = os.path.join(
                            "resumes",
                            uploaded_resume.name
                        )

                        with open(resume_path, "wb") as f:
                            f.write(uploaded_resume.getbuffer())

                    st.success("Employee Registered Successfully")

                    st.write("### Employee Information")
                    st.write("First Name:", first_name)
                    st.write("Last Name:", last_name)
                    st.write("Department:", department)
                    st.write("Email:", email)

            st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------
# MAIN
# -------------------------------------------------
if st.session_state.logged_in:
    employee_dashboard()
else:
    login()