import csv
import pyperclip

# Function to dump clipboard content to a CSV file
def dump_clipboard_to_csv(filename):
    # Read data from clipboard
    clipboard_content = pyperclip.paste().strip().split('\n')
    
    # Write data to CSV file
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for line in clipboard_content:
            writer.writerow(line.split())

    print(f"Clipboard content has been dumped to '{filename}'.")

# Function to read data from clipboard dump CSV file
def read_data_from_csv(filename):
    data = []
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append(row)
    return data

# Define constant planet values
planet_values = {
    "Mitra": 15,
    "Parama": 15,
    "Pratyak": -15,
    "Kshema": 15,
    "Naidhana": -15,
    "Sampat": 30,
    "Janma": -15,
    "Saadhana": 15,
    "Vipat": -15
}
murthi = {
    "Swarna_g":4,
    "Rajata_g":3,
    "Tamra_g":2,
    "Loha_g":1,
    "Swarna_b":1,
    "Rajata_b":2,
    "Tamra_b":3,
    "Loha_b":4,
    
    
    
    }

# Function to calculate the total value of a planet
def calculate_planet_value(planet):
    tara = planet.split()[0]  # Extracting the tara name from the planet name
    value = planet_values.get(tara, 0)
    return value

# Function to process clipboard data and calculate total values
def process_clipboard_data(clipboard_filename, output_filename):
    dump_clipboard_to_csv(clipboard_filename)
    clipboard_data = read_data_from_csv(clipboard_filename)
    
    total_value = 0
    planet_total_values = {}
    for row in clipboard_data:
        planet = row['Planet']
        tara = row['Tara']
        planet_value = calculate_planet_value(tara)
        planet_total_values[planet] = planet_value
        total_value += planet_value

    # Add total value to the planet total values
    planet_total_values['Total'] = total_value

    # Write results to CSV file
    with open(output_filename, 'w', newline='') as csvfile:
        fieldnames = ['Planet', 'Total Value']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for planet, value in planet_total_values.items():
            writer.writerow({'Planet': planet, 'Total Value': value})

    print(f"Results have been saved to '{output_filename}'.")

# Process clipboard data and write results to CSV file



#---------------------------------------------------------------------- #

import csv

# Function to read data from planet_total_values.csv
def read_planet_total_values(filename):
    data = {}
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')  # Assuming tab-separated values
        for row in reader:
            if 'Total Value' in row:
                data[row['Planet']] = row['Total Value']
    return data

# Function to update navtara.csv with total values
def update_navtara_with_total_values(navtara_filename, planet_total_values_filename):
    planet_total_values = read_planet_total_values(planet_total_values_filename)

    print("Planet Values:", planet_total_values)

    # Read existing data from navtara.csv
    existing_data = []
    with open(navtara_filename, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')  # Assuming tab-separated values
        for row in reader:
            existing_data.append(row)

    # Add new rows with values from planet_total_values.csv
    new_rows = []
    new_row = [''] * len(existing_data[0])
    for key in planet_total_values:
        
        if key in existing_data[0]:
            index = existing_data[0].index(key)
            new_row[index] = planet_total_values[key]
        
    new_rows.append(new_row)

    # Write updated content back to navtara.csv
    with open(navtara_filename, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter='\t')  # Assuming tab-separated values
        writer.writerows(new_rows)

    print(f"New data from planet_total_values.csv has been added to navtara.csv.")

# Update navtara.csv with total values

