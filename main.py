import requests
from bs4 import BeautifulSoup
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# modifying these scopes, delete token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly", "https://www.googleapis.com/auth/spreadsheets"]

SAMPLE_SPREADSHEET_ID = "1hIsj_8-n0omPDvs56geXYKV44DtpciOIO7ePFExrnHQ"
SAMPLE_RANGE_NAME = "A1:Z1"

UPCOMING = "https://devpost.com/hackathons?challenge_type[]=in-person&length[]=days&open_to[]=public&page=2&status[]=upcoming"
OPEN = "https://devpost.com/hackathons?challenge_type[]=in-person&length[]=days&open_to[]=public&status[]=open"

def scrapeUpcoming():
    try:
        response = requests.get(UPCOMING, timeout=20)
        response.raise_for_status() 

        soup = BeautifulSoup(response.text, "html.parser")

        # section = soup.find("section", id="container")
        # section = soup.find("div", id="hackathon-search")


        hackathon_tiles = soup.select('#container #hackathon-search .is-desktop .hackathons-container .hackathon-tile')
        # print(soup.prettify())

        print(f"Found {len(hackathon_tiles)} hackathon tiles")

        for tile in hackathon_tiles:
            link = tile.find('a', class_='tile-anchor')['href'] if tile.find('a', class_='tile-anchor') else None

            main_content = tile.find('div', class_='main-content').text.strip() if tile.find('div', class_='main-content') else None
            
            print("Hackathon Link:", link)
            print("Main Content:", main_content)
            print('-' * 40)


        main_contents = soup.find_all("div", class_="hackathon-tile")

        # print(section)
        print(main_contents)




        # if not section:
        #     print("No hackathons section found on the page.")
        #     return []

        tiles = soup.find_all("div", class_="hackathon-tile")
        hackathons = []
        for tile in tiles:
            try:
                name = tile.find("div", class_="content").find("h3").text.strip()
                start_date = tile.find("div", class_="start-date").text.strip()
                end_date = tile.find("div", class_="end-date").text.strip()
                status = tile.find("div", class_="status").text.strip()
                apps_open = tile.find("div", class_="apps-open").text.strip()
                apps_close = tile.find("div", class_="apps-close").text.strip()
                participants = tile.find("div", class_="participants").text.strip()
                prizes = tile.find("div", class_="prizes").text.strip()
                
                hackathons.append([name, start_date, end_date, status, apps_open, apps_close, participants, prizes])
            except AttributeError:
                print("Incomplete hackathon data in one tile. Skipping.")
        return hackathons
    except requests.RequestException as e:
        print(f"An error occurred while fetching the webpage: {e}")
        return []


def check_and_create_columns(creds):
    service = build("sheets", "v4", credentials=creds)
    sheet = service.spreadsheets()

    # Get first row
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME).execute()
    current_headers = result.get("values", [])[0] if result.get("values") else []

    required_headers = ["Name", "Start date", "End date", "Status", "Apps open", "Apps close", "participants", "prizes"]
    for header in required_headers:
        if header not in current_headers:
            current_headers.append(header)


    body = {"values": [current_headers]}
    sheet.values().update(
        spreadsheetId=SAMPLE_SPREADSHEET_ID,
        range="A1",
        valueInputOption="RAW",
        body=body
    ).execute()
    return current_headers


def write_data_to_sheet(creds, data):
    service = build("sheets", "v4", credentials=creds)
    sheet = service.spreadsheets()

    body = {
        "values": data
    }

    result = sheet.values().update(
        spreadsheetId=SAMPLE_SPREADSHEET_ID,
        range="A2", # Start from row 2
        valueInputOption="RAW",
        body=body
    ).execute()

    print(f"{result.get('updatedCells')} cells updated.")


def readData(creds):
    service = build("sheets", "v4", credentials=creds)

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
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        hackathons = scrapeUpcoming()
        if hackathons:
            check_and_create_columns(creds)
            write_data_to_sheet(creds, hackathons)
        else:
            print("No hackathons to add.")
    except HttpError as err:
        print(err)


if __name__ == "__main__":
    main()
