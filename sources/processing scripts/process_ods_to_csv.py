"""Extract the tables from the folder structure"""
from pathlib import Path
from lxml import html
from sys import stdout
import re

path = Path("/home/ubuntu/diet/odsodnihgov/factsheets/ods.od.nih.gov/factsheets")
selector = path.glob('*-HealthProfessional/index.html')
file_list = list(selector)
print(file_list)

with open("csv.csv", "w") as f:
    f.write("vitamin,age,male,female,pregnant,lactating\n")
    for file in file_list:
        with open(file, "r") as fv:
            tree = html.fromstring(str(fv.read()))
            table = tree.xpath("//table[descendant::caption[contains(text(), 'RDAs') or contains(text(), 'AIs')]]")
            try:
                reg = html.tostring([x for x in table][0]).decode("utf8")
            except TypeError:
                continue
            except IndexError:
                continue
            nutrient = re.search(r"(?:\(RDAs\)|\(AIs\)) for (.*) \[", reg)[1]
            for row in table:
                row.xpath(".//tr")
                for tr in row:
                    tr.xpath(".//td/text()")
                    for td in tr:
                        tr = html.tostring(td).replace(b"&#8211;", b"-").replace(b"<br>\n			", b" ").replace(b"&gt;", b"").decode("utf8")
                        print(tr)
                        try:
                            age = re.search(r"<td scope=\"row\">(.*?)</td>", tr)[1]
                            reg = re.findall(r"<td align=\"right\">(.*)</td>", tr)
                            try:
                                male = reg[0].replace("&#160;", "").replace(",", "")
                                female = reg[1].replace("&#160;", "").replace(",", "")
                            except IndexError:
                                continue
                            try:
                                pregnant = reg[2].replace("&#160;", "").replace(",", "")
                                lactating = reg[3].replace("&#160;", "").replace(",", "")
                            except IndexError:
                                pass
                        except TypeError:
                            continue
                        f.write(f"{nutrient},{age},{male},{female},{pregnant},{lactating}\n")
