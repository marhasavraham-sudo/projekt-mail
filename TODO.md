# רשימת משימות (TODO)

- [ ] **שלב א': תשתית**
    - [ ] הגדרת פרויקט ב-Google Cloud.
    - [ ] יצירת קובץ `requirements.txt` עם הספריות: `google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib`, `openai`.
    - [ ] כתיבת סקריפט `auth.py` לביצוע לוגין ושמירת ה-token.

- [ ] **שלב ב': Gmail API**
    - [ ] כתיבת פונקציה לשליפת המייל האחרון (או מיילים עם תווית ספציפית).
    - [ ] חילוץ גוף המייל (Body).

- [ ] **שלב ג': AI Parser**
    - [ ] יצירת פונקציה השולחת את גוף המייל ל-LLM.
    - [ ] הגדרת מבנה JSON לתוצר (Schema) לוודא תאימות.

- [ ] **שלב ד': Calendar API**
    - [ ] כתיבת פונקציה `check_availability(start_time, end_time)`.
    - [ ] כתיבת פונקציה `create_event(...)`.

- [ ] **שלב ה': אינטגרציה**
    - [ ] כתיבת סקריפט ראשי שמחבר הכל: (Fetch Mail -> Analyze -> Check Calendar -> Act).
    - [ ] הוספת שליחת מייל תשובה באמצעות Gmail API במידה ויש התנגשות.