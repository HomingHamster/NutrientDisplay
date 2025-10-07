import csv
import re
from collections import OrderedDict

# Nutrient name mapping dict `d` here
d = {
    # Amino Acids
    "Alanine": "Alanine",
    "Arginine": "Arginine",
    "Aspartic Acid": "Aspartic Acid",
    "Cysteine": "Cysteine",
    "Glutamic Acid": "Glutamic Acid",
    "Glutamine": "Glutamine",
    "Glycine": "Glycine",
    "Histidine": "Histidine",
    "Isoleucine": "Isoleucine",
    "Leucine": "Leucine",
    "Lysine": "Lysine",
    "Methionine": "Methionine",
    "Phenylalanine": "Phenylalanine",
    "Proline": "Proline",
    "Serine": "Serine",
    "Threonine": "Threonine",
    "Tryptophan": "Tryptophan",
    "Tyrosine": "Tyrosine",
    "Valine": "Valine",
    "Taurine": "Taurine",
    # Vitamins
    "Vitamin A": "Vitamin A",
    "Vitamin C": "Vitamin C",
    "Vitamin D": "Vitamin D",
    "Vitamin E": "Vitamin E",
    "Vitamin K": "Vitamin K",
    "Thiamin (B1)": "Vitamin B1",
    "Thiamin": "Vitamin B1",
    "Riboflavin (B2)": "Vitamin B2",
    "Riboflavin": "Vitamin B2",
    "Niacin (B3)": "Vitamin B3",
    "Niacin": "Vitamin B3",
    "Pantothenic Acid (B5)": "Vitamin B5",
    "Pantothenic Acid": "Vitamin B5",
    "Vitamin B6": "Vitamin B6",
    "Biotin (B7)": "Vitamin B7",
    "Biotin": "Vitamin B7",
    "Folate (B9)": "Vitamin B9",
    "Folate": "Vitamin B9",
    "Vitamin B12": "Vitamin B12",
    "Alpha-Lipoic Acid": "Alpha-Lipoic Acid",
    # Minerals
    "Calcium": "Calcium",
    "Iron": "Iron",
    "Magnesium": "Magnesium",
    "Phosphorus": "Phosphorus",
    "Potassium": "Potassium",
    "Sodium": "Sodium",
    "Zinc": "Zinc",
    "Copper": "Copper",
    "Manganese": "Manganese",
    "Selenium": "Selenium",
    "Chromium": "Chromium",
    "Molybdenum": "Molybdenum",
    "Iodine": "Iodine",
    "Fluoride": "Fluoride",
    "Chloride": "Chloride",
    "Sulfur": "Sulfur",
    "Boron": "Boron",
    "Silicon": "Silicon",
    "Vanadium": "Vanadium",
    "Nickel": "Nickel",
    "Cobalt": "Cobalt",
    # Fatty Acids & Lipids
    "Docosahexaenoic Acid (DHA)": "Docosahexaenoic Acid (DHA)",
    "Eicosapentaenoic Acid (EPA)": "Eicosapentaenoic Acid (EPA)",
    "Omega-3 Fatty Acids (ALA, EPA, DHA)": "Omega-3 Fatty Acids",
    "Omega-3 Fatty Acids (ALA)": "Omega-3 Fatty Acids",
    "Omega-3 Fatty Acids (Combined ALA, EPA, DHA)": "Omega-3 Fatty Acids",
    "Omega-3 Fatty Acids (EPA+DHA)": "Omega-3 Fatty Acids",
    "Omega-6 Fatty Acids (LA, GLA)": "Omega-6 Fatty Acids",
    "Omega-6 Fatty Acids (LA)": "Omega-6 Fatty Acids",
    "MCTs (Medium-chain triglycerides)": "MCTs",
    "MCTs": "MCTs",
    "Algal Oil": "Algal Oil",
    # Phytonutrients & Plant Compounds
    "Beta-Carotene": "Beta-Carotene",
    "Lutein": "Lutein",
    "Zeaxanthin": "Zeaxanthin",
    "Lycopene": "Lycopene",
    "Chlorophyll": "Chlorophyll",
    "Curcumin": "Curcumin",
    "Resveratrol": "Resveratrol",
    "Quercetin": "Quercetin",
    "EGCG (Epigallocatechin gallate)": "EGCG",
    "EGCG": "EGCG",
    "Anthocyanins": "Anthocyanins",
    "Flavonoids": "Flavonoids",
    "Polyphenols": "Polyphenols",
    "Isoflavones": "Isoflavones",
    "Saponins": "Saponins",
    "Tannins": "Tannins",
    "Phytosterols": "Phytosterols",
    "Beta-Glucans": "Beta-Glucans",
    "Inulin": "Inulin",
    "Chlorella": "Chlorella",
    "Spirulina": "Spirulina",
    # Probiotics & Microbial Supplements
    "Lactobacillus acidophilus": "Lactobacillus acidophilus",
    "Bifidobacterium bifidum": "Bifidobacterium bifidum",
    "Saccharomyces boulardii": "Saccharomyces boulardii",
    "Bacillus coagulans": "Bacillus coagulans",
    # Other Nutrients & Co-factors
    "Choline": "Choline",
    "Coenzyme Q10": "Coenzyme Q10",
    "Carnitine": "Carnitine",
    "Inositol": "Inositol",
    "PABA (Para-aminobenzoic acid)": "PABA",
    "PABA": "PABA",
    "Glucosamine": "Glucosamine",
    "Collagen": "Collagen",
    # Macronutrients & Miscellany
    "Total Protein": "Protein",
    "Dietary Fiber": "Dietary Fiber",
    "Water": "Water"
}

