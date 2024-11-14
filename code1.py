import os
import shutil
from PyPDF2 import PdfReader

# Define main categories and associated keywords
categories = {
    "Programming": ["programming", "code", "software", "developer"],
    "AI": ["machine learning", "neural networks", "AI", "artificial intelligence", "deep learning"],
    "Math": ["mathematics", "math", "algebra", "calculus", "statistics"],
    "Database": ["database", "SQL", "NoSQL", "data management"],
    "Security": ["cryptography", "security", "network security", "cybersecurity", "encryption"],
    "Others": []  # For uncategorized files
}

# Function to create the main category folders
def create_folder_structure(root_folder):
    for category in categories.keys():
        category_path = os.path.join(root_folder, category)
        os.makedirs(category_path, exist_ok=True)
    print("Main folder structure created successfully.")

# Function to extract metadata and use it for categorization
def extract_metadata(file_path):
    try:
        reader = PdfReader(file_path)
        metadata = reader.metadata
        # Combine title, author, and subject into one string, if available
        metadata_text = f"{metadata.title or ''} {metadata.author or ''} {metadata.subject or ''}"
        return metadata_text.lower() if metadata_text else ""
    except Exception as e:
        print(f"Error reading metadata from '{file_path}': {e}")
        return ""

# Function to categorize and move files based on metadata
def categorize_file(file_path, root_folder):
    # Get metadata for categorization
    metadata_text = extract_metadata(file_path)
    if metadata_text:
        # Check if any category keyword appears in the metadata text
        for category, keywords in categories.items():
            if any(keyword in metadata_text for keyword in keywords):
                dest_folder = os.path.join(root_folder, category)
                shutil.move(file_path, dest_folder)
                print(f"Moved '{file_path}' to '{dest_folder}'")
                return True

    # If no category matched, move to 'Others'
    others_folder = os.path.join(root_folder, "Others")
    shutil.move(file_path, others_folder)
    print(f"Moved '{file_path}' to 'Others'")
    return False

# Main function to organize PDFs in the root folder
def categorize_pdfs_by_metadata(root_folder):
    create_folder_structure(root_folder)
    for file in os.listdir(root_folder):
        if file.endswith(".pdf"):
            file_path = os.path.join(root_folder, file)
            categorize_file(file_path, root_folder)

# Entry point of the script
root_folder = input("Enter the path: ")
categorize_pdfs_by_metadata(root_folder)
