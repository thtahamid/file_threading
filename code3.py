import os
import shutil
from PyPDF2 import PdfReader

# Define main categories with an expanded list of associated keywords
categories = {
    "Programming": [
        "programming", "code", "software", "developer", "python", "java", "c++", "javascript", "software engineering"
    ],
    "AI": [
        "machine learning", "neural networks", "AI", "artificial intelligence", "deep learning", "data science",
        "reinforcement learning", "natural language processing", "computer vision"
    ],
    "Math": [
        "mathematics", "math", "algebra", "calculus", "statistics", "probability", "geometry", "discrete math"
    ],
    "Database": [
        "database", "SQL", "NoSQL", "data management", "data storage", "database design", "big data"
    ],
    "Security": [
        "cryptography", "security", "network security", "cybersecurity", "encryption", "malware", "phishing",
        "firewalls", "information security"
    ],
    "Others": []  # For files that don't fit any category
}

# Function to create the main category folders
def create_folder_structure(root_folder):
    for category in categories.keys():
        category_path = os.path.join(root_folder, category)
        os.makedirs(category_path, exist_ok=True)
    print("Main folder structure created successfully.")

# Function to extract the content from the first page of a PDF
def extract_first_page_content(file_path):
    try:
        reader = PdfReader(file_path)
        # Read the first page's text, or return an empty string if there's an issue
        if reader.pages:
            first_page_text = reader.pages[0].extract_text() or ""
            return first_page_text.lower()
    except Exception as e:
        print(f"Error processing '{file_path}': {e}")
    return ""

# Function to categorize and move files based on content from the first page
def categorize_file(file_path, root_folder):
    content_text = extract_first_page_content(file_path)
    if content_text:
        # Check if any category keyword appears in the first page text
        for category, keywords in categories.items():
            if any(keyword in content_text for keyword in keywords):
                dest_folder = os.path.join(root_folder, category)
                shutil.move(file_path, dest_folder)
                print(f"Moved '{file_path}' to '{dest_folder}'")
                return True

    # If no category matched, move to 'Others'
    others_folder = os.path.join(root_folder, "Others")
    shutil.move(file_path, others_folder)
    print(f"Moved '{file_path}' to 'Others'")
    return False

# Main function to categorize PDFs in the root folder
def categorize_pdfs(root_folder):
    create_folder_structure(root_folder)
    for file in os.listdir(root_folder):
        if file.endswith(".pdf"):
            file_path = os.path.join(root_folder, file)
            categorize_file(file_path, root_folder)

# Entry point of the script
root_folder = input("Enter the path to the root folder where your PDF files are stored: ")
categorize_pdfs(root_folder)
