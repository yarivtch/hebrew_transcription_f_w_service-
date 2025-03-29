import os
import logging
import tempfile
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

from transcription.transcriber import transcribe_audio
from transcription.utils import validate_audio_file, convert_audio_if_needed

# הגדרת לוגר
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="שרת תמלול אודיו בעברית",
    description="API לתמלול קבצי אודיו בעברית עם זיהוי דוברים",
    version="1.0.0"
)

# הגדרת CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# מודלים לתגובות
class TranscriptionSegment(BaseModel):
    start: float
    end: float
    text: str
    speaker: int

class TranscriptionResponse(BaseModel):
    success: bool = True
    message: str = "תמלול הושלם בהצלחה"
    segments: list[TranscriptionSegment] = []
    full_text: str = ""
    duration: float = 0.0
    speakers_count: int = 0

class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    error_code: str = "processing_error"

@app.get("/")
async def root():
    return {"message": "שרת תמלול אודיו בעברית פעיל"}

@app.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_endpoint(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    sensitivity: float = Form(0.7),
):
    """
    מקבל קובץ אודיו ומתמלל אותו לטקסט בעברית עם זיהוי דוברים.
    
    - **file**: קובץ אודיו (mp3, wav, ogg, m4a)
    - **sensitivity**: רגישות לזיהוי דוברים (0.1-2.0, ברירת מחדל: 0.7)
    
    מחזיר תמלול מפוסק ומאורגן לפי דוברים בפורמט JSON.
    """
    try:
        # בדיקת תקינות הקובץ
        if not file.filename:
            raise HTTPException(status_code=400, detail="לא נשלח קובץ")
        
        # וידוא שהקובץ הוא קובץ אודיו תקין
        if not await validate_audio_file(file):
            raise HTTPException(
                status_code=400, 
                detail="הקובץ שנשלח אינו קובץ אודיו תקין או שהפורמט אינו נתמך"
            )
        
        # שמירת הקובץ באופן זמני
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, file.filename)
        
        with open(temp_file_path, "wb") as temp_file:
            content = await file.read()
            temp_file.write(content)
        
        # המרת הקובץ אם צריך
        converted_file_path = await convert_audio_if_needed(temp_file_path)
        
        # תמלול הקובץ
        logger.info(f"מתחיל תמלול הקובץ: {file.filename}")
        result = await transcribe_audio(converted_file_path, sensitivity)
        
        # ניקוי קבצים זמניים ברקע
        background_tasks.add_task(lambda: os.remove(temp_file_path))
        if converted_file_path != temp_file_path:
            background_tasks.add_task(lambda: os.remove(converted_file_path))
        background_tasks.add_task(lambda: os.rmdir(temp_dir))
        
        return result
        
    except Exception as e:
        logger.error(f"שגיאה בתמלול: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                success=False,
                message=f"שגיאה בעיבוד הקובץ: {str(e)}",
                error_code="processing_error"
            ).dict()
        )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True) 