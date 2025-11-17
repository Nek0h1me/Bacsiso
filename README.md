
<h2 align="center">
<a href="https://dainam.edu.vn/vi/khoa-cong-nghe-thong-tin">
🎓 Faculty of Information Technology (DaiNam University)
</a>
</h2>

<h2 align="center">
HỆ THỐNG QUẢN LÝ DỊCH VỤ Y TẾ SỐ (NEKO CARE)
</h2>

<div align="center">
    <p align="center">
        <img src="docs/aiotlab_logo.png" alt="AIoTLab Logo" width="170"/>
        <img src="docs/fitdnu_logo.png" alt="AIoTLab Logo" width="180"/>
        <img src="docs/dnu_logo.png" alt="DaiNam University Logo" width="200"/>
    </p>

[![AIoTLab](https://img.shields.io/badge/AIoTLab-green?style=for-the-badge)](https://www.facebook.com/DNUAIoTLab)
[![Faculty of Information Technology](https://img.shields.io/badge/Faculty%20of%20Information%20Technology-blue?style=for-the-badge)](https://dainam.edu.vn/vi/khoa-cong-nghe-thong-tin)
[![DaiNam University](https://img.shields.io/badge/DaiNam%20University-orange?style=for-the-badge)](https://dainam.edu.vn)

</div>

---

## 📖 1. Giới thiệu

Dự án **Hệ thống Quản lý Dịch vụ Y tế Số (Neko Care)** là một ứng dụng web dựa trên kiến trúc Client-Server, sử dụng **Flask (Python)**. Hệ thống nhằm số hóa quy trình của phòng khám: đặt lịch hẹn, quản lý kho thuốc, mua thuốc trực tuyến và trợ lý ảo AI.

### 🎯 Mục tiêu hệ thống

* **Phân quyền người dùng:** user & admin với giao diện riêng.
* **Quản lý lịch hẹn:** người dùng đặt lịch + upload hình ảnh; admin duyệt từ email.
* **Thương mại điện tử Y tế:** mua thuốc online, tự động trừ tồn kho.
* **Tích hợp AI Chatbot:** sử dụng API Ollama (Gemma 3B).
* **Database:** lưu người dùng, lịch hẹn, thuốc, đơn hàng bằng SQLite.

---

## 🔧 2. Công nghệ sử dụng

### Backend:

* Flask
* Flask-Login
* SQLite3
* Requests
* SendGrid Mail API

### Frontend:

* HTML + CSS
* Jinja2 (template)
* Bootstrap 5
* JavaScript (Fetch API)

### AI Chatbot:

* Ollama (Gemma 3B / Gemma 1B)

---

## 🖼️ 3. Hình ảnh các chức năng

<p align="center">
<img src="10.png" alt="Admin Dashboard" style="max-width:100%;">
<br>
<em>1. Bảng điều khiển Admin</em>
</p>

<p align="center">
<img src="user.png" alt="User Dashboard" style="max-width:100%;">
<br>
<em>2. Bảng điều khiển Người dùng</em>
</p>

<p align="center">
<img src="chatbot.png" alt="Floating Chatbot" style="max-width:100%;">
<br>
<em>3. Trợ lý ảo Chatbot (Ollama)</em>
</p>

---

## ⚙️ 4. Cài đặt và Hướng dẫn chạy

### **4.1. Cài đặt môi trường Python**

```bash
pip install -r requirements.txt
```

Hoặc tự cài:

```
flask, flask-login, sqlite3, sendgrid, requests
```

---

### **4.2. Khởi động Chatbot (Ollama)**

```bash
ollama run gemma3:1b
```

Kiểm tra Ollama hoạt động tại:

```
http://localhost:11434
```

---

### **4.3. Khởi tạo cơ sở dữ liệu**

* Hệ thống tự tạo `healthcare.db` khi chạy lần đầu.
* Nếu đã có file cũ → xóa để tạo lại bảng `medicines` và `orders`.

---

### **4.4. Chạy ứng dụng Flask**

```bash
python app.py
```

Truy cập:

```
http://127.0.0.1:5000
```

---

### **4.5. Tài khoản mặc định**

* **Admin:** admin / 1
* **User:** user1 / 1

---

## 📞 5. Liên hệ

* **Họ tên:** Nguyễn Cao Tùng
* **Lớp:** CNTT 16-03
* **Email:** [nguyentungxneko@gmail.com](mailto:nguyentungxneko@gmail.com)

© 2025 AIoTLab, Faculty of Information Technology, DaiNam University. All rights reserved.
