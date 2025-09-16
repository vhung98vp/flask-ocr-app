import os
import cv2
import time
import numpy as np
from pdf2image import convert_from_path
from .model import OCRModel
from .utils import get_lines_from_thresh, get_table_grid, get_table_ids
from .pattern import filter_ids
from s3 import WClient
from config import get_logger
logger = get_logger(__name__)


ocr_model = OCRModel()
    
### FUNCTIONS ###
def process_cell(cell_img):
    cell_text = ocr_model.ocr_text_area(cell_img, None, False)
    return ''.join(cell_text)


def process_table(table_img):
    table_gray = cv2.cvtColor(table_img, cv2.COLOR_BGR2GRAY)
    table_bin = cv2.adaptiveThreshold(
        ~table_gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 15, -2
    )

    # Get horizontal and vertical lines
    h_lines, v_lines = get_table_grid(table_bin, split_ratio=30)

    cell_info = []
    for r in range(len(h_lines)-1):
        row = []
        for c in range(len(v_lines)-1):
            cy1, cy2 = h_lines[r], h_lines[r+1]
            cx1, cx2 = v_lines[c], v_lines[c+1]
            cell_img = table_img[cy1:cy2, cx1:cx2]
            if cell_img.size == 0:
                row.append("")
                continue
            cell_text = process_cell(cell_img)
            row.append(cell_text)
        cell_info.append(row)

    return cell_info


def process_contour(cnt, img, page_idx, table_idx):
    x, y, w, h = cv2.boundingRect(cnt)
    if w < 50 or h < 50:
        return None
    table_img = img[y:y+h, x:x+w]

    if len(ocr_model.ocr_text_area(table_img, 10, False)) < 3:
        return None

    logger.info(f"Detected table at page {page_idx}, table {table_idx}, position: x={x}, y={y}, w={w}, h={h}")

    area_height = img.shape[0] // 10
    header_area = img[max(0, y-area_height):y, x:x+w]
    header_text = ocr_model.ocr_text_area(header_area, 4, True)[::-1] if y > 0 else []
    footer_area = img[y+h:min(img.shape[0], y+h+area_height), x:x+w]
    footer_text = ocr_model.ocr_text_area(footer_area, 3, False) if y+h < img.shape[0] else []

    cell_info = process_table(table_img)
    
    return {
        "page": page_idx,
        "table": table_idx,
        "header": '\n'.join(header_text),
        "footer": '\n'.join(footer_text),
        "cells": cell_info
    }


def process_image(img_path, page_idx, detect_type):
    logger.info(f"Processing image: {img_path}...")
    start = time.time()
    img = cv2.imread(img_path)
    if detect_type == 0:
        text = ocr_model.ocr_text_area(img, None, False)
        logger.info(f"Total processing time for image {img_path} (s): {time.time()-start:.2f}")
        return [{
            "page": page_idx,
            "text": text
        }], filter_ids(text), []

    # Detect tables
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    thresh = cv2.adaptiveThreshold(
        ~blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 15, -2
    )

    horizontal, vertical = get_lines_from_thresh(thresh, split_ratio=15)
    mask = cv2.add(horizontal, vertical)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    results, ids, table_ids = [], [], []
    table_idx = 0
    for cnt in contours:
        result = process_contour(cnt, img, page_idx, table_idx)
        if result:
            results.append(result)
            table_idx += 1
            # Add detected ids in table
            tid = get_table_ids(result['cells'])
            table_ids.extend(tid)
            ids.extend([i for row in tid for i in row if i])
    
    # Detect text outside tables
    if detect_type == 2:
        mask = np.ones(gray.shape, dtype=np.uint8) * 255
        for cnt in contours: # Fill tables with gray
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(mask, (x, y), (x + w, y + h), 0, -1)  
        text_area = cv2.bitwise_and(gray, mask)
        text = ocr_model.ocr_text_area(text_area, None, False)

        results.append({
            "page": page_idx,
            "text": text
        })
        ids.extend(filter_ids(text))
    
    logger.info(f"Total processing time for image {img_path} (s): {time.time()-start:.2f}")
    return results, ids, table_ids


def process_pdf(pdf_path, output_dir, detect_type):
    pages = convert_from_path(pdf_path, dpi=300)
    results, ids, table_ids = [], [], []
    for page_idx, page in enumerate(pages):
        page_path = os.path.join(output_dir, f"page_{page_idx}.png")
        page.save(page_path, "PNG")
        # Get results
        res, id, tid = process_image(page_path, page_idx, detect_type)
        results.extend(res)
        ids.extend(id)
        table_ids.extend(tid)
    return results, ids, table_ids


def process_file(file_path, detect_type=2, s3_key=""):
    # 0, no table detection; 1, detect tables only; 2, detect tables and text
    logger.info(f"Processing file: {file_path} from {'local' if not s3_key else 'S3'}...")
    filename = os.path.basename(file_path)
    name, ext = os.path.splitext(filename)
    title, file_result = "", []
    if ext.lower() in ['.png', '.jpg', '.jpeg']:
        file_result = process_image(file_path, 0, detect_type)
        first_page = cv2.imread(file_path)
        title = ocr_model.ocr_title(first_page)
        if s3_key:
            upload_key = WClient.upload_file(file_path, s3_key)

    elif ext.lower() == '.pdf':
        # Make output dir
        output_dir = os.path.join(os.path.dirname(file_path), f"output_{filename}")
        os.makedirs(output_dir, exist_ok=True)

        # Process
        file_result = process_pdf(file_path, output_dir, detect_type)
        first_page = cv2.imread(os.path.join(output_dir, "page_0.png"))
        title = ocr_model.ocr_title(first_page)
        if s3_key:
            avatar_key = os.path.join(os.path.dirname(s3_key), f"{filename}_avatar.png")
            upload_key = WClient.upload_file(file_path, avatar_key)
    # Clean output dir local
        for f in os.listdir(output_dir):
            os.remove(os.path.join(output_dir, f))
        os.rmdir(output_dir)
    else:
        logger.error(f"Unsupported file type: {file_path}")

    if s3_key:
        logger.info(f"Uploaded avatar to {upload_key}")
        return {
            "file_name": filename,
            "title": title,
            "content": file_result[0],
            "ids": file_result[1],
            "table_ids": file_result[2],
            "s3_path": s3_key,
            "avatar": upload_key,
        }
    else:
        return {
            "file_name": filename,
            "title": title,
            "content": file_result[0],
            "ids": file_result[1],
            "table_ids": file_result[2],
        }