import json

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

    # Return the pk from the urls file and category data
    return {
        "name": name,
        "slug": slug,
        "category_pk": pk  # Use pk from the urls file
    }

# Input filenames
filename = "exs_101_bhumi.mp4"
urls_file = "input_files/odissi_categories_data_urls.json"
data_file = "input_files/odissi_categories_data.json"
categories_file = "input_files/odissi_categories.json"

# Get the data
result = get_data(filename, urls_file, data_file, categories_file)

# Print the result
print(result)

