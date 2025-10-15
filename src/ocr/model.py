
import cv2
import numpy as np
from PIL import Image
from paddleocr import PaddleOCR
from vietocr.tool.predictor import Predictor
from vietocr.tool.config import Cfg
from .utils import get_boxed_image


def vietocr_predictor():
    config = Cfg.load_config_from_file('./models/vietocr/config.yml')
    config['device'] = 'cuda'
    return Predictor(config)


class OCRModel:
    def __init__(self):
        self.paddle_ocr = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=True, 
            det_model_dir="./models/paddleocr/det/en/en_PP-OCRv3_det_infer",
            rec_model_dir="./models/paddleocr/rec/en/en_PP-OCRv3_rec_infer",
            cls_model_dir="./models/paddleocr/cls/ch_ppocr_mobile_v2.0_cls_infer",)
        self.viet_ocr = vietocr_predictor()

    def vietocr_text(self, img):
        pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        text = self.viet_ocr.predict(pil_img)
        return text.strip()
    
    def ocr_text_area(self, ocr_area, n_rows=3, reverse=True):
        # Use PaddleOCR to detect text boxes in ocr_area
        boxes = self.paddle_ocr.ocr(ocr_area, cls=True, rec=False)
        # boxes = ocr_result[0] if ocr_result else []
        if not boxes:
            return []
        
        boxes_sorted = sorted(boxes, key=lambda box: np.mean([pt[1] for pt in box]), reverse=reverse)
        selected_boxes = boxes_sorted[:n_rows] if n_rows else boxes_sorted

        selected_texts = []
        for box in selected_boxes:
            crop_img, _ = get_boxed_image(ocr_area, box)
            text = self.vietocr_text(crop_img)
            selected_texts.append(text)

        return selected_texts
        
    
    def ocr_title(self, img, area_height=0.25):
        h, w = img.shape[:2]
        ocr_area = img[0:int(h*area_height), 0:w]
        boxes = self.paddle_ocr.ocr(ocr_area, cls=True, rec=False)
        # boxes = ocr_result[0] if ocr_result else []

        candidates = []
        for box in boxes:
            crop_img, corner = get_boxed_image(img, box)
            text = self.vietocr_text(crop_img)
            if not text.strip():
                continue

            is_upper = text.strip().isupper()
            top, bottom, left, right = corner
            box_height = bottom-top
            center_dist = abs((left+right)/2 - w/2) / (w/2)
            candidates.append((is_upper, box_height, center_dist, top, text))
        
        if not candidates:
            return "untitled"
        
        # pick best candidate by score
        max_height = max(c[1] for c in candidates) or 1
        best = sorted(
            candidates,
            key=lambda c: (
                (1 - c[0]) * 0.1     # prefer uppercase (1=upper → score 0, else penalty)
                + (1 - (c[1] / max_height)) * 0.1  # prefer taller boxes
                + c[2] * 0.8         # prefer closer to center
            )
        )[:3]
        best.sort(key=lambda x: x[3])
        result = [c[4].strip() for c in best]
        return '\n'.join(result)
