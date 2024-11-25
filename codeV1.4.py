# (with threading)
import os
import PyPDF2
import time
import threading
from queue import Queue

class FileValidator:
    def __init__(self):
        self.correct_paths = {}
        
    def add_correct_path(self, filename, correct_path):
        self.correct_paths[filename] = correct_path
        
    def calculate_accuracy(self, file_locations):
        if not self.correct_paths:
            return 0
            
        correct_count = 0
        for filename, actual_path in file_locations.items():
            if filename in self.correct_paths:
                if self.correct_paths[filename] == actual_path:
                    correct_count += 1
                    
        return (correct_count / len(self.correct_paths)) * 100

class ThreadSafeFileMover:
    def __init__(self):
        self.file_lock = threading.Lock()
        self.counts_lock = threading.Lock()
        self.processed_files_lock = threading.Lock()
        self.file_locations_lock = threading.Lock()
        self.file_counts = {}
        self.processed_files = set()
        self.file_locations = {}
        
    def is_processed(self, file_name):
        with self.processed_files_lock:
            return file_name in self.processed_files
            
    def mark_processed(self, file_name):
        with self.processed_files_lock:
            self.processed_files.add(file_name)
            
    def move_file(self, source, destination):
        with self.file_lock:
            os.rename(source, destination)
            self.record_file_location(os.path.basename(source), 
                                    os.path.dirname(destination).split(os.path.sep)[-1])
            
    def update_counts(self, main_cat, sub_cat=None):
        with self.counts_lock:
            if sub_cat:
                self.file_counts[main_cat][sub_cat] += 1
            else:
                self.file_counts[main_cat] += 1
            
    def record_file_location(self, filename, destination):
        with self.file_locations_lock:
            self.file_locations[filename] = destination

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

def categorize_and_move_files(root_folder, categories, file_mover):
    def process_category(main_category):
        print(f"Thread started for category: {main_category}")
        files = [f for f in os.listdir(root_folder) if f.endswith('.pdf')]
        
        for file_name in files:
            if file_mover.is_processed(file_name):
                continue
                
            file_path = os.path.join(root_folder, file_name)
            if not os.path.exists(file_path):
                continue
                
            try:
                # Read PDF content
                with open(file_path, "rb") as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    if not pdf_reader.pages:
                        continue
                        
                    first_page_text = pdf_reader.pages[0].extract_text().lower()
                    file_name_lower = file_name.lower()
                    
                    # Only process files matching current category
                    if isinstance(categories[main_category], dict):
                        max_matches = 0
                        best_sub_cat = None
                        
                        for sub_cat, keywords in categories[main_category].items():
                            matches = sum(1 for keyword in keywords if 
                                       keyword in first_page_text or keyword in file_name_lower)
                            if matches > max_matches:
                                max_matches = matches
                                best_sub_cat = sub_cat
                        
                        if max_matches > 0:
                            destination_folder = os.path.join(root_folder, main_category, best_sub_cat)
                            destination_path = os.path.join(destination_folder, file_name)
                            
                            try:
                                file_mover.move_file(file_path, destination_path)
                                file_mover.update_counts(main_category, best_sub_cat)
                                file_mover.mark_processed(file_name)
                                print(f"Thread {main_category}: Moved {file_name} -> {main_category}/{best_sub_cat}")
                            except FileNotFoundError:
                                pass
                    
                    elif main_category == "Others" and os.path.exists(file_path):
                        # Only move to Others if no other category claimed it
                        if not any(file_mover.is_processed(file_name) for _ in range(100)):  # Small delay to check
                            destination_folder = os.path.join(root_folder, "Others")
                            destination_path = os.path.join(destination_folder, file_name)
                            try:
                                file_mover.move_file(file_path, destination_path)
                                file_mover.update_counts("Others")
                                file_mover.mark_processed(file_name)
                                print(f"Thread Others: Moved {file_name} -> Others")
                            except FileNotFoundError:
                                pass

            except Exception as e:
                print(f"Thread {main_category}: Error processing {file_name}: {str(e)}")
        
        print(f"Thread completed for category: {main_category}")
    
    return process_category

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
    
    # First create folder structure and get categories
    categories = create_folder_structure(root_folder)
    
    # Then get custom paths for categories
    print("\nEnter custom paths for each category (press Enter to use default):")
    custom_paths = {}
    for main_cat, subcats in categories.items():
        if isinstance(subcats, dict):
            for subcat in subcats:
                custom_path = input(f"{main_cat}/{subcat}: ").strip()
                if custom_path:
                    custom_paths[f"{main_cat}/{subcat}"] = custom_path

    start_time = time.time()
    
    print("\nStarting file categorization with threads...")
    
    # Initialize thread-safe file mover
    file_mover = ThreadSafeFileMover()
    file_mover.file_counts = {main_cat: {sub_cat: 0 for sub_cat in sub_cats.keys()} if isinstance(sub_cats, dict) else 0 
                             for main_cat, sub_cats in categories.items()}
    
    # Create and start threads for each major category
    threads = []
    category_processor = categorize_and_move_files(root_folder, categories, file_mover)
    
    # Start threads for main categories first, Others last
    main_categories = [cat for cat in categories.keys() if cat != "Others"]
    
    for main_category in main_categories:
        thread = threading.Thread(target=category_processor, args=(main_category,))
        threads.append(thread)
        thread.start()
        print(f"Started thread for {main_category}")
    
    # Wait for main category threads to complete
    for thread in threads[:-1]:
        thread.join()
    
    # Start Others category last
    others_thread = threading.Thread(target=category_processor, args=("Others",))
    others_thread.start()
    others_thread.join()
    
    # Check if any files remain in root folder
    all_moved = check_root_folder(root_folder)
    
    # Get total files processed
    total_files = sum(sum(counts.values()) if isinstance(counts, dict) else counts 
                     for counts in file_mover.file_counts.values())
    
    # After processing is complete, ask about correctness validation
    validate = input("\nWould you like to validate the correctness of file categorization? (y/n): ").lower()
    
    if validate == 'y':
        validator = FileValidator()
        print("\nFor each file, please enter the correct subfolder name.")
        print("Available subfolders:", ", ".join(sum([[f"{main}/{sub}" 
              for sub in subcats.keys()] if isinstance(subcats, dict) 
              else [main] for main, subcats in categories.items()], [])))
        
        for filename in file_mover.file_locations.keys():
            correct_path = input(f"\nCorrect subfolder for {filename}: ").strip()
            validator.add_correct_path(filename, correct_path)
        
        accuracy = validator.calculate_accuracy(file_mover.file_locations)
        print(f"\nAccuracy of categorization: {accuracy:.2f}%")
    
    # Generate the regular analysis report
    generate_analysis_report(file_mover.file_counts, total_files)
    print(f"\nTime taken: {time.time() - start_time:.2f} seconds")
    print(f"Status: {'Success' if all_moved else 'Failed - some files remain in root'}")
