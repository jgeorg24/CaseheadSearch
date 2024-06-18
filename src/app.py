import os
import re
import pandas as pd
from flask import Flask, render_template, request

app = Flask(__name__)

# Define paths to Excel files
DATA_DIR = os.path.join(os.getcwd(), 'data')  # Define the directory where data files are located
PROGRAMS = ['FNS', 'ADMA', 'F&CMA', 'ChildCare']  # List of programs, each program corresponds to an Excel file

# Home route
@app.route('/')
def index():
    return render_template('index.html', programs=PROGRAMS)  # Render the homepage with a list of programs

# Function to clean name inputs
def clean_name(name):
    return re.sub(r'[^a-zA-Z\s]', '', name.strip().upper())  # Remove non-alphabet characters and convert to uppercase

# Function to extract main last name without initials
def extract_main_last_name(name):
    parts = name.split()
    main_last_name_parts = [part for part in parts if '.' not in part]  # Exclude parts containing periods (initials)
    return ' '.join(main_last_name_parts)  # Join remaining parts to form the main last name

# Function to find the case worker based on name range
def find_case_worker(last_name):
    cleaned_last_name = clean_name(last_name)  # Clean the input last name
    main_last_name = extract_main_last_name(cleaned_last_name)  # Extract the main part of the last name
    results = []
    overlapping_results = []
    alpha_listing = None

    for program in PROGRAMS:  # Iterate through each program to find the case worker
        file_path = os.path.join(DATA_DIR, f'{program}.xlsx')  # Construct the file path
        if os.path.exists(file_path):
            df = pd.read_excel(file_path)  # Read the Excel file into a DataFrame
            df['LastName'] = df['LastName'].str.strip().str.upper()  # Normalize LastName column
            df['Overlap'] = df['Overlap'].str.strip().str.upper().fillna('')  # Normalize Overlap column and fill NaN with empty string

            # Check for exact overlap match first
            exact_overlap_matches = df[df['Overlap'].str.contains(f'\\b{cleaned_last_name}\\b', regex=True)]  # Find exact matches in Overlap column
            for index, row in exact_overlap_matches.iterrows():
                overlapping_results.append({  # Add each match to overlapping_results list
                    'Program': program,
                    'CaseWorker': row['CaseWorker'],
                    'BackupBuddy': row.get('BackupBuddy', ''),
                    'EXT': row.get('EXT', ''),
                    'Supervisor': row.get('Supervisor', ''),
                    'LastName': row['LastName']
                })

            # If exact overlaps were found, skip the alphabetical range match
            if not exact_overlap_matches.empty:
                alpha_listing = f"Matches for '{cleaned_last_name}' found in exact overlap."  # Set alpha_listing message
                continue

            # Check for alphabetical range matches
            for index, row in df.iterrows():
                name_range = row['LastName'].split('-')  # Split the range in LastName column
                if len(name_range) == 2:
                    start_name = name_range[0].strip()
                    end_name = name_range[1].strip()

                    # Get the main last name without initials from the range
                    main_start_name = extract_main_last_name(start_name)
                    main_end_name = extract_main_last_name(end_name)

                    # Check if the main_last_name falls within the range
                    if main_start_name <= main_last_name <= main_end_name:
                        results.append({  # Add match to results list
                            'Program': program,
                            'CaseWorker': row['CaseWorker'],
                            'BackupBuddy': row.get('BackupBuddy', ''),
                            'EXT': row.get('EXT', ''),
                            'Supervisor': row.get('Supervisor', ''),
                            'LastName': row['LastName']
                        })
                        alpha_listing = f"Matches for '{cleaned_last_name}' found in range '{row['LastName']}' for program '{program}'."  # Set alpha_listing message
                        break  # Exit the loop as we found a match

    return results, overlapping_results, alpha_listing, cleaned_last_name  # Return results and messages for display

# Search route
@app.route('/search', methods=['POST'])
def search():
    last_name_input = request.form['last_name']  # Get the input from the form
    results, overlapping_results, alpha_listing, cleaned_last_name = find_case_worker(last_name_input)  # Call find_case_worker function
    return render_template('index.html', results=results, programs=PROGRAMS, last_name_input=last_name_input,
                           overlapping_results=overlapping_results, alpha_listing=alpha_listing,
                           cleaned_last_name=cleaned_last_name)  # Render the homepage with results
if __name__ == '__main__':
    app.run()

