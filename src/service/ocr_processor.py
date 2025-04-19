from PIL import Image
import io
from .preprocess import preprocess_file
import easyocr
import re
import numpy as np

_READER_SIM = easyocr.Reader(["ch_sim", "en"], gpu=False)
_READER_TRA = easyocr.Reader(["ch_tra", "en"], gpu=False)

def count_chinese(text: str) -> int:
    return len(re.findall(r'[\u4e00-\u9fff]', text))

def ocr_extract(file_bytes: bytes) -> str:
    """
    Extract text from the file bytes using OCR.
    """
    preproccessed = preprocess_file(file_bytes)
    img = Image.open(io.BytesIO(preproccessed))
    arr = np.array(img)

    # sim_text = "\n".join(_READER_SIM.readtext(arr, detail=0, paragraph=True))
    tra_text = "\n".join(_READER_TRA.readtext(arr, detail=0, paragraph=True))
    return tra_text
    # if count_chinese(sim_text) >= count_chinese(tra_text):
    #     return sim_text
    # else:
    #     return tra_text