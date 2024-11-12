import os
import shutil

# Define the main categories and subcategories
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
    # Check if the directory exists
    if not os.path.isdir(root_folder):
        print(f"Error: The path '{root_folder}' does not exist. Please provide a valid directory.")
        return get_root_folder()  # Prompt the user again if invalid
    return root_folder

# Function to create folder structure with error handling
def create_folder_structure(root_folder):
    try:
        for category, subcategories in categories.items():
            category_path = os.path.join(root_folder, category)
            os.makedirs(category_path, exist_ok=True)  # Create main category folder
            for subcategory in subcategories:
                subcategory_path = os.path.join(category_path, subcategory)
                os.makedirs(subcategory_path, exist_ok=True)  # Create subcategory folder
        others_folder = os.path.join(root_folder, "Others")
        os.makedirs(others_folder, exist_ok=True)  # Create "Others" folder
        print("Folder structure created successfully.")
    except PermissionError:
        print("Error: Permission denied while creating folders. Please check your permissions.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Function to categorize files with error handling
def categorize_files(root_folder):
    for file in os.listdir(root_folder):
        if file.endswith(".pdf"):
            file_path = os.path.join(root_folder, file)
            categorized = False

            # Try categorizing files into subfolders
            try:
                for category, subcategories in categories.items():
                    for subcategory in subcategories:
                        if subcategory.lower() in file.lower():
                            dest_folder = os.path.join(root_folder, category, subcategory)
                            if not os.path.exists(dest_folder):
                                os.makedirs(dest_folder, exist_ok=True)  # Create missing subfolder if needed
                            shutil.move(file_path, dest_folder)
                            print(f"Moved '{file}' to '{dest_folder}'")
                            categorized = True
                            break

                    if categorized:
                        break

                # If no category matched, move to 'Others' folder
                if not categorized:
                    others_folder = os.path.join(root_folder, "Others")
                    shutil.move(file_path, others_folder)
                    print(f"Moved '{file}' to 'Others'")

            except PermissionError:
                print(f"Error: Permission denied while moving '{file}'.")
            except FileNotFoundError:
                print(f"Error: File '{file}' not found. It may have been moved or deleted.")
            except Exception as e:
                print(f"An unexpected error occurred while processing '{file}': {e}")

# Main program
root_folder = get_root_folder()
create_folder_structure(root_folder)
categorize_files(root_folder)
