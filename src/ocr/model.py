
import cv2
import numpy as np
from PIL import Image
from paddleocr import PaddleOCR
from vietocr.tool.predictor import Predictor
from vietocr.tool.config import Cfg
from .utils import get_boxed_image
from config import VIETOCR_CONFIG, PADDLE_CONFIG


def vietocr_config():
    try:
        # Try to use local model
        config = Cfg.load_config_from_file(VIETOCR_CONFIG['base_config'])
        config.update(Cfg.load_config_from_file(VIETOCR_CONFIG['transformer_config']))
        config['weights'] = VIETOCR_CONFIG['model_weight']
    except Exception as e:
        config = Cfg.load_config_from_name('vgg_transformer')

    config['device'] = VIETOCR_CONFIG['device']
    return config


class OCRModel:
    def __init__(self):
        self.paddle_ocr = PaddleOCR(
                        use_angle_cls=True,
                        lang=PADDLE_CONFIG['language'], 
                        det_model_dir=PADDLE_CONFIG['det_model_dir'],
                        rec_model_dir=PADDLE_CONFIG['rec_model_dir'],
                        cls_model_dir=PADDLE_CONFIG['cls_model_dir']
                    )
        self.viet_ocr = Predictor(vietocr_config())

    def vietocr_text(self, img):
        pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        text = self.viet_ocr.predict(pil_img)
        return text.strip()
    
    def ocr_text_area(self, ocr_area, n_rows=3, reverse=True):
        # Use PaddleOCR to detect text boxes in ocr_area
        ocr_result = self.paddle_ocr.ocr(ocr_area, cls=True, rec=False)
        boxes = ocr_result[0] if ocr_result else []
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
        ocr_result = self.paddle_ocr.ocr(ocr_area, cls=True, rec=False)
        boxes = ocr_result[0] if ocr_result else []

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
        
        # sort: largest height, closest to center, lower on page
        candidates.sort(key=lambda x: (not x[0], -x[1], x[2], x[3]))
        result = candidates[:3]
        result.sort(key=lambda x: x[3])
        return [c[4].strip() for c in result]