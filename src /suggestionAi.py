from fuzzywuzzy import process
import docx

# Function to read names from a .docx file
def load_names_from_docx(file_path):
    doc = docx.Document(file_path)
    names = [paragraph.text.strip() for paragraph in doc.paragraphs if paragraph.text.strip()]
    return names

# Load names from the .docx file
names = load_names_from_docx('data/Names.docx')

def suggest_name(input_name):
    # Convert input name to uppercase for case-insensitive comparison
    input_name_upper = input_name.strip().upper()
    # Convert names to uppercase for case-insensitive comparison
    names_upper = [name.upper() for name in names]
    
    # Check if the input name is an exact match to any name in the list
    if input_name_upper in names_upper:
        return None, 100  # Return None to indicate no suggestion is needed

    # Use fuzzy matching to find the best match from names list
    suggested_name, score = process.extractOne(input_name, names)
    return suggested_name, score

if __name__ == '__main__':
    input_name = input("Enter a name: ")
    suggested_name, score = suggest_name(input_name)
    if suggested_name:
        print(f"Suggested Name: {suggested_name} (Score: {score})")
    
