# -*- coding: utf-8 -*-
"""
app.py — V2 (cải tiến) | Giữ cấu trúc 3 tab
Tab 1: Tạo đề từ ma trận (upload file, AI sinh đề)
Tab 2: Soạn từng câu (GV chọn Chủ đề/Bài/YCCĐ/Dạng/Mức/Điểm)
Tab 3: Ma trận & xuất (xem danh sách câu, chỉnh sửa, xuất Word)
"""
from __future__ import annotations

import streamlit as st

from modules.ai_client import GeminiClient, DEFAULT_GEN_CONFIG
from modules.data_loader import (
    load_curriculum_from_docx,
    load_sample_curriculum,
    extract_text_from_upload,
)
from modules.ui_tabs import render_tab_matrix_to_exam, render_tab_question_builder, render_tab_matrix_export


APP_TITLE = "HỆ THỐNG RA ĐỀ CT 2018 (V2)"
DEFAULT_SCHOOL = "TRƯỜNG TIỂU HỌC ................................"
DEFAULT_FOOTER = "CTGDPT 2018 • Tối ưu cho giáo viên • 3 tab (V1/V2)"

st.set_page_config(page_title=APP_TITLE, page_icon="🏫", layout="wide")


def _init_state():
    st.session_state.setdefault("exam_result", "")      # Tab1: text đề sinh từ ma trận
    st.session_state.setdefault("exam_list", [])        # Tab2/3: list câu hỏi có cấu trúc
    st.session_state.setdefault("current_preview", "")  # Tab2: preview câu
    st.session_state.setdefault("temp_question_data", None)
    st.session_state.setdefault("yccd_cache", {})       # cache gợi ý YCCĐ (theo bài)
    st.session_state.setdefault("curriculum", None)     # dữ liệu chương trình (nested dict hoặc df)
    st.session_state.setdefault("curriculum_df", None)  # bảng dữ liệu chuẩn hoá
    st.session_state.setdefault("school_name", DEFAULT_SCHOOL)


def _get_api_key() -> str:
    # Ưu tiên secrets -> input tay
    key = ""
    try:
        key = st.secrets.get("GOOGLE_API_KEY", "")
    except Exception:
        key = ""
    if not key:
        key = st.session_state.get("_api_key_input", "")
    return key.strip()


def main():
    _init_state()

    # ===== Sidebar =====
    with st.sidebar:
        st.header("🔑 Cấu hình")
        st.session_state["school_name"] = st.text_input(
            "Tên trường (in trên đề):",
            value=st.session_state["school_name"],
        )

        if not _get_api_key():
            st.text_input(
                "Google API Key (Gemini):",
                type="password",
                key="_api_key_input",
                help="Khuyến nghị đặt trong st.secrets['GOOGLE_API_KEY']",
            )

        st.caption("📌 Streamlit Cloud → Settings → Secrets: GOOGLE_API_KEY = '...'")

        st.divider()
        st.subheader("📚 Nạp dữ liệu CT (tuỳ chọn)")
        doc = st.file_uploader("Tải lên file kế hoạch/CT (DOCX)", type=["docx"], key="curr_docx")
        if doc is not None and st.button("Nạp dữ liệu từ DOCX", type="primary"):
            with st.spinner("Đang đọc & chuẩn hoá dữ liệu..."):
                df, nested, warn = load_curriculum_from_docx(doc.getvalue())
                st.session_state["curriculum_df"] = df
                st.session_state["curriculum"] = nested
            if warn:
                st.warning(warn)
            else:
                st.success("Đã nạp dữ liệu từ DOCX.")

        if st.button("Dùng dữ liệu mẫu (demo)", help="Chạy thử khi chưa có dữ liệu DOCX"):
            df, nested = load_sample_curriculum()
            st.session_state["curriculum_df"] = df
            st.session_state["curriculum"] = nested
            st.success("Đã nạp dữ liệu mẫu.")

        st.divider()
        if st.button("🧹 Xoá đề/preview/cache", help="Xoá dữ liệu đã sinh để làm lại"):
            for k in ["exam_result", "exam_list", "current_preview", "temp_question_data", "yccd_cache"]:
                st.session_state[k] = {} if k == "yccd_cache" else ([] if k == "exam_list" else "")
            st.success("Đã xoá.")

    # ===== Header =====
    st.markdown(
        """
        <style>
          .main-header { text-align:center; color:#1565C0; font-weight:800; font-size:28px;
                         text-transform:uppercase; margin:10px 0 18px; padding-bottom:8px; border-bottom:2px solid #eee; }
          .footer { position: fixed; left: 0; bottom: 0; width: 100%;
                    background-color: #f6f6f6; color: #333; text-align:center; padding: 8px 10px; font-size: 13px;
                    border-top: 1px solid #e5e5e5; z-index: 100; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(f"<div class='main-header'>{APP_TITLE}</div>", unsafe_allow_html=True)

    api_key = _get_api_key()
    client = GeminiClient(api_key=api_key)

    tab1, tab2, tab3 = st.tabs(
        ["📁 Tab 1: Tạo đề từ ma trận", "✍️ Tab 2: Soạn từng câu", "📊 Tab 3: Ma trận & Xuất"]
    )

    with tab1:
        render_tab_matrix_to_exam(
            client=client,
            school_name=st.session_state["school_name"],
            extract_text_from_upload=extract_text_from_upload,
            gen_config=DEFAULT_GEN_CONFIG,
        )

    with tab2:
        render_tab_question_builder(
            client=client,
            curriculum=st.session_state.get("curriculum"),
            curriculum_df=st.session_state.get("curriculum_df"),
            gen_config=DEFAULT_GEN_CONFIG,
        )

    with tab3:
        render_tab_matrix_export(
            school_name=st.session_state["school_name"],
            curriculum_df=st.session_state.get("curriculum_df"),
        )

    st.markdown(f"<div class='footer'>🏫 {DEFAULT_FOOTER}</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