def parse_age_range(age_str):
    r = r'[\\D]'
    if age_str == "Birth to 6 months" or age_str == "0<6 months":
        return 0, 6
    age_str = age_str.lower()
    if "months" in age_str:
        parts = re.findall(r'\d+', age_str)
        if len(parts) == 2:
            return int(parts[0]), int(parts[1])
        elif len(parts) == 1:
            val = int(parts[0])
            return val, val
    elif "year" in age_str:
        parts = re.findall(r'\d+', age_str)
        if len(parts) == 2:
            return int(parts[0])*12, int(parts[1])*12
        elif len(parts) == 1:
            if '+' in age_str:
                return int(parts[0])*12, None
            else:
                year = int(parts[0])
                return year*12, year*12
    return None, None

def load_complete(path):
    data = []
    with open(path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['male'] in ['ND', 'CS']:
                continue
            for gender in ['male', 'female', 'pregnant', 'lactating']:
                amt = row.get(gender)
                if not amt:
                    continue
                start, end = parse_age_range(row['age'])
                nutrient = d.get(row['nutrient'])
                if not nutrient:
                    print(f"Skipping unknown nutrient {row['nutrient']} in complete.csv")
                    continue
                data.append({
                    'nutrient': nutrient,
                    'gender': gender.capitalize(),
                    'age_start_months': start,
                    'age_end_months': end,
                    'amount': amt,
                    'unit': row['footnotes'].split(' - ')[1] if 'footnotes' in row and ' - ' in row['footnotes'] else '',
                    'source_type': 'RDA Extract',
                    'source_name': 'Extract from ODS',
                    'source_url': 'https://ods.od.nih.gov/',
                    'notes': 'RDA calculated value'
                })
    return data

def load_comprehensive(path):
    data = []
    with open(path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            start, end = parse_age_range(row['Age_Group'])
            nutrient = d.get(row['Nutrient'])
            if not nutrient:
                print(f"Skipping unknown nutrient {row['Nutrient']} in comprehensive.csv")
                continue
            data.append({
                'nutrient': nutrient,
                'gender': row['Gender'],
                'age_start_months': start,
                'age_end_months': end,
                'amount': row['Amount'],
                'unit': row['Unit'],
                'source_type': row['Source_Type'],
                'source_name': row['Source_Name'],
                'source_url': row['Source_URL'],
                'notes': row.get('Nutrient_Notes', '')
            })
    return data

def load_enhanced(path):
    data = []
    with open(path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('Male') in ['ND', 'CS']:
                continue
            for gender in ['Male', 'Female', 'Pregnant', 'Lactating']:
                amt = row.get(gender)
                if not amt:
                    continue
                start, end = parse_age_range(row['Age_Group'])
                nutrient = d.get(row['Nutrient'])
                if not nutrient:
                    print(f"Skipping unknown nutrient {row['Nutrient']} in enhanced.csv")
                    continue
                data.append({
                    'nutrient': nutrient,
                    'gender': gender,
                    'age_start_months': start,
                    'age_end_months': end,
                    'amount': amt,
                    'unit': row.get('Unit',''),
                    'source_type': 'Enhanced',
                    'source_name': row.get('Source_Links','') if row.get('Source_Links','').startswith("https:") else 'Amateur calculation by Cognisa Ltd, for research purposes only',
                    'source_url': '',
                    'notes': f"{row.get('Footnotes','')} {row.get('Nutrient_Notes','')}".strip()
                })
    return data

def merge_datasets(complete, comprehensive, enhanced):
    # Prioritize complete, then comprehensive, then enhanced
    merged = OrderedDict()
    def key(rec):
        return (rec['nutrient'], rec['gender'], rec['age_start_months'], rec['age_end_months'])
    for dataset in (complete, comprehensive, enhanced):
        for rec in dataset:
            k = key(rec)
            if k not in merged:
                merged[k] = rec
    return list(merged.values())

def write_csv(data, path='final_nutrients.csv'):
    fields = ['nutrient','gender','age_start_months','age_end_months','amount','unit','source_type','source_name','source_url','notes']
    with open(path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

if __name__ == '__main__':
    complete_data = load_complete('complete.csv')
    comprehensive_data = load_comprehensive('comprehensive.csv')
    enhanced_data = load_enhanced('enhanced.csv')

    final_data = merge_datasets(complete_data, comprehensive_data, enhanced_data)
    write_csv(final_data)
    print(f"Finished writing {len(final_data)} normalized nutrient records to final_nutrients.csv")
