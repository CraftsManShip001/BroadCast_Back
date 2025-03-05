from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

app = FastAPI()

origins = [
    "http://localhost:3001",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

# 필요한 스코프
SCOPES = [
    "https://www.googleapis.com/auth/forms.body", 
    "https://www.googleapis.com/auth/spreadsheets.readonly",
]

@app.get("/getCount")
async def get_supported_count():
    creds = None
    google_token = os.environ.get("GOOGLE_TOKEN")
    
    if google_token:
        creds = Credentials.from_authorized_user_info(info=json.loads(google_token))
    
    if not creds or not creds.valid:
        client_secrets_json = os.environ.get("GOOGLE_CLIENT_SECRETS")
        
        if client_secrets_json:
            client_secrets = json.loads(client_secrets_json)
            flow = InstalledAppFlow.from_client_config(client_secrets, SCOPES)
            creds = flow.run_local_server(port=8080)
            os.environ["GOOGLE_TOKEN"] = creds.to_json()
    
    sheet = build('sheets', 'v4', credentials=creds)

    # 엑셀 정보
    spreadsheet_id = '11yXA4KH58aSJBBFGspCnJ5O1gqfsPcDv46QQPc-b8HI'
    range_name = '방송부!A1:Z1000'

    # 데이터 커트
    result = sheet.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
    values = result.get('values', [])
    
    return {"count": len(values) - 4}
