import json
import csv

def get_data(filename, urls_file, data_file, categories_file):
    # Load the JSON files
    with open(urls_file, 'r') as f:
        urls_data = json.load(f)
    
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    with open(categories_file, 'r') as f:
        categories = json.load(f)

    # Find the pk from the urls file based on the filename
    pk = None
    for item in urls_data:
        if filename in item['fields']['path']:
            pk = item['pk']
            break
    
    if pk is None:
        return "Filename not found in urls file."
    
    # Use the pk to find the corresponding entry in the data file
    category_id = None
    for item in data:
        if item['pk'] == pk:
            category_id = item['fields']['category_id']
            break
    
    if category_id is None:
        return "Category data not found for the given pk."
    
    # Use the category_id to find the corresponding entry in the categories file
    slug = None
    name = None
    for item in categories:
        if item['pk'] == category_id:
            slug = item['fields']['slug']
            name = item['fields']['name']
            break
    
    if slug is None or name is None:
        return "Category not found for the given category_id."

    # Return the data including category_id as category_data_movements_id
    return {
        "name": name,
        "slug": slug,
        "category_pk": pk,
        "category_data_movements_id": pk  # Using pk directly as requested
    }

def parse_cue(cue_str):
    """Parse the cue string into start_time and end_time"""
    if not cue_str or cue_str.strip() == "":
        return None, None
    
    try:
        start, end = cue_str.split('-')
        start_time = int(start.strip())
        end_time = end.strip()
        if end_time.lower() == 'end':
            end_time = 70000  # Using 70000 as per your latest script
        else:
            end_time = int(end_time)
        return start_time, end_time
    except (ValueError, AttributeError):
        return None, None

def generate_json_from_csv(csv_file, urls_file, data_file, categories_file, output_file):
    result = []
    pk_counter = 3000  # Starting pk value
    
    with open(csv_file, 'r') as f:
        csv_reader = csv.DictReader(f)
        
        for row in csv_reader:
            # Process all types: EXPLANATION, SEQUENCE, UNIT
            type_value = row['type'].strip()
            if type_value not in ['EXPLANATION', 'SEQUENCE', 'UNIT']:
                print(f"Skipping {row['movie']} - invalid type: {type_value}")
                continue
                
            # Skip if cue is empty
            if not row['cue']:
                print(f"Skipping {row['movie']} - empty cue")
                continue
                
            start_time, end_time = parse_cue(row['cue'])
            if start_time is None or end_time is None:
                print(f"Skipping {row['movie']} - invalid cue format: {row['cue']}")
                continue
                
            filename = row['movie']
            data = get_data(filename, urls_file, data_file, categories_file)
            
            if isinstance(data, str):  # If get_data returns an error message
                print(f"Skipping {filename} - {data}")
                continue
                
            # Create the JSON object
            json_obj = {
                "model": "kalari.CategoriesMovements",
                "pk": pk_counter,
                "fields": {
                    "name": data["name"],
                    "category_data_movements_id": data["category_data_movements_id"],
                    "start_time": start_time,
                    "end_time": end_time,
                    "related_explanation_slug": f"{data['slug']}-un-exp",
                    "type": type_value  # Use the actual type from CSV
                }
            }
            
            result.append(json_obj)
            pk_counter += 1
    
    # Write to output file
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    return result

# Input files
csv_file = "input_files/SEQUENCE_CUE_POINTS.csv"
urls_file = "input_files/odissi_categories_data_urls.json"
data_file = "input_files/odissi_categories_data.json"
categories_file = "input_files/odissi_categories.json"
output_file = "output.json"

# Generate the JSON
result = generate_json_from_csv(csv_file, urls_file, data_file, categories_file, output_file)

# Print the result
print(json.dumps(result, indent=2))