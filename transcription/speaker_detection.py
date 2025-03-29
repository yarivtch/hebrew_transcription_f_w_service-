import re
from typing import List, Dict, Any
import logging

# הגדרת לוגר
logger = logging.getLogger(__name__)

# ביטויים רגולריים לזיהוי תחילת דיבור חדש
SPEAKER_PATTERNS = [
    r'^(היי|שלום|אהלן|הי|יו|אהלו)',  # ברכות
    r'^(אז|טוב|אוקיי|אוקי|בסדר|אממ)',  # מילות פתיחה
    r'^(תראה|תראי|תקשיב|תקשיבי)',  # פניות
    r'^(אני חושב|אני חושבת)',  # הבעת דעה
    r'^(מה דעתך|מה אתה חושב|מה את חושבת)',  # שאלות
]

def detect_speakers(segments: List[Dict[str, Any]], sensitivity: float = 0.7) -> List[Dict[str, Any]]:
    """
    מזהה דוברים שונים בסגמנטים של תמלול.
    
    Args:
        segments: רשימת סגמנטים מהתמלול
        sensitivity: רגישות לזיהוי דוברים (0.1-2.0)
    
    Returns:
        רשימת סגמנטים עם זיהוי דוברים
    """
    if not segments:
        return []
    
    # התאמת רגישות - ערך נמוך יותר מוביל ליותר דוברים
    pause_threshold = max(0.5, min(2.0, sensitivity))
    
    # הוספת מידע על דוברים
    current_speaker = 0
    result = []
    
    for i, segment in enumerate(segments):
        is_new_speaker = False
        
        # בדיקה אם יש הפסקה משמעותית בין הסגמנטים
        if i > 0:
            prev_end = segments[i-1]["end"]
            current_start = segment["start"]
            pause_duration = current_start - prev_end
            
            # הפסקה ארוכה מסף מסוים מצביעה על דובר חדש
            if pause_duration > pause_threshold:
                is_new_speaker = True
                logger.debug(f"זיהוי דובר חדש בגלל הפסקה של {pause_duration:.2f} שניות")
        
        # בדיקת תבניות לשוניות המצביעות על דובר חדש
        text = segment["text"].strip()
        for pattern in SPEAKER_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                is_new_speaker = True
                logger.debug(f"זיהוי דובר חדש בגלל תבנית לשונית: {pattern}")
                break
        
        # עדכון מספר הדובר אם זוהה דובר חדש
        if is_new_speaker:
            current_speaker += 1
        
        # הוספת הסגמנט עם מידע על הדובר
        segment_with_speaker = segment.copy()
        segment_with_speaker["speaker"] = current_speaker
        result.append(segment_with_speaker)
    
    return result 