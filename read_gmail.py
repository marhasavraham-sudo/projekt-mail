import os
import time
import re
import dateparser
from datetime import datetime, timezone
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# --- הגדרות ---
SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/calendar'
]
TOKEN_FILE = 'token.json'
CREDENTIALS_FILE = 'credentials.json'

def get_service(api_name, version):
    """פונקציה גנרית להתחברות ל-API של גוגל"""
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    
    return build(api_name, version, credentials=creds)

def parse_meeting_time(text):
    """חילוץ תאריך ושעה מתוך טקסט"""
    date_match = re.search(r'(\d{1,2}[./]\d{1,2}[./]\d{4})', text)
    time_match = re.search(r'(\d{1,2}:\d{2})\s*[-–]\s*(\d{1,2}:\d{2})', text)
    
    if date_match and time_match:
        date_str = date_match.group(1)
        start_time_str = time_match.group(1)
        end_time_str = time_match.group(2)
        
        full_date_start = f"{date_str} {start_time_str}"
        full_date_end = f"{date_str} {end_time_str}"
        
        start_dt = dateparser.parse(full_date_start)
        end_dt = dateparser.parse(full_date_end)
        
        if start_dt and end_dt:
            return start_dt.replace(tzinfo=timezone.utc), end_dt.replace(tzinfo=timezone.utc)
    return None, None

def check_calendar_conflict(cal_service, start, end):
    """בדיקה אם קיימת פגישה בטווח הזמן הזה"""
    events_result = cal_service.events().list(
        calendarId='primary',
        timeMin=start.isoformat(),
        timeMax=end.isoformat(),
        singleEvents=True
    ).execute()
    return len(events_result.get('items', [])) > 0

def run_bot():
    print(f"--- הרצה: {datetime.now().strftime('%H:%M:%S')} ---")
    
    try:
        gmail_service = get_service('gmail', 'v1')
        cal_service = get_service('calendar', 'v3')
        
        # קריאת מיילים שלא נקראו
        results = gmail_service.users().messages().list(userId='me', q='is:unread').execute()
        messages = results.get('messages', [])
        
        if not messages:
            print("אין מיילים חדשים לטיפול.")
            return

        for msg in messages:
            full_msg = gmail_service.users().messages().get(userId='me', id=msg['id']).execute()
            subject = next((h['value'] for h in full_msg['payload']['headers'] if h['name'] == 'Subject'), "No Subject")
            snippet = full_msg['snippet']
            text_to_parse = f"{subject} {snippet}"
            
            print(f"בודק מייל: {subject}")
            
            start, end = parse_meeting_time(text_to_parse)
            
            if start and end:
                if check_calendar_conflict(cal_service, start, end):
                    print(f"⚠️ התנגשות נמצאה עבור: {subject}")
                    # כאן אפשר להוסיף שליחת מייל התראה במידת הצורך
                else:
                    event = {
                        'summary': subject,
                        'start': {'dateTime': start.isoformat()},
                        'end': {'dateTime': end.isoformat()},
                    }
                    cal_service.events().insert(calendarId='primary', body=event).execute()
                    print(f"✅ הפגישה '{subject}' נוצרה בהצלחה!")
                    
                    # הסרת התווית UNREAD כדי שלא יטופל שוב
                    gmail_service.users().messages().modify(userId='me', id=msg['id'], body={'removeLabelIds': ['UNREAD']}).execute()
            else:
                print("לא נמצא זימון במייל זה.")
                
    except Exception as e:
        print(f"שגיאה בהרצה: {e}")

# לולאת הרצה כל 30 דקות
if __name__ == '__main__':
    while True:
        run_bot()
        print("ממתין 30 דקות להרצה הבאה...")
        time.sleep(1800)
