from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import os

def main():
    # טעינת ההרשאה שנוצרה בטסט הקודם
    creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/gmail.readonly'])

    # בניית שירות ה-Gmail
    service = build('gmail', 'v1', credentials=creds)

    # בקשת 5 המיילים האחרונים מהתיבת נכנס (INBOX)
    results = service.users().messages().list(userId='me', maxResults=5).execute()
    messages = results.get('messages', [])

    if not messages:
        print("לא נמצאו מיילים.")
    else:
        print("5 המיילים האחרונים שלך:")
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            print(f"- נושא: {msg['snippet']}")

if __name__ == '__main__':
    main()