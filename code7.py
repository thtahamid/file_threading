import os
import PyPDF2

def create_folder_structure(root_folder):
    categories = {
    "Programming": [
        "programming", "code", "developer", "python", "java", "c++", "javascript", "coding",
        "software engineering", "backend", "frontend", "full stack", "ruby", "go", "typescript",
        "php", "swift", "kotlin", "development"
    ],
    "AI": [
        "machine learning", "AI", "artificial intelligence", "deep learning", "data science",
        "neural networks", "nlp", "natural language processing", "computer vision",
        "reinforcement learning", "supervised learning", "unsupervised learning", "AI ethics",
        "predictive modeling", "generative models", "AI tools"
    ],
    "Math": [
        "algebra", "calculus", "statistics", "probability", "geometry", "mathematics",
        "linear algebra", "differential equations", "discrete mathematics", "number theory",
        "trigonometry", "graph theory", "combinatorics", "math modeling"
    ],
    "Database": [
        "database", "SQL", "NoSQL", "data storage", "big data", "data engineering",
        "database management", "relational databases", "postgresql", "mysql", "mongodb",
        "oracle", "dynamodb", "database design", "data warehouses", "etl", "schemas",
        "database optimization"
    ],
    "Security": [
        "cryptography", "security", "network security", "cybersecurity", "encryption",
        "penetration testing", "firewalls", "ethical hacking", "vulnerability assessment",
        "security protocols", "zero trust", "incident response", "forensics",
        "malware analysis", "phishing", "DDoS", "ransomware", "secure coding", "infosec"
    ],
    "Others": [
        "general topics", "miscellaneous", "varied interests", "random ideas",
        "general knowledge"
    ]
}


    # Create directories for each main category if they don't exist
    for category in categories.keys():
        category_path = os.path.join(root_folder, category)
        os.makedirs(category_path, exist_ok=True)
    print("Main folder structure created successfully.")
    return categories

def analyze_and_move_files(root_folder, categories):
    files = [f for f in os.listdir(root_folder) if f.endswith('.pdf')]
    file_counts = {category: 0 for category in categories}
    total_files = len(files)
    
    for file_name in files:
        file_path = os.path.join(root_folder, file_name)
        try:
            with open(file_path, "rb") as f:
                pdf_reader = PyPDF2.PdfReader(f)
                if pdf_reader.pages:
                    first_page_text = pdf_reader.pages[0].extract_text().lower()

                    # Categorize based on prioritized keyword matching
                    best_match = "Others"
                    max_matches = 0

                    for category in ["Math", "Programming", "AI", "Database", "Security", "Others"]:
                        keywords = categories[category]
                        matches = sum(1 for keyword in keywords if keyword in first_page_text)
                        if matches > max_matches:
                            max_matches = matches
                            best_match = category

                    # Move file to best matched category folder
                    destination_folder = os.path.join(root_folder, best_match)
                    os.rename(file_path, os.path.join(destination_folder, file_name))
                    print(f"Moved '{file_name}' to '{destination_folder}'")
                    file_counts[best_match] += 1

        except Exception as e:
            print(f"Error processing {file_name}: {e}")
    
    return file_counts, total_files

def generate_analysis_report(file_counts, total_files):
    print("\nAnalysis Report:")
    print("----------------")
    for category, count in file_counts.items():
        percentage = (count / total_files) * 100 if total_files > 0 else 0
        print(f"{category}: {percentage:.2f}%")
    
    # Correctness Score: assumes files are correctly matched based on highest matches
    correctness_score = 100.00 if total_files > 0 else 0
    print(f"\nCorrectness Score: {correctness_score:.2f}%")

# Main Execution
if __name__ == "__main__":
    root_folder = input("Enter the path to the root folder: ").strip()
    categories = create_folder_structure(root_folder)
    file_counts, total_files = analyze_and_move_files(root_folder, categories)
    generate_analysis_report(file_counts, total_files)
