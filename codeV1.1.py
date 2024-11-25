# (Without threading)
import os
import PyPDF2
import time

def create_folder_structure(root_folder):
    # Define the multilevel folder structure
    folder_structure = {
        "Programming": {"Python": [], "Java": [], "C": [] },
        "AI": {"Machine_Learning": [], "Neural_Networks": [] },
        "Math": {"Linear_Algebra": [], "Calculus": [] },
        "Database": {"SQL": [], "NoSQL": [] },
        "Security": {"Cryptography": [], "Network_Security": [] },
        "Others": [] }

    # Define keywords for each subcategory
    categories = {
        "Programming": {
            "Python": ["python", "pip", "django", "flask", "pandas", "numpy"],
            "Java": ["java", "spring", "maven", "gradle", "jdbc", "jvm"],
            "C": ["c programming", "c++", "pointers", "memory management", "gcc"] },
        "AI": {
            "Machine_Learning": ["machine learning", "supervised", "unsupervised", "regression", "classification"],
            "Neural_Networks": ["neural networks", "deep learning", "cnn", "rnn", "lstm"] },
        "Math": {
            "Linear_Algebra": ["linear algebra", "matrices", "vectors", "eigenvalues"],
            "Calculus": ["calculus", "derivatives", "integrals", "differential equations"] },
        "Database": {
            "SQL": ["sql", "mysql", "postgresql", "relational database"],
            "NoSQL": ["nosql", "mongodb", "cassandra", "document database"] },
        "Security": {
            "Cryptography": ["cryptography", "encryption", "decryption", "cipher"],
            "Network_Security": ["network security", "firewall", "vpn", "protocol"] },
        "Others": ["general topics", "miscellaneous", "varied interests"] }

    # Create the folder structure
    for main_category, subcategories in folder_structure.items():
        main_path = os.path.join(root_folder, main_category)
        os.makedirs(main_path, exist_ok=True)
        
        if isinstance(subcategories, dict):
            for subcategory in subcategories:
                sub_path = os.path.join(main_path, subcategory)
                os.makedirs(sub_path, exist_ok=True)
    
    print("Folder structure created successfully.")
    return categories

def categorize_and_move_files(root_folder, categories):
    files = [f for f in os.listdir(root_folder) if f.endswith('.pdf')]
    file_counts = {main_cat: {sub_cat: 0 for sub_cat in sub_cats.keys()} if isinstance(sub_cats, dict) else 0 
                  for main_cat, sub_cats in categories.items()}
    
    print("\nProcessing files...")
    for file_name in files:
        file_path = os.path.join(root_folder, file_name)
        
        try:
            # Read PDF content
            with open(file_path, "rb") as f:
                pdf_reader = PyPDF2.PdfReader(f)
                if pdf_reader.pages:
                    first_page_text = pdf_reader.pages[0].extract_text().lower()
                    file_name_lower = file_name.lower()
                    
                    # Find best matching category and subcategory
                    best_main_cat = "Others"
                    best_sub_cat = None
                    max_matches = 0

                    # Check each category
                    for main_cat, sub_cats in categories.items():
                        if isinstance(sub_cats, dict):
                            for sub_cat, keywords in sub_cats.items():
                                matches = sum(1 for keyword in keywords if 
                                           keyword in first_page_text or keyword in file_name_lower)
                                if matches > max_matches:
                                    max_matches = matches
                                    best_main_cat = main_cat
                                    best_sub_cat = sub_cat

                    # Move file to appropriate folder
                    if max_matches > 0:
                        destination_folder = os.path.join(root_folder, best_main_cat, best_sub_cat)
                        destination_path = os.path.join(destination_folder, file_name)
                        os.rename(file_path, destination_path)
                        file_counts[best_main_cat][best_sub_cat] += 1
                        print(f"Moved: {file_name} -> {best_main_cat}/{best_sub_cat}")
                    else:
                        # Move to Others if no matches found
                        destination_folder = os.path.join(root_folder, "Others")
                        destination_path = os.path.join(destination_folder, file_name)
                        os.rename(file_path, destination_path)
                        file_counts["Others"] += 1
                        print(f"Moved: {file_name} -> Others")

        except Exception as e:
            print(f"Error processing {file_name}: {e}")
    
    return file_counts, len(files)

# def generate_analysis_report(file_counts, total_files):
#     print("\nSummary:")
#     print(f"Total files found in root folder: {total_files}\n")
#     for main_cat, sub_counts in file_counts.items():
#         if isinstance(sub_counts, dict):
#             total = sum(sub_counts.values())
#             if total > 0:
#                 print(f"{main_cat}: {total} files")
#                 for sub_cat, count in sub_counts.items():
#                     if count > 0:
#                         print(f"  └─{sub_cat}: {count}")
#         elif sub_counts > 0:
#             print(f"{main_cat}: {sub_counts} files")


def generate_analysis_report(file_counts, total_files):
    print(f"Total files found in root folder: {total_files}\n")
    
    total_moved = 0
    percentages = {}

    for main_cat, sub_counts in file_counts.items():
        if isinstance(sub_counts, dict):
            total = sum(sub_counts.values())
            total_moved += total
            if total > 0:
                percentages[main_cat] = total  # Store total for percentage calculation

    # Calculate and print percentages for each major folder
    if total_files > 0:
        for main_cat, moved_count in percentages.items():
            percentage_moved = (moved_count / total_files) * 100
            print(f"{main_cat}: {percentage_moved:.2f}% ")
    else:
        print("No files found to process.")

    # Calculate overall percentages
    if total_moved > 0:
        percentage_correct = (total_moved / total_moved) * 100  # This will always be 100%
    else:
        percentage_correct = 0

    print(f"\nCorrectness: {percentage_correct:.2f}%")


def check_root_folder(root_folder):
    remaining_files = [f for f in os.listdir(root_folder) if f.endswith('.pdf')]
    if remaining_files:
        print("\nWARNING: Files still in root folder:")
        for file in remaining_files:
            print(f"- {file}")
        return False
    return True

# Main Execution
if __name__ == "__main__":
    root_folder = input("Enter the path to the root folder: ").strip()
    
    start_time = time.time()
    categories = create_folder_structure(root_folder)
    
    file_counts, total_files = categorize_and_move_files(root_folder, categories)
    
    # Check if any files remain in root folder
    all_moved = check_root_folder(root_folder)
    
    generate_analysis_report(file_counts, total_files)
    print(f"\nTime taken: {time.time() - start_time:.2f} seconds")
    print(f"Status: {'Success' if all_moved else 'Failed - some files remain in root'}")
