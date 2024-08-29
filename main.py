# import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# modifying these scopes, delete token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly", "https://www.googleapis.com/auth/spreadsheets"]

SAMPLE_SPREADSHEET_ID = "1hIsj_8-n0omPDvs56geXYKV44DtpciOIO7ePFExrnHQ"
SAMPLE_RANGE_NAME = "A2:c9"

UPCOMING = "https://devpost.com/hackathons?challenge_type[]=in-person&length[]=days&open_to[]=public&page=2&status[]=upcoming"
OPEN = "https://devpost.com/hackathons?challenge_type[]=in-person&length[]=days&open_to[]=public&status[]=open"

def scrapeUpcoming():
    # browser = webdriver.PhantomJS()
    # browser.get(UPCOMING)
    # html = browser.page_source
    # soup = BeautifulSoup(html, 'lxml')
    # a = soup.find('section', 'wrapper')
    # # r = requests.get(UPCOMING, timeout=5)

    # # print(r)

    # soup = BeautifulSoup(r.content, 'html.parser')

    # tiles = soup.find_all("div", class_="hackathon-tile")
    # print(tiles)
    # # print(soup.prettify())

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    chrome_driver_path = "/opt/homebrew/Caskroom/chromedriver/128.0.6613.86/chromedriver-mac-arm64/chromedriver"

    service = Service(chrome_driver_path)
    browser = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        browser.get(UPCOMING)
        html = browser.page_source
        soup = BeautifulSoup(html, 'lxml')
        
        # section = soup.find('div', class_='hackathons-container')
        # section = soup.find('div', class_='columns')
        section = soup.find('section', id='container')
        if section:
            tiles = section.find_all("div", class_="hackathon-tile")
            for tile in tiles:
                print(tile.text)
                location = tile.find("div", class_="info").text
                print(location)
                name = soup.find('div', class_='content').find('h3').text
                print(name)

        else:
            print("not found")

    except Exception as e:
        print(f"error: {e}")
    finally:
        browser.quit()

def writeText(creds, values):
    service = build("sheets", "v4", credentials=creds)
    sheet = service.spreadsheets()

    # values = [
    # ["Item", "Cost"],
    # ["Pen", "1.20"],
    # ["Notebook", "2.45"],
    # ["Eraser", "0.50"]
    # ]

    body = {
    "values": values
    }

    result = sheet.values().update(
    spreadsheetId=SAMPLE_SPREADSHEET_ID,
    range="A2",
    valueInputOption="RAW",  # or "USER_ENTERED" if to parse the values
    body=body
    ).execute()

    print(f"{result.get('updatedCells')}")
    
def readData(creds):
    service = build("sheets", "v4", credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = (
    sheet.values()
    .get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME)
    .execute()
    )
    values = result.get("values", [])

    if not values:
        print("No data found.")
        return


    for row in values:
        print(row)

def main():
  creds = None
  # credentials
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())


  try:
    # h = [["test", "1"], ["Pen", "1.20"], ["Notebook", "2.45"], ["Eraser", "0.50"]]
    # writeText(creds=creds, values=h)
    # readData(creds)
    scrapeUpcoming()
  except HttpError as err:
    print(err)



if __name__ == "__main__":
  main()

