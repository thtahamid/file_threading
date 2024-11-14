from PyPDF2 import PdfReader

# Function to extract and print metadata
def extract_metadata(file_path):
    try:
        reader = PdfReader(file_path)
        metadata = reader.metadata

        if metadata:
            print("Metadata for", file_path)
            print("-" * 30)
            for key, value in metadata.items():
                print(f"{key}: {value}")
            print("-" * 30)
        else:
            print("No metadata found for this file.")
    except Exception as e:
        print(f"Error reading metadata from '{file_path}': {e}")

# Ask user for the path to the PDF file
file_path = input("Enter the path to the PDF file: ")
extract_metadata(file_path)

