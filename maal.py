# -*- coding: utf-8 -*-
"""Untitled90.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1uBU8hNlVSmHtusvdQNeFoVQAuUXYGnLl

TEXT EXTRACTION USING PADDLE OCR
"""

import pandas as pd
from paddleocr import PaddleOCR
from PIL import Image
import requests
from io import BytesIO
import numpy as np
from tqdm import tqdm  # Optional for showing progress bar
​
# Initialize the OCR model
ocr = PaddleOCR(use_angle_cls=True, lang='en',use_gpu=True)
​
# Load image from URL and convert to NumPy array
def load_image_from_url(url):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content)).convert('RGB')  # Convert to RGB format
    img_np = np.array(img)  # Convert PIL Image to NumPy array
    return img_np
​
# Function to extract text from image URL
def extract_text_from_image_url(image_url):
    img_np = load_image_from_url(image_url)
    result = ocr.ocr(img_np, cls=True)

    # Join all text lines into a single string
    extracted_text = " ".join([line[1][0] for line in result[0]])
    return extracted_text
​
# Main function to process the CSV
def process_csv(input_csv_path, output_csv_path):
    # Load the CSV into a pandas DataFrame and slice rows from start_row to end_row
    df = pd.read_csv(input_csv_path)

    # Create a list to store extracted text
    extracted_texts = []
​
    # Iterate through each row and process the image URL
    for index, row in tqdm(df.iterrows(), total=len(df)):
        image_url = row['image_link']  # Assuming the column name for the URL is 'image_link'
        try:
            text = extract_text_from_image_url(image_url)
        except Exception as e:
            print(f"Error processing {image_url}: {e}")
            text = ""  # Leave blank if there's an error
        extracted_texts.append(text)
​
    # Final save for the complete dataset
    df['extracted_text'] = extracted_texts
    df.to_csv(output_csv_path, index=False)
    print(f"Processed CSV saved to {output_csv_path}")
​
# Example usage
input_csv = '/kaggle/input/amazonmlchallengedataset/test.csv'
output_csv = 'train_with_text_test.csv'
process_csv(input_csv, output_csv)

"""FURTHER TESTING ACCORDING TO MODEL"""

