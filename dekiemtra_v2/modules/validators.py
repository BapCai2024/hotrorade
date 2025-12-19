# -*- coding: utf-8 -*-
from __future__ import annotations

import re
from typing import Dict, List, Tuple


def validate_question_format(text: str, q_type: str) -> Tuple[bool, List[str]]:
    errors: List[str] = []
    t = (text or "").strip()
    if not t:
        return False, ["Nội dung câu hỏi rỗng."]

    qt = (q_type or "").lower()

    if "trắc nghiệm" in qt or "4 lựa chọn" in qt:
        for opt in ["A.", "B.", "C.", "D."]:
            if opt not in t:
                errors.append(f"Thiếu lựa chọn {opt}")
        m = re.search(r"(?im)^\s*đáp\s*án\s*:\s*([abcd])\s*$", t)
        if not m:
            errors.append("Thiếu hoặc sai dòng 'Đáp án: A/B/C/D'")

    elif "đúng/sai" in qt or "dung/sai" in qt:
        if "đáp án" not in t.lower():
            errors.append("Nên có phần 'Đáp án:' cho Đúng/Sai để xuất đề ổn định.")

    elif "ghép" in qt or "nối cột" in qt or "noi cot" in qt:
        if "cột a" not in t.lower() or "cột b" not in t.lower():
            errors.append("Thiếu 'Cột A' hoặc 'Cột B'.")
        if "đáp án" not in t.lower():
            errors.append("Thiếu 'Đáp án:' (dạng 1-b;2-a...).")

    elif "điền khuyết" in qt or "hoàn thành" in qt or "dien khuyet" in qt:
        if "......" not in t and "…" not in t and "___" not in t:
            errors.append("Câu điền khuyết nên có chỗ trống (...... hoặc ___).")
        if "đáp án" not in t.lower():
            errors.append("Thiếu 'Đáp án:' cho câu điền khuyết.")

    else:
        if "đáp án" not in t.lower() and "gợi ý" not in t.lower():
            errors.append("Khuyến nghị có 'Đáp án:' hoặc 'Gợi ý chấm' để xuất đề ổn định.")

    return (len(errors) == 0), errors


def validate_exam_list(exam_list: List[Dict]) -> Tuple[bool, List[str]]:
    errors: List[str] = []
    if not exam_list:
        return False, ["Chưa có câu hỏi nào trong đề."]

    total = 0.0
    for i, q in enumerate(exam_list, start=1):
        try:
            total += float(q.get("points", 0) or 0)
        except Exception:
            errors.append(f"Câu {i}: điểm không hợp lệ.")

    if total <= 0:
        errors.append("Tổng điểm = 0. Bạn hãy nhập điểm cho từng câu.")
    return (len(errors) == 0), errors


def total_points(exam_list: List[Dict]) -> float:
    s = 0.0
    for q in exam_list:
        try:
            s += float(q.get("points", 0) or 0)
        except Exception:
            pass
    return s
