import json
import csv
from collections import OrderedDict

def parse_cue(cue_str):
    if not cue_str or cue_str.strip() == "":
        return None, None
    try:
        start, end = cue_str.split('-')
        start_time = int(start.strip())
        # If 'end' is found in the CSV, default to 2000
        end_time = 2000 if end.strip().lower() == 'end' else int(end.strip())
        return start_time, end_time
    except (ValueError, AttributeError):
        return None, None

def get_combined_data(file1, file2, urls_file, data_file, categories_file):
    def get_data(filename, urls_file, data_file, categories_file):
        with open(urls_file, 'r') as f:
            urls_data = json.load(f)

        with open(data_file, 'r') as f:
            data = json.load(f)

        with open(categories_file, 'r') as f:
            categories = json.load(f)

        pk = None
        for item in urls_data:
            if filename in item['fields']['path']:
                pk = item['pk']
                break

        if pk is None:
            return None, f"Filename {filename} not found in urls file."

        category_id = None
        for item in data:
            if item['pk'] == pk:
                category_id = item['fields']['category_id']
                break

        if category_id is None:
            return None, f"Category data not found for pk {pk}."

        slug, name = None, None
        for item in categories:
            if item['pk'] == category_id:
                slug = item['fields']['slug']
                name = item['fields']['name']
                break

        if slug is None or name is None:
            return None, f"Category not found for category_id {category_id}."

        return {
            "name": name,
            "slug": slug,
            "category_pk": pk
        }, None

    data1, error1 = get_data(file1, urls_file, data_file, categories_file)
    if error1:
        return None, f"Error processing {file1}: {error1}"

    data2, error2 = get_data(file2, urls_file, data_file, categories_file)
    if error2:
        return None, f"Error processing {file2}: {error2}"

    # Combine the two data sets into one dictionary as before
    return {
        "name": data2["name"],
        "slug": data2["slug"],
        "category_pk": data1["category_pk"]
    }, None

def generate_json_from_csv(csv_file, urls_file, data_file, categories_file, output_file):
    result = []
    pk_counter = 3000

    with open(csv_file, 'r') as f:
        csv_reader = csv.DictReader(f)

        for row in csv_reader:
            type_value = row['type'].strip()
            if type_value not in ['EXPLANATION', 'SEQUENCE', 'UNIT', 'CONTEXT']:
                print(f"Skipping {row['movie']} - invalid type: {type_value}")
                continue

            start_time, end_time = parse_cue(row['cue'])

            file1 = row['category_pk']  # from the CSV 'category_pk' column
            file2 = row['movie']        # from the CSV 'movie' column

            data, error = get_combined_data(file1, file2, urls_file, data_file, categories_file)
            if error:
                print(f"Skipping {file1}, {file2} - {error}")
                continue

            # Use OrderedDict to guarantee the exact field order
            fields_dict = OrderedDict()

            # 1) name
            fields_dict["name"] = data["name"]
            # 2) category_data_movements_id
            fields_dict["category_data_movements_id"] = data["category_pk"]

            if start_time is not None and end_time is not None:
                # 3) When cue times exist, add start_time and end_time next
                fields_dict["start_time"] = start_time
                fields_dict["end_time"] = end_time
                # 4) related_explanation_slug
                fields_dict["related_explanation_slug"] = f"{data['slug']}"
                # 5) type
                fields_dict["type"] = type_value
            else:
                # When cue times are absent, add the keys in the required order:
                # 3) related_explanation_slug
                fields_dict["related_explanation_slug"] = f"{data['slug']}"
                # 4) type
                fields_dict["type"] = type_value
                # 5) is_related_only comes after type
                fields_dict["is_related_only"] = True

            # Build the full JSON object using an OrderedDict
            json_obj = OrderedDict()
            json_obj["model"] = "kalari.CategoriesMovements"
            json_obj["pk"] = pk_counter
            json_obj["fields"] = fields_dict

            result.append(json_obj)
            pk_counter += 1

    # Write out the JSON, preserving the key order (sort_keys=False).
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, sort_keys=False)

    return result

# File paths
csv_file = "input_files/cue_file.csv"
urls_file = "input_files/odissi_categories_data_urls.json"
data_file = "input_files/odissi_categories_data.json"
categories_file = "input_files/odissi_categories.json"
output_file = "odissi_categories_movements.json"

# Generate JSON
result = generate_json_from_csv(csv_file, urls_file, data_file, categories_file, output_file)
