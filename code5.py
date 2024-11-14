import os
import shutil
from PyPDF2 import PdfReader

# Define main categories with an expanded list of associated keywords
categories = {
    "Programming": ["programming", "code", "developer", "python", "java", "c++", "javascript"],
    "AI": ["machine learning", "AI", "artificial intelligence", "deep learning", "data science"],
    "Math": ["algebra", "calculus", "statistics", "probability", "geometry"],
    "Database": ["database", "SQL", "NoSQL", "data storage", "big data"],
    "Security": ["cryptography", "security", "network security", "cybersecurity", "encryption"],
    "Others": []  # For files that don't fit into the above categories
}

# Initialize counters for analysis report
category_count = {category: 0 for category in categories.keys()}
total_files = 0
correctly_categorized = 0

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
        if reader.pages:
            first_page_text = reader.pages[0].extract_text() or ""
            return first_page_text.lower()
    except Exception as e:
        print(f"Error processing '{file_path}': {e}")
    return ""

# Function to categorize and move files based on content from the first page
def categorize_file(file_path, root_folder):
    global correctly_categorized
    content_text = extract_first_page_content(file_path)
    if content_text:
        for category, keywords in categories.items():
            if any(keyword in content_text for keyword in keywords):
                dest_folder = os.path.join(root_folder, category)
                shutil.move(file_path, dest_folder)
                category_count[category] += 1
                correctly_categorized += 1
                print(f"Moved '{file_path}' to '{dest_folder}'")
                return True

    # If no category matched, move to 'Others'
    others_folder = os.path.join(root_folder, "Others")
    shutil.move(file_path, others_folder)
    category_count["Others"] += 1
    print(f"Moved '{file_path}' to 'Others'")
    return False

# Main function to categorize PDFs in the root folder
def categorize_pdfs(root_folder):
    global total_files
    create_folder_structure(root_folder)
    for file in os.listdir(root_folder):
        if file.endswith(".pdf"):
            file_path = os.path.join(root_folder, file)
            if os.path.isfile(file_path):
                categorize_file(file_path, root_folder)
                total_files += 1

# Function to generate an analysis report
def generate_analysis_report():
    if total_files == 0:
        print("No files to analyze.")
        return
    
    print("\nAnalysis Report:")
    print("----------------")
    for category, count in category_count.items():
        percentage = (count / total_files) * 100
        print(f"{category}: {percentage:.2f}%")

    # Calculate correctness score as a percentage of correctly categorized files
    correctness_score = (correctly_categorized / total_files) * 100
    print(f"\nCorrectness Score: {correctness_score:.2f}%")

# Entry point of the script
root_folder = input("Enter the path to the root folder : ")
categorize_pdfs(root_folder)
generate_analysis_report()
