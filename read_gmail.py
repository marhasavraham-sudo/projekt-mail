import time
import re
import dateparser
from datetime import datetime, timedelta
# יש להוסיף כאן את הייבואים של ה-API שכבר עובדים לך (googleapiclient וכו')

def parse_meeting_time(text):
    """מנסה למצוא תאריך ושעה בטקסט חופשי"""
    # חיפוש תבניות כמו 24/06/2026 או 24.06.26
    date_match = re.search(r'(\d{1,2}[./]\d{1,2}[./]\d{2,4})', text)
    # חיפוש טווח שעות כמו 08:00-10:00
    time_match = re.search(r'(\d{1,2}:\d{2})\s*[-–]\s*(\d{1,2}:\d{2})', text)
    
    if date_match and time_match:
        date_str = date_match.group(1)
        start_time_str = time_match.group(1)
        end_time_str = time_match.group(2)
        
        # המרה לאובייקט datetime
        start_dt = dateparser.parse(f"{date_str} {start_time_str}")
        end_dt = dateparser.parse(f"{date_str} {end_time_str}")
        return start_dt, end_dt
    return None, None

def check_calendar_conflict(service, start, end):
    """בודק אם יש פגישה בטווח הזמן הזה"""
    events_result = service.events().list(
        calendarId='primary', 
        timeMin=start.isoformat() + 'Z',
        timeMax=end.isoformat() + 'Z',
        singleEvents=True
    ).execute()
    return len(events_result.get('items', [])) > 0

def run_automation():
    print(f"--- הרצה: {datetime.now()} ---")
    # 1. קריאת מיילים (הלוגיקה שלך)
    # 2. ניתוח טקסט בעזרת parse_meeting_time
    # 3. אם מצאנו:
    #    if check_calendar_conflict(...):
    #        send_email("התנגשות בלו"ז! לא ניתן לקבוע את הפגישה.")
    #    else:
    #        create_calendar_event(...)
    pass

# לולאה שרצה כל 30 דקות
while True:
    try:
        run_automation()
    except Exception as e:
        print(f"שגיאה: {e}")
    
    print("מחכה 30 דקות להרצה הבאה...")
    time.sleep(1800) # 1800 שניות = 30 דקות
