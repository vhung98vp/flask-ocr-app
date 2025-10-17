import cv2
import numpy as np
import uuid
from .pattern import filter_id, filter_ids
from config import KAFKA

### UTILS ###
def build_doc_uid(s3_key, entity_type=KAFKA['doc_entity_type'], namespace=KAFKA['namespace_uuid']):
    return str(uuid.uuid5(namespace, f"{entity_type}:{s3_key}"))

def get_table_ids(cell_info):
    table = [[filter_id(text) if text else "" for text in row] for row in cell_info]
    cols_with_text = {j for i, row in enumerate(table) for j, text in enumerate(row) if text != ""}
    cols = sorted(cols_with_text)
    # Filer rows and cols without text
    filtered = [[row[j] for j in cols] for row in table]
    result = [row for row in filtered if any(cell != "" for cell in row)]
    return result


def get_boxed_image(img, box):
    pts = np.array(box).astype(int)
    x_min = np.min(pts[:, 0])
    x_max = np.max(pts[:, 0])
    y_min = np.min(pts[:, 1])
    y_max = np.max(pts[:, 1])
    crop_img = img[y_min:y_max, x_min:x_max]
    return crop_img, [y_min, y_max, x_min, x_max]

def get_lines_from_thresh(thresh, split_ratio=15):
    horizontal = thresh.copy()
    vertical = thresh.copy()

    h_size = int(horizontal.shape[1] / split_ratio)
    h_structure = cv2.getStructuringElement(cv2.MORPH_RECT, (h_size, 1))
    horizontal = cv2.erode(horizontal, h_structure)
    horizontal = cv2.dilate(horizontal, h_structure)

    v_size = int(vertical.shape[0] / split_ratio)
    v_structure = cv2.getStructuringElement(cv2.MORPH_RECT, (1, v_size))
    vertical = cv2.erode(vertical, v_structure)
    vertical = cv2.dilate(vertical, v_structure)

    return horizontal, vertical


def merge_close_lines(lines, min_gap=5):
    merged = []
    current = []
    for l in lines:
        if not current:
            current.append(l)
        elif l - current[-1] <= min_gap:
            current.append(l)
        else:
            merged.append(int(np.mean(current)))
            current = [l]
    if current:
        merged.append(int(np.mean(current)))
    return merged


def get_table_grid(table_bin, split_ratio=30):
    horizontal, vertical = get_lines_from_thresh(table_bin, split_ratio)

    horizontal_sum = np.sum(horizontal, axis=1)
    vertical_sum = np.sum(vertical, axis=0)
    h_lines = [i for i in range(len(horizontal_sum)) if horizontal_sum[i] > 255*max(table_bin.shape[1] * 0.1, 200)]
    v_lines = [i for i in range(len(vertical_sum)) if vertical_sum[i] > 255*max(table_bin.shape[0] * 0.1, 200)]
    h_lines = merge_close_lines(h_lines, 20)
    v_lines = merge_close_lines(v_lines, 20)
    
    return h_lines, v_lines

def content_to_text(content):
    texts = []
    ids = []
    table_ids = []
    for item in content:
        if 'cells' in item:
            texts.append('\n'.join(['|'.join(row) for row in item['cells']]))
            tid = get_table_ids(item['cells'])
            table_ids.extend(tid)
            ids.extend([i for row in tid for i in row if i])
        else:
            texts.append("\n".join(item.get('text', '')))
            ids.extend(filter_ids(item.get('text', '')))
    full_text = '\n'.join(texts)
    ids = list(set(ids))
    return full_text, ids, table_ids