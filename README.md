# שרת תמלול אודיו בעברית

שרת Python המיועד לתמלול אודיו בעברית, הפועל כסוכן חכם המקבל קבצי אודיו, מתמלל אותם, ומחזיר תוצאות בפורמט JSON.

## מאפיינים

- שרת Python מבוסס FastAPI שמאזין בפורט 8000
- תמלול באמצעות faster-whisper עם המודל ivrit-ai/faster-whisper-v2-d4
- זיהוי דוברים שונים לפי הפסקות בדיבור וסימנים לשוניים
- תמיכה בכל סוגי קבצי האודיו הנפוצים (MP3, WAV, OGG, M4A)
- הגדרת CORS נכונה לאפשר גישה מהקליינט
- תיקוף קבצי קלט למניעת העלאת קבצים מסוכנים

## התקנה מקומית

### דרישות מקדימות

- Python 3.10 ומעלה
- FFmpeg מותקן במערכת

### שלבי התקנה

1. שכפול המאגר:
bash
git clone https://github.com/your-username/hebrew-transcription-server.git
cd hebrew-transcription-server


2. יצירת סביבה וירטואלית והתקנת תלויות:
bash
python -m venv venv
source venv/bin/activate # בלינוקס/מק
או
venv\Scripts\activate # בווינדוס
pip install -r requirements.txt


3. יצירת קובץ הגדרות סביבה:
bash
cp .env.example .env
ערוך את הקובץ .env לפי הצורך


4. הפעלת השרת:
bash
uvicorn main:app --reload
בכתובת http://localhost:8000

## תיעוד API

### נקודות קצה

#### `GET /`

בדיקת חיבור בסיסית.

#### `POST /transcribe`

מקבל קובץ אודיו ומתמלל אותו לטקסט בעברית עם זיהוי דוברים.

**פרמטרים:**

- `file`: קובץ אודיו (mp3, wav, ogg, m4a)
- `sensitivity`: רגישות לזיהוי דוברים (0.1-2.0, ברירת מחדל: 0.7)

**תגובה:**
json
{
"success": true,
"message": "תמלול הושלם בהצלחה",
"segments": [
{
"start": 0.0,
"end": 2.5,
"text": "שלום, מה שלומך?",
"speaker": 0
},
{
"start": 3.2,
"end": 5.7,
"text": "הכל בסדר, תודה ששאלת.",
"speaker": 1
}
],
"full_text": "שלום, מה שלומך? הכל בסדר, תודה ששאלת.",
"duration": 5.7,
"speakers_count": 2
}

## פריסה ב-Render

### שלבים לפריסה

1. העלה את הקוד ל-GitHub:
bash
git init
git add .
git remote add origin https://github.com/yarivtch/hebrew_transcription_f_w_service-.git
git push -u origin main

