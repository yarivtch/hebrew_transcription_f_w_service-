import os
import logging
from typing import Dict, List, Tuple, Any
import numpy as np
from faster_whisper import WhisperModel
from pydantic import BaseModel

from .speaker_detection import detect_speakers

# הגדרת לוגר
logger = logging.getLogger(__name__)

# מודל ברירת מחדל
DEFAULT_MODEL = "ivrit-ai/faster-whisper-v2-d4"
MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", DEFAULT_MODEL)

# טעינת המודל עם פרמטרים לחיסכון בזיכרון
logger.info(f"טוען מודל תמלול: {MODEL_SIZE}")
model = WhisperModel(
    MODEL_SIZE, 
    device="cuda" if os.getenv("USE_GPU", "false").lower() == "true" else "cpu",
    compute_type="int8",  # שימוש בדיוק נמוך יותר לחיסכון בזיכרון
    download_root=os.path.join(os.path.dirname(__file__), "../models")  # שמירת המודל בתיקייה ספציפית
)

class TranscriptionSegment(BaseModel):
    start: float
    end: float
    text: str
    speaker: int

async def transcribe_audio(audio_path: str, sensitivity: float = 0.7) -> Dict[str, Any]:
    """
    מתמלל קובץ אודיו ומזהה דוברים שונים.
    
    Args:
        audio_path: נתיב לקובץ האודיו
        sensitivity: רגישות לזיהוי דוברים (0.1-2.0)
    
    Returns:
        מילון עם תוצאות התמלול כולל סגמנטים לפי דוברים
    """
    logger.info(f"מתחיל תמלול: {audio_path}")
    
    # הגדרות תמלול
    beam_size = 5
    
    # ביצוע התמלול
    segments, info = model.transcribe(
        audio_path,
        language="he",
        beam_size=beam_size,
        word_timestamps=True,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=500)
    )
    
    # המרת הסגמנטים לרשימה
    segments_list = []
    for segment in segments:
        segments_list.append({
            "start": segment.start,
            "end": segment.end,
            "text": segment.text.strip(),
            "words": [{"word": w.word, "start": w.start, "end": w.end, "probability": w.probability} 
                     for w in segment.words] if segment.words else []
        })
    
    # זיהוי דוברים
    segments_with_speakers = detect_speakers(segments_list, sensitivity)
    
    # יצירת טקסט מלא
    full_text = " ".join([s["text"] for s in segments_with_speakers])
    
    # ספירת דוברים ייחודיים
    speakers_count = len(set([s["speaker"] for s in segments_with_speakers]))
    
    # יצירת תוצאה סופית
    result = {
        "success": True,
        "message": "תמלול הושלם בהצלחה",
        "segments": [
            TranscriptionSegment(
                start=s["start"],
                end=s["end"],
                text=s["text"],
                speaker=s["speaker"]
            ) for s in segments_with_speakers
        ],
        "full_text": full_text,
        "duration": info.duration,
        "speakers_count": speakers_count
    }
    
    logger.info(f"תמלול הושלם: {audio_path}, משך: {info.duration:.2f} שניות, דוברים: {speakers_count}")
    
    return result 