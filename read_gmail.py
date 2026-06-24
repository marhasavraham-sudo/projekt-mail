import os
import re
import dateparser
from datetime import datetime, timezone
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# --- הגדרות ---
# מחרוזת המייל לדוגמה (כפי שמופיע במייל שלך)
email_subject = "היי ברצוני לקבוע פגישה בתאריך 24/06/2026 בשעה 8:00-10:00 מהות הפגישה - 'סטטוס פרויקט מרה'ס'"

SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_service():
    """חיבור ליומן גוגל בעזרת הטוקן הקיים"""
    # מוודא שהטוקן קיים
    if not os.path.exists('token_calendar.json'):
        raise FileNotFoundError("לא נמצא קובץ token_calendar.json. הרץ את סקריפט החיבור מחדש.")
    
    creds = Credentials.from_authorized_user_file('token_calendar.json', SCOPES)
    return build('calendar', 'v3', credentials=creds)

def parse_meeting_time(text):
    """חילוץ תאריך ושעה בצורה מדויקת"""
    # 1. מציאת התאריך (פורמט: DD/MM/YYYY)
    date_match = re.search(r'(\d{1,2}[./]\d{1,2}[./]\d{4})', text)
    # 2. מציאת השעות (פורמט: HH:MM-HH:MM)
    time_match = re.search(r'(\d{1,2}:\d{2})\s*[-–]\s*(\d{1,2}:\d{2})', text)
    
    if date_match and time_match:
        date_str = date_match.group(1)
        start_time_str = time_match.group(1)
        end_time_str = time_match.group(2)
        
        # איחוד למחרוזת אחת ופיענוח ע"י dateparser
        full_date_start = f"{date_str} {start_time_str}"
        full_date_end = f"{date_str} {end_time_str}"
        
        start_dt = dateparser.parse(full_date_start)
        end_dt = dateparser.parse(full_date_end)
        
        # הגדרת אזור זמן UTC למניעת אזהרות
        return start_dt.replace(tzinfo=timezone.utc), end_dt.replace(tzinfo=timezone.utc)
    
    return None, None

def main():
    print("--- מנסה לפענח את המייל... ---")
    start, end = parse_meeting_time(email_subject)
    
    if not start or not end:
        print("❌ שגיאה: לא הצלחתי לפענח את התאריך או השעה מהטקסט.")
        return

    print(f"✅ הצלחה: נמצא תאריך {start.strftime('%d/%m/%Y')} בין {start.strftime('%H:%M')} ל-{end.strftime('%H:%M')}")
    
    # חיבור ליומן ויצירת אירוע
    try:
        service = get_service()
        event = {
            'summary': 'סטטוס פרויקט מרה"ס',
            'start': {'dateTime': start.isoformat()},
            'end': {'dateTime': end.isoformat()},
        }
        event = service.events().insert(calendarId='primary', body=event).execute()
        print(f"🎉 הפגישה נוספה ליומן! לינק: {event.get('htmlLink')}")
    except Exception as e:
        print(f"❌ שגיאה בחיבור ליומן: {e}")

if __name__ == '__main__':
    main()
