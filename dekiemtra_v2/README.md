# V2 Streamlit — Hệ thống ra đề CT 2018 (giữ 3 tab)

Cấu trúc:
- `app.py` (3 tab)
- `modules/`
  - `ai_client.py` (Gemini rotate model + cache list_models)
  - `data_loader.py` (đọc DOCX kế hoạch/CT, đọc file ma trận xlsx/docx/pdf)
  - `validators.py` (kiểm tra format câu hỏi theo dạng)
  - `docx_export.py` (xuất đề & ma trận Word)
  - `ui_tabs.py` (render 3 tab)

---

## 1) Chạy local

### Bước 1: Cài thư viện
```bash
pip install -r requirements.txt
```

### Bước 2: Cấu hình API key (khuyến nghị)
Tạo file `.streamlit/secrets.toml`:
```toml
GOOGLE_API_KEY = "PASTE_KEY_HERE"
```

### Bước 3: Chạy
```bash
streamlit run app.py
```

---

## 2) Đẩy lên GitHub & deploy Streamlit Cloud

### A) Copy code vào repo GitHub
1. Tạo repo mới trên GitHub.
2. Clone repo về máy:
```bash
git clone <URL_REPO_CUA_BAN>
cd <TEN_REPO>
```
3. Copy toàn bộ nội dung project này vào thư mục repo (giữ nguyên cấu trúc).
4. Commit & push:
```bash
git add .
git commit -m "Add V2 Streamlit app (3 tabs) + modules"
git push
```

### B) Deploy Streamlit Cloud
1. Vào Streamlit Cloud → New app → chọn repo/branch → file `app.py`.
2. Settings → Secrets, thêm:
```toml
GOOGLE_API_KEY = "PASTE_KEY_HERE"
```
3. Deploy.

---

## 3) Cách dùng 3 tab

### Tab 1 — Tạo đề từ ma trận
Upload file ma trận `.xlsx/.docx/.pdf` → bấm **Sinh đề theo ma trận**.

### Tab 2 — Soạn từng câu
- (Tuỳ chọn) Nạp dữ liệu CT từ DOCX ở Sidebar → có dropdown lớp/môn/học kì/chủ đề/bài.
- GV nhập YCCĐ; AI chỉ gợi ý tham khảo.
- Chọn dạng câu hỏi (TN/Đ-S/Nối/Điền/TL), mức độ, điểm → **Preview** → **Thêm vào đề**.

### Tab 3 — Ma trận & Xuất
- Chỉnh trực tiếp bảng.
- Tải Word: **Đề**, **Đề + Đáp án**, **Bảng ma trận**.

---

## 4) Gợi ý dữ liệu lớn
DOCX thường không ổn định. Khuyến nghị chuyển sang Excel có cột:
`Bộ sách, Học kì, Lớp, Môn, Chủ đề, Bài, Số tiết, YCCĐ`.
