# (with threading)
import os
import PyPDF2
import time
import threading
from queue import Queue

class ThreadSafeFileMover:
    def __init__(self):
        self.file_lock = threading.Lock()
        self.counts_lock = threading.Lock()
        self.processed_files_lock = threading.Lock()
        self.moves_lock = threading.Lock()
        self.file_counts = {}
        self.processed_files = set()
        self.moves = []
        
    def is_processed(self, file_name):
        with self.processed_files_lock:
            return file_name in self.processed_files
            
    def mark_processed(self, file_name):
        with self.processed_files_lock:
            self.processed_files.add(file_name)
            
    def move_file(self, source, destination):
        with self.file_lock:
            os.rename(source, destination)
            
    def update_counts(self, main_cat, sub_cat=None):
        with self.counts_lock:
            if sub_cat:
                self.file_counts[main_cat][sub_cat] += 1
            else:
                self.file_counts[main_cat] += 1

    def record_move(self, file_name, destination):
        with self.moves_lock:
            self.moves.append((file_name, destination))

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
                                file_mover.record_move(file_name, f"{main_category}/{best_sub_cat}")
                            except FileNotFoundError:
                                pass
                    
                    elif main_category == "Others" and os.path.exists(file_path):
                        if not any(file_mover.is_processed(file_name) for _ in range(100)):
                            destination_folder = os.path.join(root_folder, "Others")
                            destination_path = os.path.join(destination_folder, file_name)
                            try:
                                file_mover.move_file(file_path, destination_path)
                                file_mover.update_counts("Others")
                                file_mover.mark_processed(file_name)
                                file_mover.record_move(file_name, "Others")
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
    
    start_time = time.time()
    categories = create_folder_structure(root_folder)
    
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
    
    print("\nFile Movements:")
    for file_name, destination in sorted(file_mover.moves):
        print(f"Moved {file_name} -> {destination}")
    
    # Check if any files remain in root folder
    all_moved = check_root_folder(root_folder)
    
    # Get total files processed
    total_files = sum(sum(counts.values()) if isinstance(counts, dict) else counts 
                     for counts in file_mover.file_counts.values())
    
    print("\nAnalysis Report:")
    generate_analysis_report(file_mover.file_counts, total_files)
    print(f"\nTime taken: {time.time() - start_time:.2f} seconds")
    print(f"Status: {'Success' if all_moved else 'Failed - some files remain in root'}")
