import json
import csv

def get_data(filename, urls_file, data_file, categories_file):
    with open(urls_file, 'r') as f:
        urls_data = json.load(f)
    
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    with open(categories_file, 'r') as f:
        categories = json.load(f)

    pk = next((item['pk'] for item in urls_data if filename in item['fields']['path']), None)
    if pk is None:
        return f"Filename {filename} not found in urls file."
    
    category_id = next((item['fields']['category_id'] for item in data if item['pk'] == pk), None)
    if category_id is None:
        return f"Category data not found for pk {pk}."
    
    category = next((item for item in categories if item['pk'] == category_id), None)
    if category is None:
        return f"Category not found for category_id {category_id}."
    
    return {
        "name": category['fields']['name'],
        "slug": category['fields']['slug'],
        "category_pk": pk
    }

def parse_cue(cue_str):
    if not cue_str or cue_str.strip() == "":
        return None, None
    try:
        start, end = cue_str.split('-')
        start_time = int(start.strip())
        end_time = 70000 if end.strip().lower() == 'end' else int(end.strip())
        return start_time, end_time
    except (ValueError, AttributeError):
        return None, None

def generate_json_from_csv(csv_file, urls_file, data_file, categories_file, output_file):
    result = []
    pk_counter = 3000  
    
    with open(csv_file, 'r') as f:
        csv_reader = csv.DictReader(f)
        
        for row in csv_reader:
            type_value = row['Type'].strip()
            if type_value not in ['EXPLANATION', 'SEQUENCE', 'UNIT']:
                print(f"Skipping {row['movie']} - invalid type: {type_value}")
                continue
            
            start_time, end_time = parse_cue(row['cue'])
            filename = row['movie']
            data = get_data(filename, urls_file, data_file, categories_file)
            
            if isinstance(data, str):
                print(f"Skipping {filename} - {data}")
                continue
            
            json_obj = {
                "model": "kalari.CategoriesMovements",
                "pk": pk_counter,
                "fields": {
                    "name": data["name"],
                    "category_data_movements_id": data["category_pk"],
                    "related_explanation_slug": f"{data['slug']}",
                    "type": type_value
                }
            }
            
            if start_time is not None and end_time is not None:
                json_obj["fields"].update({"start_time": start_time, "end_time": end_time})
            else:
                json_obj["fields"].update({"is_related_only": True})
            
            result.append(json_obj)
            pk_counter += 1
    
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    return result

csv_file = "input_files/cue_dropdown.csv" 
urls_file = "input_files/odissi_categories_data_urls.json"
data_file = "input_files/odissi_categories_data.json"
categories_file = "input_files/odissi_categories.json"
output_file = "odissi_categories_movements.json"

result = generate_json_from_csv(csv_file, urls_file, data_file, categories_file, output_file)
print(json.dumps(result, indent=2))
