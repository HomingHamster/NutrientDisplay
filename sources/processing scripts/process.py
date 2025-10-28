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
    s = age_str.lower().strip()
    if s.startswith("birth to") or s.startswith("0<6"):
        return 0, 6
    if "month" in s:
        nums = re.findall(r'\d+', s)
        if len(nums) == 2:
            return int(nums[0]), int(nums[1])
        elif len(nums) == 1:
            v = int(nums[0])
            return v, v
    if "year" in s:
        nums = re.findall(r'\d+', s)
        if len(nums) == 2:
            return int(nums[0])*12, int(nums[1])*12
        elif len(nums) == 1:
            if s.endswith("+"):
                return int(nums[0])*12, None
            else:
                v = int(nums[0])*12
                return v, v
    return None, None

def load_comprehensive(path):
    data = []
    with open(path, newline='') as f:
        rdr = csv.DictReader(f)
        for row in rdr:
            nutrient = d.get(row['Nutrient'])
            if not nutrient:
                print(f"Skipping unknown nutrient {row['Nutrient']} in comprehensive.csv")
                continue
            start, end = parse_age_range(row['Age_Group'])
            source_url = row.get('Source_URL', '').strip()
            notes = row.get('Nutrient_Notes', '').strip()
            data.append({
                'nutrient': nutrient,
                'gender': row['Gender'],
                'age_start_months': start,
                'age_end_months': end,
                'amount': row['Amount'],
                'unit': row['Unit'],
                'source_type': row.get('Source_Type', 'Comprehensive'),
                'source_name': row.get('Source_Name', 'Comprehensive Research'),
                'source_url': source_url,
                'notes': notes
            })
    return data

def load_complete(path):
    data = []
    with open(path, newline='') as f:
        rdr = csv.DictReader(f)
        for row in rdr:
            if row.get('male') in ['ND', 'CS']:
                continue
            for gender in ['male', 'female', 'pregnant', 'lactating']:
                amt = row.get(gender)
                if not amt:
                    continue
                nutrient = d.get(row['nutrient'])
                if not nutrient:
                    print(f"Skipping unknown nutrient {row['nutrient']} in complete.csv")
                    continue
                start, end = parse_age_range(row['age'])
                footnotes = row.get('footnotes', '')
                unit = ''
                if ' - ' in footnotes:
                    unit = footnotes.split(' - ')[1]
                data.append({
                    'nutrient': nutrient,
                    'gender': gender.capitalize(),
                    'age_start_months': start,
                    'age_end_months': end,
                    'amount': amt,
                    'unit': unit,
                    'source_type': 'Amateur AI calculation',
                    'source_name': 'Cognisa Ltd',
                    'source_url': '',
                    'notes': 'Amateur calculation'
                })
    return data


def load_enhanced(path):
    data = []
    with open(path, newline='') as f:
        rdr = csv.DictReader(f)
        for row in rdr:
            if row.get('Male') in ['ND', 'CS']:
                continue
            for gender in ['Male', 'Female', 'Pregnant', 'Lactating']:
                amt = row.get(gender)
                if not amt:
                    continue
                nutrient = d.get(row['Nutrient'])
                if not nutrient:
                    print(f"Skipping unknown nutrient {row['Nutrient']} in enhanced.csv")
                    continue
                start, end = parse_age_range(row['Age_Group'])
                url = row.get('Source_Links', '').strip()
                if 'ods.od.nih.gov' in url:
                    source_name = 'ODS NIH'
                elif 'who.int' in url:
                    source_name = 'WHO'
                else:
                    continue  # skip non-trusted enhanced sources
                notes_base = f"{row.get('Footnotes','')} {row.get('Nutrient_Notes','')}".strip()
                # Remove *AI only if a source URL is present (which it is here)
                notes_base = notes_base.replace('*AI', '').strip()
                data.append({
                    'nutrient': nutrient,
                    'gender': gender,
                    'age_start_months': start,
                    'age_end_months': end,
                    'amount': amt,
                    'unit': row.get('Unit', ''),
                    'source_type': 'Enhanced',
                    'source_name': source_name,
                    'source_url': url,
                    'notes': notes_base
                })
    return data


def merge_datasets(comprehensive, enhanced, complete):
    merged = OrderedDict()
    def key(rec):
        return (rec['nutrient'], rec['gender'], rec['age_start_months'], rec['age_end_months'])

    # Add comprehensive first
    for rec in comprehensive:
        merged[key(rec)] = rec

    # Add enhanced if not present (with credible source)
    for rec in enhanced:
        k = key(rec)
        if k not in merged:
            merged[k] = rec

    # Add complete last if not present
    for rec in complete:
        k = key(rec)
        if k not in merged:
            merged[k] = rec

    return list(merged.values())

def write_output(records, path='final_nutrients.csv'):
    fields = ['nutrient', 'gender', 'age_start_months', 'age_end_months', 'amount',
              'unit', 'source_type', 'source_name', 'source_url', 'notes']
    with open(path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for rec in records:
            writer.writerow(rec)

if __name__ == '__main__':
    comprehensive_data = load_comprehensive('comprehensive.csv')
    enhanced_data = load_enhanced('enhanced.csv')
    complete_data = load_complete('complete.csv')

    final_data = merge_datasets(comprehensive_data, enhanced_data, complete_data)
    write_output(final_data)
    print(f'Wrote {len(final_data)} records to final_nutrients.csv')