def extract_entity_value(entity_name, extracted_text):
    # Convert extracted_text to lowercase for easier matching
    text = extracted_text.lower()

    # Replace commas with periods in numbers (e.g., 4,3 to 4.3)
    text = re.sub(r'(\d+),(\d+)', r'\1.\2', text)

    # Define unit map at the beginning of the function
    unit_map = {
            'mm': 'millimetre', 'millimeter': 'millimetre',
            'cm': 'centimetre', 'centimeter': 'centimetre',
            'm': 'metre', 'meter': 'metre',
            'in': 'inch', '"': 'inch', 'inches': 'inch',
            'ft': 'foot', 'feet': 'foot', 'yard': 'yard',
            'g': 'gram', 'mg': 'milligram', 'kg': 'kilogram', 'µg': 'microgram',
            'oz': 'ounce', 'lb': 'pound', 'lbs': 'pound', 'ton': 'ton',
            'v': 'volt', 'kv': 'kilovolt', 'mv': 'millivolt',
            'w': 'watt', 'kw': 'kilowatt', 'wat': 'watt',  # Correct misspelled "wat" to "watt"
            'cl': 'centilitre', 'centiliter': 'centilitre',
            'dl': 'decilitre', 'deciliter': 'decilitre',
            'fl oz': 'fluid ounce', 'gal': 'gallon', 'imp gallon': 'imperial gallon',
            'l': 'litre', 'liter': 'litre', 'ml': 'millilitre', 'milliliter': 'millilitre',
            'µl': 'microlitre', 'microliter': 'microlitre', 'pint': 'pint', 'quart': 'quart',
             'a': 'ampere', 'amp': 'ampere'
        }



    # Define patterns for different units
    patterns = {
          'width': r'\(?(\d+(?:\.\d+)?)\)?\s*\(?\s*(mm|millimetre|millimeter|cm|centimetre|centimeter|m|metre|meter|in|inch|"|inches|ft|foot|feet|yard)\s*\)?',
    'depth': r'\(?(\d+(?:\.\d+)?)\)?\s*\(?\s*(mm|millimetre|millimeter|cm|centimetre|centimeter|m|metre|meter|in|inch|"|inches|ft|foot|feet|yard)\s*\)?',
    'height': r'\(?(\d+(?:\.\d+)?)\)?\s*\(?\s*(mm|millimetre|millimeter|cm|centimetre|centimeter|m|metre|meter|in|inch|"|inches|ft|foot|feet|yard)\s*\)?',
    'item_weight': r'\(?(\d+(?:\.\d+)?)\)?\s*\(?\s*(g|gram|mg|milligram|kg|kilogram|µg|microgram|oz|ounce|lb|pound|ton)\s*\)?',
    'maximum_weight_recommendation': r'\(?(\d+(?:\.\d+)?)\)?\s*\(?\s*(g|gram|mg|milligram|kg|kilogram|µg|microgram|oz|ounce|lb|pound|ton)\s*\)?',
    'voltage': r'\(?(\d+(?:\.\d+)?)\)?\s*\(?\s*(v|volt|kv|kilovolt|mv|millivolt)\s*\)?',
    'wattage': r'\(?(\d+(?:\.\d+)?)\)?\s*\(?\s*(w|watt|kw|kilowatt|wat)\s*\)?',
    'item_volume': r'\(?(\d+(?:\.\d+)?)\)?\s*\(?\s*(cl|centilitre|centiliter|cubic\s*foot|cubic\s*inch|cup|dl|decilitre|deciliter|fl\s*oz|fluid\s*ounce|gal|gallon|imp\s*gallon|l|litre|liter|µl|microlitre|microliter|ml|millilitre|milliliter|pint|quart)\s*\)?',
        'current': r'(\d+(?:\.\d+)?)\s*(a|amp|ampere)'
    }

    # Use the appropriate pattern based on the entity name
    pattern = patterns.get(entity_name.lower(), r'(\d+(?:\.\d+)?)\s*(\w+)')

    # Find all matches in the text
    matches = re.findall(pattern, text)

    if matches:
        # Sort matches by numeric value (descending) and return the largest
        sorted_matches = sorted(matches, key=lambda x: float(x[0]), reverse=True)
        value, unit = sorted_matches[0]

        full_unit = unit_map.get(unit.lower(), unit)
        return f"{value} {full_unit}"

    # If wattage is not found directly, search for voltage and current
    if entity_name.lower() == 'wattage':
        voltage_match = re.search(patterns['voltage'], text)
        current_match = re.search(patterns['current'], text)
        if voltage_match and current_match:
            voltage = float(voltage_match.group(1))
            current = float(current_match.group(1))
            wattage = voltage * current
            return f"{wattage:.2f} watt"

    # If voltage is asked and not found, return wattage if available
    if entity_name.lower() == 'voltage':
        wattage_match = re.search(patterns['wattage'], text)
        if wattage_match:
            return f"{wattage_match.group(1)} {unit_map.get(wattage_match.group(2).lower(), wattage_match.group(2))}"

    # If wattage is asked and not found, return voltage if available
    if entity_name.lower() == 'wattage':
        voltage_match = re.search(patterns['voltage'], text)
        if voltage_match:
            return f"{voltage_match.group(1)} {unit_map.get(voltage_match.group(2).lower(), voltage_match.group(2))}"

    return ""

def process_csv(input_file_path, output_file_path):
    results = []
    with open(input_file_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            entity_name = row['entity_name']
            extracted_text = row['extracted_text']
            extracted_value = extract_entity_value(entity_name, extracted_text)
            results.append({
                'index': row['index'],
                'entity_name': entity_name,
                'extracted_value': extracted_value
            })

    # Write results to output CSV file
    with open(output_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['index', 'entity_name', 'extracted_value']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for result in results:
            writer.writerow(result)

    print(f"Results have been saved to {output_file_path}")
    return results

# Usage
input_file_path = '/kaggle/input/test-pred/updated_with_new_predictions.csv'
output_file_path = 'output7.csv'

results = process_csv(input_file_path, output_file_path)

# Print first few results as a sample
print("\nSample of processed results:")
for result in results[:5]:  # Print first 5 results
    print(f"Index: {result['index']}, Entity: {result['entity_name']}, Extracted Value: {result['extracted_value']}")