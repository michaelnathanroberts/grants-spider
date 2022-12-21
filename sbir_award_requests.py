import requests
import json


ITEM_KEYS = ['firm', 'award_title', 'agency', 'branch', 'phase', 'program', 'agency_tracking_number', 
             'contract', 'proposal_award_date', 'contract_end_date', 'solicitation_number', 'solicitation_year', 
             'topic_code', 'award_year', 'award_amount', 'duns', 'hubzone_owned', 'socially_economically_disadvantaged', 'women_owned', 'number_employees', 'company_url', 'address1', 'address2', 'city', 'state', 'zip', 'poc_name', 'poc_title', 'poc_phone', 'poc_email', 'pi_name', 'pi_title',
             'pi_phone', 'pi_email', 'ri_name', 'ri_poc_name', 'ri_poc_phone', 'abstract', 'award_link']
MAX_ROWS = 1000
NULL_JSON = {'ERROR': 'No record found.'}


awards = []
quit = False
i = 0

while not quit:
    r = requests.get("https://www.sbir.gov/api/awards.json", {"rows": 1000, "start": (1000 * i) + 1})
    dump = r.json()
    if dump == NULL_JSON:
        quit = True
    else:
        awards.extend(dump)
        i += 1
        print(i)

with open("tempdata.json", "wt", encoding="utf-8") as file:       
    json.dump(awards, file)

"""awards = None

import json
with open("tempdata.json", "rt", encoding="utf-8") as file:
    awards = json.load(file)"""
    
with open("awards.csv", "wt", encoding="utf-8") as file:
    print(",".join(ITEM_KEYS), file=file)
    for award in awards:
        if "cybersecurity" in award["award_title"].lower() or "cybersecurity" in award["abstract"].lower():
            s = ""
            for key in award.keys():
                value = award[key].replace("\"", "\"\"") if award[key] is not None else ""
                s = s + "\"" + value + "\"" + ","
            print(s, file=file)
        
# CLOSE awards.csv!
        

        

        


