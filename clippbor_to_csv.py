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

#Data format we need 
#jup pararma
def read_data_from_csv(filename):
    data = []
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile,fieldnames = ['Planet', 'Tara', 'Murthi', 'House', 'Under', 'vedha_from','from', 'Causing','vedha_to','to','t2','t3'])
        next(reader)
        for row in reader:
            #cleaning the row
            
            #solving the tara type problem which is stored in house col
            if row['Tara']=='Parama':
                row['House']=row['vedha_from']
                
                if row['to']=='(Good)':
                    row['Under']=row['t2']
                    #print("paraveda",row["Under"])
                elif row['to']=='-':
                    row['Under']=row['to']
                    #print("paraveda",row["Under"])
                
            else:
                if row['Causing']=='(Good)':
                    row["Under"]=row['vedha_to']
                    #print("veda",row["Under"])
                elif row['Causing']=='-':
                    row["Under"]=row['Causing']
                    #print("veda",row["Under"])
                    
                    
                
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
planets = {
    'Sun': 0,
    'Moon': 0,
    'Mars': 0,
    'Mercury': 0,
    'Jupiter': 0,
    'Venus': 0,
    'Saturn': 0,
    'Rahu': 0,
    'Ketu':0,
    'Sun,': 0,
    'Moon,': 0,
    'Mars,': 0,
    'Mercury,': 0,
    'Jupiter,': 0,
    'Venus,': 0,
    'Saturn,': 0,
    'Rahu,': 0,
    'Ketu,': 0
    
    
}


murthi_val = {
    "Swarna_g":1,
    "Rajata_g":0.75,
    "Tamra_g":0.5,
    "Loha_g":.25,
    "Swarna_b":.25,
    "Rajata_b":0.75,
    "Tamra_b":0.5,
    "Loha_b":1,
    
    }

murthi_rec_g ={
    "Swarna":"Swarna_g",
    "Rajata":"Rajata_g",
    "Taamra":"Tamra_g",
    "Loha":"Loha_g",
    }
murthi_rec_b={
    
    "Swarna":"Swarna_b",
    "Rajata":"Rajata_b",
    "Taamra":"Tamra_b",
    "Loha":"Loha_b",
    }
    
# Function to calculate the total value of a planet
def calculate_planet_value(planet,murthi,chk):
    tara = planet.split()[0]  # Extracting the tara name from the planet name
    value = planet_values.get(tara, 0)
    if value > 0 :
        mul=murthi_val.get(murthi_rec_g.get(murthi,0),1)
    else:
        mul=murthi_val.get(murthi_rec_b.get(murthi,0),1)
        
    if(chk):
        return value*mul
    else:
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
        murthi = row['House']
        #cheking the vedha is present or not 
        vedha=row['Under']
        
        #if want to have values without murthis pass 0 or else 1
        planet_value = calculate_planet_value(tara,murthi,1)
        planet_value = planet_value * planets.get(vedha,1)
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

