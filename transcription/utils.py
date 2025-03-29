import os
import logging
from typing import Optional
import magic
from fastapi import UploadFile
from pydub import AudioSegment

# הגדרת לוגר
logger = logging.getLogger(__name__)

# סוגי קבצים נתמכים
SUPPORTED_MIME_TYPES = [
    "audio/mpeg",           # MP3
    "audio/mp3",            # MP3
    "audio/wav",            # WAV
    "audio/x-wav",          # WAV
    "audio/ogg",            # OGG
    "audio/vorbis",         # OGG Vorbis
    "audio/opus",           # OGG Opus
    "audio/webm",           # WebM
    "audio/mp4",            # M4A
    "audio/x-m4a",          # M4A
    "audio/aac",            # AAC
    "audio/x-aac",          # AAC
    "audio/flac",           # FLAC
    "audio/x-flac",         # FLAC
]

async def validate_audio_file(file: UploadFile) -> bool:
    """
    בודק אם הקובץ שהועלה הוא קובץ אודיו תקין.
    
    Args:
        file: קובץ שהועלה
    
    Returns:
        True אם הקובץ תקין, False אחרת
    """
    # קריאת תוכן הקובץ
    content = await file.read()
    await file.seek(0)  # החזרת הסמן לתחילת הקובץ
    
    # בדיקת סוג הקובץ
    mime_type = magic.from_buffer(content, mime=True)
    
    # בדיקה אם הסוג נתמך
    is_valid = mime_type in SUPPORTED_MIME_TYPES
    
    if not is_valid:
        logger.warning(f"סוג קובץ לא נתמך: {mime_type}, שם קובץ: {file.filename}")
    
    return is_valid

async def convert_audio_if_needed(file_path: str) -> str:
    """
    ממיר את קובץ האודיו לפורמט WAV אם צריך.
    
    Args:
        file_path: נתיב לקובץ האודיו
    
    Returns:
        נתיב לקובץ המומר (או המקורי אם לא נדרשה המרה)
    """
    file_ext = os.path.splitext(file_path)[1].lower()
    
    # אם הקובץ כבר בפורמט WAV, אין צורך בהמרה
    if file_ext == ".wav":
        return file_path
    
    # המרה לפורמט WAV
    try:
        logger.info(f"ממיר קובץ מפורמט {file_ext} לפורמט WAV")
        
        # טעינת הקובץ באמצעות pydub
        if file_ext == ".mp3":
            audio = AudioSegment.from_mp3(file_path)
        elif file_ext == ".ogg":
            audio = AudioSegment.from_ogg(file_path)
        elif file_ext in [".m4a", ".aac"]:
            audio = AudioSegment.from_file(file_path, format="m4a")
        elif file_ext == ".flac":
            audio = AudioSegment.from_file(file_path, format="flac")
        else:
            # ניסיון לטעון את הקובץ בפורמט כללי
            audio = AudioSegment.from_file(file_path)
        
        # שמירה בפורמט WAV
        output_path = os.path.splitext(file_path)[0] + ".wav"
        audio.export(output_path, format="wav")
        
        return output_path
    
    except Exception as e:
        logger.error(f"שגיאה בהמרת הקובץ: {str(e)}")
        # אם יש שגיאה בהמרה, נחזיר את הקובץ המקורי
        return file_path 