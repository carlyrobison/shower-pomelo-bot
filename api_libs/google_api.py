from googleapiclient.discovery import build
from google.oauth2 import service_account
import settings as settings
import logging

logger = logging.getLogger(__name__)


# helper function
def extract_id_from_sheets_url(url):
    """
    Assumes `url` is of the form
    https://docs.google.com/spreadsheets/d/<ID>/edit...
    and returns the <ID> portion
    """
    start = url.find("/d/") + 3
    end = url.find("/edit")
    return url[start:end]

class GoogleDriveAPI:
    def __init__(self):
        if settings.GOOGLE_API_AUTHN_INFO is None:
            logger.warning("No google drive integration!")
        self._credentials = service_account.Credentials.from_service_account_info(
            settings.GOOGLE_API_AUTHN_INFO,
            scopes=settings.GOOGLE_DRIVE_PERMISSIONS_SCOPES,
        )

    def sheets_service(self):
        return build(
            "sheets", "v4", credentials=self._credentials, cache_discovery=False
        )

    def drive_service(self):
        return build(
            "drive", "v3", credentials=self._credentials, cache_discovery=False
        )

    def add_puzzle_link_to_sheet(self, puzzle_url, sheet_id):
        req_body = {
            "values": [
                [f'=HYPERLINK("{puzzle_url}", "Puzzle Link")'],
            ]
        }
        self.sheets_service().spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range="C1:C1",
            valueInputOption="USER_ENTERED",
            body=req_body,
        ).execute()

    def add_puzzle_title_to_sheet(self, puzzle_title, sheet_id):
        req_body = {
            "values": [
                [puzzle_title],
            ]
        }
        self.sheets_service().spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range="B1:B1",
            valueInputOption="USER_ENTERED",
            body=req_body,
        ).execute()

    # Make sheet with name and puzzle URL
    def make_sheet(self, name, puzzle_url=''):
        req_body = {"name": name}
        # copy template sheet
        file = self.drive_service().files().copy(
                fileId=settings.GOOGLE_SHEETS_TEMPLATE_FILE_ID,
                body=req_body,
                fields="id,webViewLink,permissions",
            ).execute()
        sheet_url = file["webViewLink"]

        self.add_puzzle_title_to_sheet(name, file["id"])
        if puzzle_url != '':
            self.add_puzzle_link_to_sheet(puzzle_url, file["id"])

        return sheet_url

    # Move sheet to SOLVED folder, mark it as solved, return the name of the puzzle
    def solve_sheet(self, sheet_url, answer):
        spreadsheet_id = extract_id_from_sheets_url(sheet_url)

        # Getting the existing title so we can prepend [SOLVED: answer] to it
        file = self.drive_service().files().get(
            fileId=spreadsheet_id,
            fields="name",
        ).execute()

        existing_title = file['name']
        new_title = '[SOLVED: {0}] {1}'.format(answer.upper(), existing_title)

        reqBody = {'name': new_title};
        # Set the title as solved and move it to the archives
        self.drive_service().files().update(
            fileId=spreadsheet_id,
            addParents=settings.GOOGLE_DRIVE_SOLVED_FOLDER_ID,
            body=reqBody,
            fields='id,parents,name'
            ).execute();
        return existing_title

# IGNORING CODE
# transfer new sheet ownership back to OG owner, so that scripts can run
# (bot runs just fine)
def transfer_ownership(file):
    permission = next(
        p for p in file["permissions"] if p["emailAddress"] == self._sheets_owner
    )
    self.drive_service().permissions().update(
        fileId=file["id"],
        permissionId=permission["id"],
        body={"role": "owner"},
        transferOwnership=True,
    ).execute()
