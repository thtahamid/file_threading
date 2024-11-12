import os
import shutil
import re

# Define the main categories and subcategories with keywords for better matching
categories = {
    "Programming": ["Python", "Java", "C"],
    "AI": ["Machine_Learning", "Neural_Networks"],
    "Math": ["Linear_Algebra", "Calculus"],
    "Database": ["SQL", "NoSQL"],
    "Security": ["Cryptography", "Network_Security"],
    "Others": []
}

# Function to get the root folder path with error checking
def get_root_folder():
    root_folder = input("Enter the path to the root folder where your PDF files are stored: ")
    if not os.path.isdir(root_folder):
        print(f"Error: The path '{root_folder}' does not exist. Please provide a valid directory.")
        return get_root_folder()
    return root_folder

# Function to create folder structure
def create_folder_structure(root_folder):
    for category, subcategories in categories.items():
        category_path = os.path.join(root_folder, category)
        os.makedirs(category_path, exist_ok=True)
        for subcategory in subcategories:
            subcategory_path = os.path.join(category_path, subcategory)
            os.makedirs(subcategory_path, exist_ok=True)
    others_folder = os.path.join(root_folder, "Others")
    os.makedirs(others_folder, exist_ok=True)
    print("Folder structure created successfully.")

# Function to categorize files with improved accuracy
def categorize_files(root_folder):
    for file in os.listdir(root_folder):
        if file.endswith(".pdf"):
            file_path = os.path.join(root_folder, file)
            categorized = False

            # Normalize the file name: convert to lowercase and remove special characters
            file_name_normalized = re.sub(r'[^a-z0-9\s]', '', file.lower())  # Remove special chars
            file_name_words = file_name_normalized.split()

            # Try categorizing the file based on keywords
            for category, subcategories in categories.items():
                # First, check the subfolders of the category
                for subcategory in subcategories:
                    # Check if the subcategory is part of the file name (case insensitive)
                    if subcategory.lower() in file_name_normalized:
                        dest_folder = os.path.join(root_folder, category, subcategory)
                        if not os.path.exists(dest_folder):
                            os.makedirs(dest_folder, exist_ok=True)  # Ensure subfolder exists
                        shutil.move(file_path, dest_folder)
                        print(f"Moved '{file}' to '{dest_folder}'")
                        categorized = True
                        break

                if categorized:
                    break

            # If no category matched, move to 'Others'
            if not categorized:
                others_folder = os.path.join(root_folder, "Others")
                shutil.move(file_path, others_folder)
                print(f"Moved '{file}' to 'Others'")

# Main program
root_folder = get_root_folder()
create_folder_structure(root_folder)
categorize_files(root_folder)
