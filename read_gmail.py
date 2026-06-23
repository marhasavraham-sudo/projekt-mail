import os
import time
import dateparser
import re
from datetime import datetime, timezone, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# הרשאות גישה (גם למייל וגם ליומן)
SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/calendar'
]

def get_service(api_name, version):
    creds = None
    token_file = f'token_{api_name}.json'
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open(token_file, 'w') as token:
            token.write(creds.to_json())
    return build(api_name, version, credentials=creds)

def parse_date_from_text(text):
    """חילוץ תאריך ושעה מתוך הטקסט בצורה גמישה"""
    # חיפוש תבנית של שעות (למשל 08:00-10:00)
    time_match = re.search(r'(\d{1,2}:\d{2})\s*[-–]\s*(\d{1,2}:\d{2})', text)
    if not time_match: return None, None
    
    start_time = time_match.group(1)
    end_time = time_match.group(2)
    
    # שימוש ב-dateparser למציאת תאריך בטקסט (למשל "24/06/2026")
    parsed_date = dateparser.parse(text, languages=['he', 'en'])
    if not parsed_date: return None, None
    
    start_dt = parsed_date.replace(hour=int(start_time.split(':')[0]), minute=int(start_time.split(':')[1]), second=0, tzinfo=timezone.utc)
    end_dt = parsed_date.replace(hour=int(end_time.split(':')[0]), minute=int(end_time.split(':')[1]), second=0, tzinfo=timezone.utc)
    
    return start_dt, end_dt

def check_conflict(cal_service, start, end):
    events = cal_service.events().list(
        calendarId='primary',
        timeMin=start.isoformat(),
        timeMax=end.isoformat(),
        singleEvents=True
    ).execute()
    return len(events.get('items', [])) > 0

def process_emails():
    print(f"--- הרצה: {datetime.now()} ---")
    gmail = get_service('gmail', 'v1')
    calendar = get_service('calendar', 'v3')
    
    # חיפוש מיילים שלא נקראו
    results = gmail.users().messages().list(userId='me', q='is:unread').execute()
    messages = results.get('messages', [])
    
    for msg in messages:
        full_msg = gmail.users().messages().get(userId='me', id=msg['id']).execute()
        snippet = full_msg['snippet']
        subject = next(h['value'] for h in full_msg['payload']['headers'] if h['name'] == 'Subject')
        
        print(f"בודק מייל: {subject}")
        
        start, end = parse_date_from_text(f"{subject} {snippet}")
        
        if start and end:
            if check_conflict(calendar, start, end):
                print("⚠️ נמצאה התנגשות בלו"ז! שולח מייל התראה...")
                # כאן אפשר להוסיף קוד לשליחת מייל חזרה
            else:
                print(f"✅ קובע פגישה: {subject}")
                event = {'summary': subject, 'start': {'dateTime': start.isoformat()}, 'end': {'dateTime': end.isoformat()}}
                calendar.events().insert(calendarId='primary', body=event).execute()
                # מסמן כמקרא (כדי לא לטפל שוב)
                gmail.users().messages().modify(userId='me', id=msg['id'], body={'removeLabelIds': ['UNREAD']}).execute()

while True:
    try:
        process_emails()
    except Exception as e:
        print(f"שגיאה בהרצה: {e}")
    print("מחכה 30 דקות...")
    time.sleep(1800)
