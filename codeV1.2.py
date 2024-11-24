# (Without threading)
import os
import PyPDF2
import time
import threading
from queue import Queue

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
    
    print("Multilevel folder structure created successfully.")
    return categories


def worker(main_category, categories, root_folder, file_queue, lock):
    while not file_queue.empty():
        file_name = file_queue.get()
        file_path = os.path.join(root_folder, file_name)

        try:
            # Read PDF content
            with open(file_path, "rb") as f:
                pdf_reader = PyPDF2.PdfReader(f)
                if pdf_reader.pages:
                    first_page_text = pdf_reader.pages[0].extract_text().lower()
                    file_name_lower = file_name.lower()

                    # Find best matching subcategory
                    best_sub_cat = None
                    max_matches = 0

                    for sub_cat, keywords in categories[main_category].items():
                        matches = sum(1 for keyword in keywords if keyword in first_page_text or keyword in file_name_lower)
                        if matches > max_matches:
                            max_matches = matches
                            best_sub_cat = sub_cat

                    # Move file to appropriate folder
                    if max_matches > 0 and best_sub_cat:
                        destination_folder = os.path.join(root_folder, main_category, best_sub_cat)
                        os.makedirs(destination_folder, exist_ok=True)

                        with lock:  # Ensure thread-safe file moving
                            os.rename(file_path, os.path.join(destination_folder, file_name))
                            print(f"Moved: {file_name} -> {main_category}/{best_sub_cat}")
                    else:
                        # Move to Others if no matches found
                        destination_folder = os.path.join(root_folder, "Others")
                        os.makedirs(destination_folder, exist_ok=True)

                        with lock:  # Ensure thread-safe file moving
                            os.rename(file_path, os.path.join(destination_folder, file_name))
                            print(f"Moved: {file_name} -> Others")

        except Exception as e:
            print(f"Error processing {file_name}: {e}")

        file_queue.task_done()


def categorize_and_move_files(root_folder, categories):
    files = [f for f in os.listdir(root_folder) if f.endswith('.pdf')]
    file_queue = Queue()
    lock = threading.Lock()
    threads = []

    # Populate the queue with files
    for file_name in files:
        file_queue.put(file_name)

    # Create and start a thread for each major category
    for main_category in categories.keys():
        thread = threading.Thread(target=worker, args=(main_category, categories, root_folder, file_queue, lock))
        thread.start()
        threads.append(thread)

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    print("All files have been processed.")

def generate_analysis_report(file_counts, total_files):
    print("\nSummary:")
    print(f"Total files found in root folder: {total_files}\n")
    for main_cat, sub_counts in file_counts.items():
        if isinstance(sub_counts, dict):
            total = sum(sub_counts.values())
            if total > 0:
                print(f"{main_cat}: {total} files")
                for sub_cat, count in sub_counts.items():
                    if count > 0:
                        print(f"  └─{sub_cat}: {count}")
        elif sub_counts > 0:
            print(f"{main_cat}: {sub_counts} files")



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
    
    categorize_and_move_files(root_folder, categories)
    
    print(f"\nTime taken: {time.time() - start_time:.2f} seconds")
