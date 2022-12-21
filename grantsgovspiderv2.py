from selenium.webdriver import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver

import bs4
import datetime
import requests
import os
import pandas as pd
import shutil
import time
import zipfile

OPPORTUNITY_CATEGORY_CODES = {
    'D': "Discretionary",
    'M': "Mandatory",
    'C': "Continuation",
    'E': "Earmark",
    'O': "Other"
}

FUNDING_INSTRUMENT_TYPE_CODES = {
    'G': 'Grant',
    'CA': 'Cooperative Agreement',
    'O': 'Other',
    'PC': 'Procurement Contract'
}

FUNDING_ACTIVITY_CATEGORY_CODES = {
    'ACA': 'Affordable Care Act',
    'AG': 'Agriculture',
    'AR': 'Arts (see "Cultural Affairs" in CFDA)',
    'BC': 'Business and Commerce',
    'CD': 'Community Development',
    'CP': 'Consumer Protection',
    'DPR': 'Disaster Prevention and Relief',
    'ED': 'Education',
    'ELT': 'Employment, Labor and Training',
    'EN': 'Energy',
    'ENV': 'Environment',
    'FN': 'Food and Nutrition',
    'HL': 'Health',
    'HO': 'Housing',
    'HU': 'Humanities (see "Cultural Affairs" in CFDA)',
    'ISS': 'Income Security and Social Services',
    'IS': 'Information and Statistics',
    'LJL': 'Law, Justice and Legal Services',
    'NR': 'Natural Resources',
    'RA': 'Recovery Act',
    'RD': 'Regional Development',
    'ST': 'Science and Technology and other Research and Development',
    'T': 'Transportation',
    'O': 'Other (see text field entitled "Explanation of Other Category of Funding Activity" for clarification)'
}

ELIGIBILITY_CODES = {
    0: 'State governments',
    1: 'County governments',
    2: 'City or township governments',
    4: 'Special district governments',
    5: 'Independent school districts',
    6: 'Public and State controlled institutions of higher education',
    7: 'Native American tribal governments (Federally recognized)',
    8: 'Public housing authorities/Indian housing authorities',
    11: 'Native American tribal organizations (other than Federally recognized tribal governments)',
    12: 'Nonprofits having a 501 (c) (3) status with the IRS, other than institutions of higher education',
    13: 'Nonprofits that do not have a 501 (c) (3) status with the IRS, other than institutions of higher education',
    20: 'Private institutions of higher education',
    21: 'Individuals',
    22: 'For-profit organizations other than small businesses',
    23: 'Small businesses',
    25: 'Others (see text field entitled \"Additional Information on Eligibility\" for clarification.)',
    99: 'Unrestricted (i.e., open to any type of entity below), ' +
        'subject to any clarification in text field entitled \"Additional Information on Eligibility\"'
}

UNNECESSARY_COLUMNS = [
    'OpportunityID',
    'Version',
    'ArchiveDate',
    'CloseDateExplanation',
    'OpportunityCategoryExplanation',
    'EstimatedSynopsisPostDate',
    'FiscalYear',
    'EstimatedSynopsisCloseDate',
    'EstimatedSynopsisCloseDateExplanation',
    'EstimatedAwardDate',
    'EstimatedProjectStartDate',
]

# For Windows
SEPERATOR = "\\"

# For Mac
# SEPERATOR = "/"

ONE_DAY = datetime.timedelta(days=1)


def to_yyyymmdd(date: datetime.date):
    return date.isoformat().replace("-", "")


def get_optimal_date(web_driver: webdriver.Chrome, date: datetime.date = datetime.date.today()):
    web_driver.get("about:blank")
    time.sleep(1)
    web_driver.get(f"https://www.grants.gov/extract/GrantsDBExtract{to_yyyymmdd(date)}v2.zip")
    time.sleep(2)
    soup = bs4.BeautifulSoup(web_driver.page_source, features="lxml")
    tag = soup.find("h1")
    if isinstance(tag, bs4.element.PageElement) and "Not Found" in tag.text:
        yesterday = date - ONE_DAY
        return get_optimal_date(web_driver, yesterday)
    return date


service = ChromeService(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
dateString = to_yyyymmdd(get_optimal_date(driver, datetime.date(2022, 7, 14)))

CURRENT_DIR = os.getcwd()
DOWNLOADS = SEPERATOR.join(CURRENT_DIR.split(SEPERATOR)[0:3]) + SEPERATOR + "Downloads"
ZIPPED_PATH = DOWNLOADS + SEPERATOR + f"GrantsDBExtract{dateString}v2.zip"
XML_FILE_NAME = f"GrantsDBExtract{dateString}v2.xml"
CSV_FILE_NAME = "grants.csv"
DOWNLOAD_SECONDS = 240

time.sleep(DOWNLOAD_SECONDS)

with zipfile.ZipFile(ZIPPED_PATH, "r") as zippedFile:
    zippedFile.extractall(CURRENT_DIR)

df = pd.read_xml(XML_FILE_NAME)

for column in ["OpportunityCategory", "FundingInstrumentType", "CategoryOfFundingActivity"]:
    code_dict = {}
    if column == "OpportunityCategory":
        code_dict = OPPORTUNITY_CATEGORY_CODES
    elif column == "FundingInstrumentType":
        code_dict = FUNDING_INSTRUMENT_TYPE_CODES
    elif column == "CategoryOfFundingActivity":
        code_dict = FUNDING_ACTIVITY_CATEGORY_CODES
    for i in range(len(df)):
        value = df.at[i, column]
        if value in code_dict.keys():
            df.at[i, column] = code_dict[value]

for j in range(len(df)):
    try:
        value = int(df.at[j, "EligibleApplicants"])
        if value in ELIGIBILITY_CODES:
            df.at[j, "EligibleApplicants"] = ELIGIBILITY_CODES[value]
    except ValueError:
        # Data on eligibility missing, no big deal
        pass

for column in ["PostDate", "CloseDate", "LastUpdatedDate", "ArchiveDate", "EstimatedSynopsisPostDate"]:
    for k in range(len(df)):
        value = df.at[k, column]

        month = day = year = 0
        if value is None:
            continue
        try:
            value = int(value)
        except ValueError:
            continue
        value, year = divmod(value, 10_000)
        month, day = divmod(value, 100)
        df.at[k, column] = str(datetime.date(year, month, day))

df: pd.DataFrame = df.drop(UNNECESSARY_COLUMNS, axis=1)
df.to_csv(CSV_FILE_NAME, index=False)
