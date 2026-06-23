from google_auth_oauthlib.flow import InstalledAppFlow
import os

# ההרשאות שאנחנו צריכים
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_token():
    # פתיחת התהליך מול קובץ ה-credentials.json שלך
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    
    # הפעלת השרת המקומי כדי לקבל את האישור מהדפדפן
    creds = flow.run_local_server(port=0)

    # כאן אנחנו שומרים את הקובץ באופן ידני!
    with open('token.json', 'w') as token:
        token.write(creds.to_json())
    
    print("הצלחה! הקובץ token.json נוצר בהצלחה בתיקייה.")

if __name__ == '__main__':
    get_token()