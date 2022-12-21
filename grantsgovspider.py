import bs4
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
import time
import re

HEADERS = [
    "Document Type", "Funding Opportunity Number", "Funding Opportunity Title", "Opportunity Category",
    "Opportunity Category Explanation", "Funding Instrument Type", "Category of Funding Activity",
    "Category Explanation", "Expected Number of Awards", "CFDA Number(s)", "Cost Sharing or Matching Requirement",
    "Version", "Posted Date", "Last Updated Date", "Original Closing Date for Applications",
    "Current Closing Date for Applications", "Archive Date", "Estimated Total Program Funding",
    "Award Ceiling", "Award Floor", "Eligible Applicants", "Additional Information on Eligibility",
    "Agency Name", "Description", "Link to Additional Information", "Grantor Contact Information"
]

ADDITIONAL_INFO_LINK_INDEX = 2
PSEUDO_A_ORD = 194

counter = 0


def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext


def ordered_rows(even_rows, odd_rows):
    global counter
    for k in range(len(even_rows)):
        yield even_rows[k]
        counter += 1
        print("Grant", counter)
        try:
            yield odd_rows[k]
        except IndexError:
            break  # Completely normal
        else:
            counter += 1
            print("Grant", counter)


service = ChromeService(ChromeDriverManager().install())
with webdriver.Chrome(service=service) as driver, \
        open("grants.csv", "wt", encoding="utf-8") as file:
    print(*HEADERS, sep=",", file=file)

    for page in range(1, 1000):
        driver.get("https://www.grants.gov/custom/search.jsp")
        time.sleep(3)

        individualsCheckbox = driver.find_element(By.XPATH, '//*[@id="21"]')
        smallBusinessCheckbox = driver.find_element(By.XPATH, '//*[@id="23"]')
        individualsCheckbox.click()
        smallBusinessCheckbox.click()

        # categoryDiv = driver.find_element(By.ID, "categoryDiv")
        # checkboxes = bs4.BeautifulSoup(categoryDiv.text, features='lxml').findAll('input')
        # print(checkboxes)
        # break
        print("Page", page)
        driver.execute_script(f"pageSearchResults({page})")
        time.sleep(3)

        soup = bs4.BeautifulSoup(driver.page_source, features="lxml")
        searchResultsDiv: bs4.Tag = soup.find(id='searchResultsDiv')
        even_rows: list[bs4.Tag] = searchResultsDiv.findAll("tr", {"class": "gridevenrow"})
        odd_rows: list[bs4.Tag] = searchResultsDiv.findAll("tr", {"class": "gridoddrow"})

        # If we have no even rows, there are no more results. Break
        if len(even_rows) == 0:
            break

        for row in ordered_rows(even_rows, odd_rows):
            page_link = row.find("a", {"title": "Click to View Grant Opportunity"})
            opp_id = int(str(page_link).split("(")[1].split(",")[0])
            driver.get(f"https://www.grants.gov/custom/viewOppDetails.jsp?oppId={opp_id}")
            time.sleep(3)
            grant_soup = bs4.BeautifulSoup(driver.page_source, features="lxml")

            tablePrefix = "synopsis"
            try:
                grant_soup.find("div", id="synopsisDetailsGeneralInfoTableLeft").contents[0]
            except IndexError:
                tablePrefix = "forecast"

            infoLeftDiv: bs4.Tag = grant_soup.find("div", id=(tablePrefix + "DetailsGeneralInfoTableLeft"))
            try:
                infoLeftTable: bs4.Tag = infoLeftDiv.contents[0]
            except IndexError:
                print("Problem OpID: ", opp_id)
                continue
            values: list[bs4.Tag] = infoLeftTable.findAll("span", {"class": "search-custom"})
            j = 0
            while j < len(values):
                value = values[j]
                if value.parent.name == "span":
                    values.pop(j - 1)
                else:
                    j += 1
            for i in range(len(values)):
                valueText = "\"" + values[i].text.replace("\"", "\"\"").replace(chr(PSEUDO_A_ORD), "") + "\""
                print(valueText, end=",", file=file)

            infoRightDiv: [bs4.Tag] = grant_soup.find("div", id=(tablePrefix + "DetailsGeneralInfoTableRight"))
            infoRightTable = infoRightDiv.contents[0]
            values: list[bs4.Tag] = infoRightTable.findAll("span", {"class": "search-custom"})
            j = 0
            while j < len(values):
                value = values[j]
                if value.parent.name == "span":
                    values.pop(j - 1)
                else:
                    j += 1
            for i in range(len(values)):
                valueText = "\"" + values[i].text.replace("\"", "\"\"").replace(chr(PSEUDO_A_ORD), "") + "\""
                print(valueText, end=",", file=file)

            eligibilityDiv: [bs4.Tag] = grant_soup.find("div", id=(tablePrefix + "DetailsEligibilityTable"))
            eligibilityTable = eligibilityDiv.contents[0]
            values: list[bs4.Tag] = eligibilityTable.findAll("span", {"class": "search-custom"})
            j = 0
            while j < len(values):
                value = values[j]
                if value.parent.name == "span":
                    values.pop(j - 1)
                else:
                    j += 1
            for i in range(len(values)):
                valueText = "\"" + values[i].text.replace("\"", "\"\"").replace(chr(PSEUDO_A_ORD), "") + "\""
                print(valueText, end=",", file=file)

            additionalInfoDiv: [bs4.Tag] = grant_soup.find("div", id=(tablePrefix + "DetailsAdditionalInfoTable"))
            additionalInfoTable = additionalInfoDiv.contents[0]
            values: list[bs4.Tag] = additionalInfoTable.findAll("span", {"class": "search-custom"})
            j = 0
            while j < len(values):
                value = values[j]
                if value.parent.name == "span":
                    values.pop(j - 1)
                else:
                    j += 1
            for i in range(len(values)):
                if i == ADDITIONAL_INFO_LINK_INDEX:
                    linkHtml = values[ADDITIONAL_INFO_LINK_INDEX].find("a")
                    link = ""
                    if linkHtml is not None:
                        link = linkHtml.attrs["href"].replace("\"", "\"\"")
                    print("\"" + link + "\"", file=file, end=",")
                else:
                    valueText = "\"" + values[i].text.replace("\"", "\"\"").replace(chr(PSEUDO_A_ORD), "") + "\""
                    valueText = cleanhtml(valueText)
                    print(valueText, file=file, end=",")

            print("\n", end="", file=file)
        print("\n", end="", file=file)
        break
