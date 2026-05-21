import streamlit as st
from PIL import Image
import os
import cv2
import numpy as np
import pdfplumber
from docx import Document
import pandas as pd
import io

# Pure Python library to read embedded images without needing Poppler
from pypdf import PdfReader 

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
# PURE PYTHON TEXT EXTRACTION (No Poppler Required)
# -------------------------------------------------
@st.cache_data
def extract_pdf_text(uploaded_file):
    try:
        text = ""
        file_bytes = uploaded_file.read()
        
        # Method 1: Try reading native digital text layout
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
                    
        # Method 2: If digital text extraction is empty, try raw image extraction fallback
        if text.strip() == "":
            with st.spinner("Scanned document detected. Extracting text records..."):
                reader = PdfReader(io.BytesIO(file_bytes))
                for page in reader.pages:
                    # Look through embedded images on the scanned page
                    for image_file_object in page.images:
                        # Extract raw image bytes directly from the PDF object structure
                        image_bytes = image_file_object.data
                        text += f"[Extracted Image Attachment: {image_file_object.name}]\n"
                        # Note: To fully read text INSIDE this image without Poppler, 
                        # you can process image_bytes using lightweight cloud APIs or web models.
                        
        return text
    except Exception as e:
        return f"Error reading PDF: {e}"

@st.cache_data
def extract_docx_text(uploaded_file):
    try:
        doc = Document(uploaded_file)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    except Exception as e:
        return f"Error reading DOCX: {e}"

# -------------------------------------------------
# FACE VALIDATION
# -------------------------------------------------
def validate_face(image):
    img_array = np.array(image.convert("RGB"))
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    return len(faces) > 0

# -------------------------------------------------
# DASHBOARD
# -------------------------------------------------
def employee_dashboard():
    st.sidebar.title("📌 Navigation")
    menu = st.sidebar.radio("Select Option", ["Dashboard", "Employee Registration"])
    st.sidebar.success("Logged in as Admin")

    if menu == "Dashboard":
        st.markdown("<h1 class='title'>📊 HR Employee Dashboard</h1>", unsafe_allow_html=True)
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Employees", "120")
        m2.metric("Departments", "8")
        m3.metric("Uploaded Resumes", "95")
        st.divider()

        data = {
            "Employee ID": [101, 102, 103],
            "Name": ["John", "Emma", "David"],
            "Department": ["IT", "HR", "Finance"]
        }
        df = pd.DataFrame(data)
        st.subheader("Employee Records")
        st.dataframe(df, use_container_width=True)

        chart_data = pd.DataFrame({
            "Months": ["Jan", "Feb", "Mar", "Apr", "May"],
            "Employees Joined": [5, 8, 6, 10, 7]
        })
        st.subheader("Employee Growth")
        st.line_chart(chart_data.set_index("Months"))

    elif menu == "Employee Registration":
        st.markdown("<h1 class='title'>📝 Employee Registration Form</h1>", unsafe_allow_html=True)
        col1, col2 = st.columns([1,2])

        with col1:
            st.markdown("<div class='box'>", unsafe_allow_html=True)
            st.subheader("Profile Picture")
            uploaded_image = st.file_uploader("Upload JPG/PNG Image", type=["jpg", "jpeg", "png"])
            if uploaded_image is not None:
                file_size = uploaded_image.size / (1024 * 1024)
                if file_size > 1:
                    st.error("Image size should be below 1 MB")
                else:
                    image = Image.open(uploaded_image)
                    if not validate_face(image):
                        st.error("Invalid Photo: No face detected")
                    else:
                        st.image(image, caption="Profile Preview", width=250)
            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            st.markdown("<div class='box'>", unsafe_allow_html=True)
            st.subheader("Employee Details")
            first_name = st.text_input("First Name")
            last_name = st.text_input("Last Name")
            department = st.selectbox("Department", ["IT", "HR", "Finance", "Marketing"])
            email = st.text_input("Email")

            st.subheader("Resume Upload")
            uploaded_resume = st.file_uploader("Upload Resume", type=["pdf", "docx"], accept_multiple_files=False)
            
            extracted_text = ""
            
            if uploaded_resume is not None:
                if uploaded_resume.type == "application/pdf":
                    extracted_text = extract_pdf_text(uploaded_resume)
                elif uploaded_resume.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                    extracted_text = extract_docx_text(uploaded_resume)
                
                if extracted_text.strip() == "":
                    st.warning("No text could be extracted from this file. The document appears to be fully unreadable.")
                else:
                    st.text_area("Extracted Resume Text", extracted_text, height=250)
                    st.download_button(label="⬇ Download Resume Text", data=extracted_text, file_name="resume_text.txt", mime="text/plain")

            if st.button("Register Employee"):
                if first_name == "" or last_name == "" or email == "":
                    st.error("Please fill all required fields")
                else:
                    if not os.path.exists("profile_pics"):
                        os.makedirs("profile_pics")
                    if not os.path.exists("resumes"):
                        os.makedirs("resumes")
                    if uploaded_image is not None:
                        image_path = os.path.join("profile_pics", uploaded_image.name)
                        with open(image_path, "wb") as f:
                            f.write(uploaded_image.getbuffer())
                    if uploaded_resume is not None:
                        uploaded_resume.seek(0)
                        resume_path = os.path.join("resumes", uploaded_resume.name)
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
# MAIN RUNNER
# -------------------------------------------------
if st.session_state.logged_in:
    employee_dashboard()
else:
    login()