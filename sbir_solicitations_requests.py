import requests
import pandas
import json
import csv


ITEM_KEYS = ['solicitation_title', 'solicitation_number', 'program', 'phase', 'agency', 'branch',
             'solicitation_year', 'release_date', 'open_date', 'close_date', 'application_due_date',
             'occurrence_number', 'sbir_solicitation_link', 'solicitation_agency_url', 'current_status',
             'solicitation_topics'] 

    
MAX_ROWS = 1000
NULL_JSON = {'ERROR': 'No record found.'}


"""solicitations = []
quit = False
i = 0

while not quit:
    r = requests.get("https://www.sbir.gov/api/solicitations.json", {"rows": 1000, "start": (1000 * i) + 1, "open": 1})
    dump = r.json()
    if dump == NULL_JSON:
        quit = True
    else:
        solicitations.extend(dump)
        i += 1
        print(i)
        
        
with open("tempdatasolicit.json", "wt", encoding="utf-8") as file:
    s = json.dump(solicitations, file)"""

solicitations = []
with open("tempdatasolicit.json", "rt", encoding="utf-8") as file:
    solicitations = json.load(file)


with open("solicitations.csv", "wt", encoding="utf-8") as file:
    print(",".join(ITEM_KEYS), file=file)
    for solicitation in solicitations:
        if solicitation["agency"] == "Department of Health and Human Services":
            continue
        s = ""
        for key in solicitation.keys():
            value = solicitation[key]
            if isinstance(value, str) or value is None:
                print("\"" + (value.replace("\"", "\"\"") if solicitation[key] is not None else "") + "\"",
                      end=",", file=file)
            elif key == "application_due_date":
                print("\"" + (" | ".join(value)) + "\"",
                      end=",", file=file)                
            elif key == "solicitation_topics":
                if len(solicitation[key]) > 1:
                    print(solicitation["solicitation_title"])
                for topic in solicitation[key]:
                    print("\"" + topic["topic_title"] + "\"",
                      end=",", file=file)
        file.write("\n")
        

# CLOSE solicitations.csv!