2. היכנס ל-[Render](https://render.com/) וצור חשבון אם אין לך.

3. לחץ על "New" ובחר "Web Service".

4. בחר את המאגר שלך מ-GitHub.

5. הגדר את השירות:
   - **Name**: hebrew_transcription_f_w_service
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

6. בחר תוכנית מתאימה (לפחות Standard עבור קבצים גדולים).

7. הגדר משתני סביבה:
   - `WHISPER_MODEL_SIZE`: ivrit-ai/faster-whisper-v2-d4
   - `USE_GPU`: false
   - `ALLOWED_ORIGINS`: * (או רשימת דומיינים מופרדים בפסיקים)

8. הגדר דיסק נוסף:
   - **Mount Path**: /tmp
   - **Size**: 10 GB

9. לחץ על "Create Web Service".

### הגדרות נוספות

#### טיפול בקבצים גדולים

1. הגדל את הזמן המקסימלי לבקשה ב-Render:
   - לך להגדרות השירות
   - תחת "Advanced" הגדר Request Timeout ל-120 שניות או יותר

2. הגדל את גודל הקובץ המקסימלי:
   - הוסף משתנה סביבה `MAX_UPLOAD_SIZE` עם ערך בבייטים (למשל 100000000 עבור 100MB)

#### שגיאת זיכרון ב-Render

אם אתה נתקל בשגיאה `Ran out of memory (used over 512MB)` בעת פריסה ב-Render:

1. **שדרג לתוכנית בתשלום**:
   - לחץ על "Change Plan" בפרויקט שלך
   - בחר בתוכנית Standard (2GB RAM) או גבוהה יותר

2. **או השתמש במודל קטן יותר**:
   - שנה את משתנה הסביבה `WHISPER_MODEL_SIZE` ל-`tiny` או `base`
   - עדכן את קובץ `transcription/transcriber.py` להשתמש בפרמטרים חסכוניים בזיכרון:
     ```python
     model = WhisperModel(
         MODEL_SIZE, 
         device="cpu",
         compute_type="int8"
     )
     ```

3. **הגבל את גודל הקבצים** שניתן להעלות לשירות

## תקשורת בין קליינט לשרת

### דוגמת קוד קליינט JavaScript

javascript
async function transcribeAudio(audioFile, sensitivity = 0.7) {
const formData = new FormData();
formData.append('file', audioFile);
formData.append('sensitivity', sensitivity);
try {
const response = await fetch('https://your-render-url.onrender.com/transcribe', {
method: 'POST',
body: formData,
});
if (!response.ok) {
throw new Error(שגיאת שרת: ${response.status});
}
const result = await response.json();
return result;
} catch (error) {
console.error('שגיאה בתמלול:', error);
throw error;
}
}
// דוגמת שימוש
document.getElementById('uploadForm').addEventListener('submit', async (e) => {
e.preventDefault();
const fileInput = document.getElementById('audioFile');
const sensitivityInput = document.getElementById('sensitivity');
if (!fileInput.files[0]) {
alert('אנא בחר קובץ אודיו');
return;
}
const file = fileInput.files[0];
const sensitivity = parseFloat(sensitivityInput.value) || 0.7;
try {
const result = await transcribeAudio(file, sensitivity);
// הצגת התוצאות
const resultDiv = document.getElementById('result');
// יצירת תצוגת דוברים
let transcriptHtml = '';
let currentSpeaker = -1;
result.segments.forEach(segment => {
if (segment.speaker !== currentSpeaker) {
currentSpeaker = segment.speaker;
transcriptHtml += <div class="speaker-change">דובר ${currentSpeaker + 1}:</div>;
}
transcriptHtml += <div class="segment">${segment.text}</div>;
});
resultDiv.innerHTML = <h3>תוצאות התמלול</h3> <div class="transcript">${transcriptHtml}</div> <div class="metadata"> <p>משך: ${result.duration.toFixed(2)} שניות</p> <p>מספר דוברים: ${result.speakers_count}</p> </div> ;
} catch (error) {
alert(שגיאה בתמלול: ${error.message});
}
});

## הוראות מפורטות

### מבנה הפרויקט

הפרויקט מאורגן באופן הבא:
transcription-server/
├── main.py # קובץ ראשי של השרת
├── transcription/ # מודול התמלול
│ ├── init.py # אתחול המודול
│ ├── transcriber.py # לוגיקת התמלול
│ ├── speaker_detection.py # זיהוי דוברים
│ └── utils.py # פונקציות עזר
├── requirements.txt # תלויות הפרויקט
├── Dockerfile # להרצה בקונטיינר
├── render.yaml # הגדרות לפריסה ב-Render
├── .env.example # דוגמה למשתני סביבה
├── README.md # תיעוד הפרויקט
└── .gitignore # קבצים להתעלם בגיט

### תהליך התמלול

1. **קבלת הקובץ**: השרת מקבל קובץ אודיו דרך נקודת הקצה `/transcribe`
2. **וידוא תקינות**: בדיקה שהקובץ הוא קובץ אודיו תקין
3. **המרת פורמט**: המרה ל-WAV אם נדרש
4. **תמלול**: שימוש ב-faster-whisper לתמלול האודיו
5. **זיהוי דוברים**: זיהוי דוברים שונים לפי הפסקות וסימנים לשוניים
6. **החזרת תוצאות**: החזרת התוצאות בפורמט JSON מובנה

### הגדרות מתקדמות

#### התאמת רגישות זיהוי דוברים

פרמטר ה-`sensitivity` משפיע על זיהוי הדוברים:
- ערך נמוך (0.1-0.5): יותר דוברים (רגישות גבוהה לשינויים)
- ערך גבוה (1.0-2.0): פחות דוברים (רגישות נמוכה לשינויים)

#### שימוש ב-GPU

אם יש לך GPU תואם, תוכל להפעיל את המודל על GPU:
1. וודא שיש לך CUDA מותקן
2. הגדר את משתנה הסביבה `USE_GPU=true`

#### התאמת המודל

ניתן להחליף את המודל המשמש לתמלול:
1. הגדר את משתנה הסביבה `WHISPER_MODEL_SIZE` לשם המודל הרצוי
2. לדוגמה: `WHISPER_MODEL_SIZE=large-v2`

### פתרון בעיות נפוצות

#### שגיאת זיכרון

אם אתה נתקל בשגיאות זיכרון:
1. הגדל את הזיכרון הזמין לשירות ב-Render
2. שקול להשתמש במודל קטן יותר

#### שגיאת timeout

אם התמלול לוקח יותר מדי זמן:
1. הגדל את ה-timeout בהגדרות השירות ב-Render
2. שקול לחלק קבצים גדולים לחלקים קטנים יותר

#### שגיאות CORS

אם יש בעיות גישה מהקליינט:
1. וודא שהגדרת נכון את משתנה הסביבה `ALLOWED_ORIGINS`
2. הוסף את הדומיין של הקליינט לרשימת הדומיינים המורשים

#### שגיאת libmagic:

אם אתה נתקל בשגיאה `ImportError: failed to find libmagic. Check your installation`:

- **בווינדוס**: התקן את החבילה החלופית:
  ```bash
  pip uninstall python-magic
  pip install python-magic-bin
  ```

- **בלינוקס**: התקן את חבילת המערכת:
  ```bash
  sudo apt-get install libmagic1
  ```

- **במק**: התקן באמצעות Homebrew:
  ```bash
  brew install libmagic
  ```

#### שגיאת onnxruntime:

אם אתה נתקל בשגיאה `Applying the VAD filter requires the onnxruntime package`:

```bash
pip install onnxruntime==1.15.1
```

אם יש לך GPU ואתה רוצה לנצל אותו:

```bash
pip install onnxruntime-gpu==1.15.1
```

## הרצה בסביבה וירטואלית

הרצת השירות בסביבה וירטואלית מומלצת כדי למנוע התנגשויות עם חבילות Python אחרות במערכת שלך.

### יצירת סביבה וירטואלית והפעלת השירות

#### בלינוקס/מק:

```bash
# יצירת סביבה וירטואלית
python -m venv venv

# הפעלת הסביבה הוירטואלית
source venv/bin/activate

# התקנת התלויות
pip install -r requirements.txt

# הפעלת השרת
python -m uvicorn main:app --reload
```

#### בווינדוס:

```bash
# יצירת סביבה וירטואלית
python -m venv venv

# הפעלת הסביבה הוירטואלית
venv\Scripts\activate

# התקנת התלויות
pip install -r requirements.txt

# הפעלת השרת
python -m uvicorn main:app --reload
```

### יציאה מהסביבה הוירטואלית

כאשר תרצה לצאת מהסביבה הוירטואלית, פשוט הקלד:

```bash
deactivate
```

### פתרון בעיות בסביבה וירטואלית

#### שגיאת הרשאות ביצירת הסביבה:

אם אתה נתקל בשגיאת הרשאות בעת יצירת הסביבה הוירטואלית, נסה להוסיף `--user`:

```bash
python -m venv --user venv
```

#### שגיאת התקנת חבילות:

אם יש בעיות בהתקנת החבילות, וודא שיש לך גרסה עדכנית של pip:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### שגיאת FFmpeg:

וודא שהתקנת FFmpeg במערכת שלך:

- **לינוקס**: `sudo apt-get install ffmpeg`
- **מק**: `brew install ffmpeg`
- **ווינדוס**: הורד מ-[האתר הרשמי](https://ffmpeg.org/download.html) או התקן באמצעות Chocolatey: `choco install ffmpeg`
