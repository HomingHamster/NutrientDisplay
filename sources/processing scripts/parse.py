import re
import main
import csv

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

def check_range_containment(existing_ranges, query_range):
  start_q, end_q = query_range
  max_end = None
  for start, end in existing_ranges:
    if start <= start_q <= end:
      max_end = max(max_end if max_end is not None else 0, end)
    elif start_q < start <= end_q:
      max_end = max(max_end if max_end is not None else 0, end)
  if max_end is None or max_end < start_q:
    return query_range
  elif max_end >= end_q:
    return None
  else:
    return (max_end + 1, end_q)

f = open("sources/comprehensive.csv")
f = csv.DictReader(f)

for nutrient in f:
  r = r'[\W^ ^)^(]'
  a = main.models.Record(nutrient="-".join(re.split(r, nutrient["Nutrient"].strip())), age_months_start=parsetimee(nutrient["Age_Group"])[0], gender=nutrient["Gender"], amount=nutrient["Amount"], unit=nutrient["Unit"], source_type=nutrient["Source_Type"], source_name=nutrient["Source_Name"], source_url=nutrient["Source_URL"], nutrient_notes=nutrient["Nutrient_Notes"])
  if parsetimee(nutrient["Age_Group"])[1]:
    a.age_months_end = parsetimee(nutrient["Age_Group"])[1]
    a.save()

f = open("sources/enhanced.csv")
f = csv.DictReader(f)

for nutrient in f:
  r = r'[\W^ ^)^(]'
  if nutrient["Male"] == "CS" or nutrient["Male"] == "ND":
    continue
  for col in ["Male", "Female", "Pregnant", "Lactating"]:
    if not nutrient[col]:
      continue
    recs = main.models.Record.objects.filter(nutrient__icontains=nutrient["Nutrient"], gender__iexact=col).order_by("age_months_start")
    recs = [[x.age_months_start, x.age_months_end] for x in recs]
    out_range = check_range_containment(recs, parsetimee(nutrient["Age_Group"]))
    if out_range:
      a = main.models.Record(nutrient="-".join(re.split(r, nutrient["Nutrient"].strip())), age_months_start=out_range[0], age_months_end=out_range[1], gender=col, amount=nutrient[col], unit=nutrient["Unit"], source_type=nutrient["Source"], source_name=nutrient["Source_Links"], nutrient_notes=nutrient["Footnotes"] + ". " +nutrient["Nutrient_Notes"])
      a.save()

f = open("sources/complete.csv")
f = csv.DictReader(f)

for nutrient in f:
  r = r'[\W^ ^)^(]'
  if nutrient["male"] == "CS" or nutrient["male"] == "ND":
    continue
  for col in ["male", "female", "pregnant", "lactating"]:
    if not nutrient[col]:
      continue
    recs = main.models.Record.objects.filter(nutrient__icontains=nutrient["nutrient"], gender__iexact=col).order_by("age_months_start")
    recs = [[x.age_months_start, x.age_months_end] for x in recs]
    out_range = check_range_containment(recs, parsetimee(nutrient["age"]))
    if out_range:
      a = main.models.Record(nutrient="-".join(re.split(r, nutrient["nutrient"].strip())), age_months_start=out_range[0], age_months_end=out_range[1], gender=col.capitalize(), amount=nutrient[col], unit=nutrient["footnotes"].split(" - ")[1], source_type="Optimal Diet Analysis", source_name="Calculated from optimal diet pattern analysis", nutrient_notes="No good sources for amount required")
      a.save()