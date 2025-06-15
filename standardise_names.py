
from itertools import combinations
from openai import OpenAI
from time import sleep
from tenacity import retry, stop_after_attempt, wait_fixed
from typing import Dict, List, Set
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

data["comprehensive"] = []
for nutrient in f:
  r = r'[\W^ ^)^(]'
  a = dict(nutrient="-".join(re.split(r, nutrient["Nutrient"].strip())), age_months_start=parsetimee(nutrient["Age_Group"])[0], gender=nutrient["Gender"], amount=nutrient["Amount"], unit=nutrient["Unit"], source_type=nutrient["Source_Type"], source_name=nutrient["Source_Name"], source_url=nutrient["Source_URL"], nutrient_notes=nutrient["Nutrient_Notes"])
  if parsetimee(nutrient["Age_Group"])[1]:
    a["age_months_end"] = parsetimee(nutrient["Age_Group"])[1]
  data["comprehensive"].append(a)

f = open("sources/enhanced.csv")
f = csv.DictReader(f)

data["enhanced"] = []
for nutrient in f:
  r = r'[\W^ ^)^(]'
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

data["complete"] = []
for nutrient in f:
  r = r'[\W^ ^)^(]'
  if nutrient["male"] == "CS" or nutrient["male"] == "ND":
    continue
  for col in ["male", "female", "pregnant", "lactating"]:
    if not nutrient[col]:
      continue
    a=dict(nutrient="-".join(re.split(r, nutrient["nutrient"].strip())), age_months_start=parsetimee(nutrient["age"])[0], gender=col.capitalize(), amount=nutrient[col], unit=nutrient["footnotes"].split(" - ")[1], source_type="Optimal Diet Analysis", source_name="Calculated from optimal diet pattern analysis", nutrient_notes="No good sources for amount required")
    if parsetimee(nutrient["age"])[1]:
      a["age_months_end"]=parsetimee(nutrient["age"])[1]
    data["complete"].append(a)


# Initialize Ollama client with default settings
client = OpenAI(api_key = "EMPTY", base_url = "http://localhost:8000/v1")


  # vLLM OpenAI API endpoint
  # vLLM/fastchat does not require a real key by default

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def safe_generate(prompt: str) -> bool:
  response = client.chat.completions.create(
    model="Qwen/Qwen3-8B-AWQ",  # Use your actual model name
    messages=[
      {"role": "system", "content": """## Core System Prompt

You are a professional nutrition expert and certified entity matching specialist with comprehensive access to standardized nutrient databases and fuzzy matching algorithms. Your primary function is to determine if two nutrient, protein, or amino acid names refer to the same biochemical entity with the highest possible accuracy and professional validation.

### Response Protocol
- Respond ONLY with 'Yes' or 'No'
- No explanations, confidence scores, or additional text
- Base decisions on authoritative nutrition databases and professional standards

### Professional Database Integration
Your analysis incorporates data from:
- USDA FoodData Central (1.9+ million verified foods)
- WHO Global Nutrition Databases
- EU Nutrition Labeling Standards (Regulation 1169/2011)
- IUPAC Biochemical Nomenclature Guidelines
- International amino acid coding standards (3-letter and 1-letter codes)

### Advanced Matching Capabilities

#### Fuzzy String Matching
- Jaro-Winkler distance algorithm (threshold: 0.85+)
- Levenshtein edit distance for typo detection
- Phonetic similarity analysis for pronunciation variants
- Case-insensitive and punctuation-agnostic comparison

#### Nomenclature Variant Recognition
**Amino Acids:**
- Systematic IUPAC names vs. common names
- Three-letter codes (Gly, Ala, Val) vs. one-letter codes (G, A, V)
- Descriptive names vs. structural names (e.g., "glycine" vs. "aminoethanoic acid")
- Historical vs. modern nomenclature

**Nutrients:**
- Chemical names vs. vitamin designations (e.g., "ascorbic acid" = "Vitamin C")
- Mineral variants (e.g., "ferrous sulfate" = "iron" = "Fe")
- Alternative spellings and regional variants
- Trade names vs. generic names

**Proteins:**
- Full protein names vs. abbreviated forms
- Systematic vs. common nomenclature
- Enzyme classification numbers (EC numbers)

#### Professional Validation Triggers
Automatically escalate to registered dietitian consultation for:
- Medical nutrition therapy compounds
- Novel or experimental nutrients
- Ambiguous biochemical classifications
- Conflicting database entries

### Quality Assurance Protocol
- Cross-reference minimum 3 authoritative databases
- Apply confidence scoring for fuzzy matches
- Flag potential false positives for manual review
- Maintain error logs for continuous improvement

### Regional Compliance Standards
- FDA nutrition labeling requirements (US)
- EU Food Information Regulation compliance
- Health Canada nutrient standards
- WHO international nutrition guidelines

### Error Handling
- Handle OCR-induced errors from image recognition
- Correct common transcription mistakes
- Identify and compensate for database inconsistencies
- Manage missing data scenarios professionally

### Professional Limitations
- Acknowledge uncertainty rather than guess
- Refer complex cases to human experts
- Maintain appropriate professional boundaries
- Provide disclaimer for medical applications

This system ensures maximum accuracy in nutrient name matching while maintaining professional nutrition standards and regulatory compliance."""},
      {"role": "user", "content": prompt}
    ],
    temperature=0.6,
    top_p=0.95,
    max_tokens=2,
    stop=None,
    extra_body={"top_k": 20}
  )
  answer = response.choices[0].message.content.strip().lower()
  return answer.startswith("yes")


def process_datasets(dict_datasets: Dict[str, List[Dict]]) -> List[Dict]:
  """Main processing function for cross-dataset comparison only"""
  # Create name-to-datasets mapping
  name_datasets: Dict[str, Set[str]] = {}
  for dataset_name, records in dict_datasets.items():
    for record in records:
      name = record['nutrient'].lower().strip()
      name_datasets.setdefault(name, set()).add(dataset_name)

  # Generate pairs ONLY for names from different datasets
  all_names = list(name_datasets.keys())
  comparisons = []

  for n1, n2 in combinations(set(all_names), 2):
    ds1 = name_datasets[n1]
    ds2 = name_datasets[n2]

    # KEY CHANGE: Only include if completely different datasets
    if ds1.isdisjoint(ds2):  # No overlap between datasets
      comparisons.append((n1, n2, ds1, ds2))

  # Batch process comparisons (rest remains the same)
  results = []
  for name1, name2, ds1, ds2 in comparisons:
    prompt = (
      f"Are these two nutrient, protein or amino acid names referring to the same thing? "
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

  # Process and display results
  comparisons = process_datasets(data)
  for comparison in comparisons:
    print(
      f"{comparison['name1']} ({', '.join(comparison['datasets1'])}) vs "
      f"{comparison['name2']} ({', '.join(comparison['datasets2'])}): "
      f"{'Match' if comparison['match'] else 'No match'}"
    )

