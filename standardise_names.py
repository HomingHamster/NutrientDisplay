
import re
import csv

data={}

def parsetimee(string):
  r = r'[\D]'
  if string == "Birth to 6 months" or string == "0<6 months":
    return (0, 6)
  elif string[-6:] == "months":
    return (int(re.split(r, string.split(" ")[0])[0]), int(re.split(r, string.split(" ")[0])[1]))
  elif string[-5:] == "years":
    if string.split(" ")[0][-1:] == "+":
      return (12*int(string.split(" ")[0][:-1]), 9999)
    else:
      return (12*int(re.split(r, string.split(" ")[0])[0]), 12*int(re.split(r, string.split(" ")[0])[1]))
  return "ERROR"

f = open("sources/comprehensive.csv")
f = csv.DictReader(f)

for nutrient in f:
  r = r'[\W^ ^)^(]'
  data["comprehensive"]=dict(nutrient="-".join(re.split(r, nutrient["Nutrient"].strip())), age_months_start=parsetimee(nutrient["Age_Group"])[0], gender=nutrient["Gender"], amount=nutrient["Amount"], unit=nutrient["Unit"], source_type=nutrient["Source_Type"], source_name=nutrient["Source_Name"], source_url=nutrient["Source_URL"], nutrient_notes=nutrient["Nutrient_Notes"])
  if parsetimee(nutrient["Age_Group"])[1]:
    data["comprehensive"]["age_months_end"] = parsetimee(nutrient["Age_Group"])[1]

f = open("sources/enhanced.csv")
f = csv.DictReader(f)

for nutrient in f:
  r = r'[\W^ ^)^(]'
  data["enhanced"]=[]
  if nutrient["Male"] == "CS" or nutrient["Male"] == "ND":
    continue
  for col in ["Male", "Female", "Pregnant", "Lactating"]:
    if not nutrient[col]:
      continue
    a=dict(nutrient="-".join(re.split(r, nutrient["Nutrient"].strip())), age_months_start=parsetimee(nutrient["Age_Group"])[0], gender=col, amount=nutrient[col], unit=nutrient["Unit"], source_type=nutrient["Source"], source_name=nutrient["Source_Links"], nutrient_notes=nutrient["Footnotes"] + ". " +nutrient["Nutrient_Notes"])
    if parsetimee(nutrient["Age_Group"])[1]:
      a["age_months_end"]=parsetimee(nutrient["Age_Group"])[1]
    data["enhanced"].append(a)

f = open("sources/complete.csv")
f = csv.DictReader(f)

for nutrient in f:
  r = r'[\W^ ^)^(]'
  data["complete"] = []
  if nutrient["male"] == "CS" or nutrient["male"] == "ND":
    continue
  for col in ["male", "female", "pregnant", "lactating"]:
    if not nutrient[col]:
      continue
    a=dict(nutrient="-".join(re.split(r, nutrient["nutrient"].strip())), age_months_start=parsetimee(nutrient["age"])[0], gender=col.capitalize(), amount=nutrient[col], unit=nutrient["footnotes"].split(" - ")[1], source_type="Optimal Diet Analysis", source_name="Calculated from optimal diet pattern analysis", nutrient_notes="No good sources for amount required")
    if parsetimee(nutrient["age"])[1]:
      a["age_months_end"]=parsetimee(nutrient["age"])[1]
    data["complete"].append(a)


from itertools import combinations
from ollama import Client
from time import sleep
from tenacity import retry, stop_after_attempt, wait_fixed
from typing import Dict, List, Set, Tuple

# Initialize Ollama client with default settings
client = Client(host='http://localhost:11434')


@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def safe_generate(prompt: str) -> bool:
  """Safe LLM query with retry logic"""
  response = client.generate(
    model='llama3',
    prompt=prompt,
    options={'temperature': 0.0}
  )
  return response['response'].strip().lower() == 'yes'


def process_datasets(dict_datasets: Dict[str, List[Dict]]) -> List[Dict]:
  """Main processing function for dataset comparison"""
  # Create name-to-datasets mapping
  name_datasets: Dict[str, Set[str]] = {}
  for dataset_name, records in dict_datasets.items():
    for record in records:
      name = record['name'].lower().strip()
      name_datasets.setdefault(name, set()).add(dataset_name)

  # Generate unique pairs with dataset origins
  all_names = list(name_datasets.keys())
  comparisons = [
    (n1, n2, name_datasets[n1], name_datasets[n2])
    for n1, n2 in combinations(set(all_names), 2)
  ]

  # Batch process comparisons
  results = []
  for name1, name2, ds1, ds2 in comparisons:
    prompt = (
      f"Are these two taxonomic names referring to the same species? "
      f"Respond only with 'Yes' or 'No'.\n"
      f"Name 1: {name1}\nName 2: {name2}"
    )

    try:
      is_match = safe_generate(prompt)
      results.append({
        'name1': name1,
        'name2': name2,
        'datasets1': list(ds1),
        'datasets2': list(ds2),
        'match': is_match
      })
      sleep(0.5)  # Rate limiting
    except Exception as e:
      print(f"Error comparing {name1} vs {name2}: {str(e)}")

  return results


# Example usage
if __name__ == "__main__":
  # Sample dataset structure
  example_data = {
    "a": [
      {"name": "Canis lupus familiaris"},
      {"name": "Felis catus"}
    ],
    "b": [
      {"name": "Felis silvestris catus"},
      {"name": "Canis familiaris"}
    ],
    "c": [
      {"name": "Felis catus"},
      {"name": "Canis lupus familiaris"}
    ]
  }

  # Process and display results
  comparisons = process_datasets(example_data)
  for comparison in comparisons:
    print(
      f"{comparison['name1']} ({', '.join(comparison['datasets1'])}) vs "
      f"{comparison['name2']} ({', '.join(comparison['datasets2'])}): "
      f"{'Match' if comparison['match'] else 'No match'}"
    )

