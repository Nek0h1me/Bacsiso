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
<!-- Thay thế bằng logo phù hợp nếu có -->
<img src="docs/dnu_logo.png" alt="DaiNam University Logo" width="200"/>
</p>

<!-- Thêm các badge liên quan đến công nghệ Flask và Python -->

</div>

📖 1. Giới thiệu

Dự án Hệ thống Quản lý Dịch vụ Y tế Số (Neko Care) là một ứng dụng web dựa trên kiến trúc Client-Server, sử dụng framework Flask của Python. Hệ thống nhằm số hóa các quy trình cơ bản trong phòng khám, bao gồm: đặt lịch hẹn, quản lý tồn kho thuốc, mua thuốc trực tuyến và cung cấp trợ lý ảo (Chatbot AI) để hỗ trợ người dùng.

🎯 Mục tiêu hệ thống

Phân quyền người dùng: Cung cấp hai vai trò (user và admin) với các bảng điều khiển riêng biệt.

Quản lý lịch hẹn: Cho phép người dùng đặt lịch, tải lên hình ảnh liên quan, và Admin duyệt/từ chối lịch hẹn qua email.

Thương mại điện tử Y tế: Cho phép người dùng tìm kiếm, xem tồn kho và đặt mua thuốc trực tuyến. Admin quản lý kho thuốc (thêm/sửa/xóa) và xử lý đơn hàng, có cơ chế trừ tồn kho tự động.

Tích hợp AI: Sử dụng API Chatbot cục bộ (Ollama) để cung cấp hỗ trợ tức thì về các thắc mắc sức khỏe cơ bản.

Cấu trúc dữ liệu: Sử dụng SQLite để lưu trữ an toàn thông tin người dùng, lịch hẹn, thuốc và đơn hàng.

🔧 2. Ngôn ngữ lập trình & Công nghệ sử dụng

Backend:  (Flask, Flask-Login, requests, sqlite3).

Frontend: HTML, Jinja2, Bootstrap 5, JavaScript (Fetch API).

Cơ sở dữ liệu: SQLite.

Dịch vụ Mail: SendGrid.

Mô hình AI: Ollama API (sử dụng mô hình Gemma 3B hoặc tương đương).

🖼️ 3. Hình ảnh các chức năng

<p align="center">
<img src="docs/1_admin_dashboard.png" alt="Mô tả: Giao diện Admin tổng quan" style="max-width:100%;">





<em>1: Bảng điều khiển Admin (Thống kê, Lịch hẹn, Quản lý Thuốc)</em>
</p>
<p align="center">
<img src="docs/2_user_dashboard.png" alt="Mô tả: Giao diện User" style="max-width:100%;">





<em>2: Bảng điều khiển Người dùng (Đặt lịch & Mua thuốc tìm kiếm tự động)</em>
</p>
<p align="center">
<img src="docs/3_floating_chatbot.png" alt="Mô tả: Chatbot nổi" style="max-width:100%;">





<em>3: Trợ lý ảo Chatbot (tích hợp Ollama)</em>
</p>

⚙️ 4. Cài đặt và Hướng dẫn chạy

4.1. Cài đặt môi trường Python

Clone repository và cài đặt các thư viện Python cần thiết:

# Giả sử bạn đang ở thư mục dự án
pip install -r requirements.txt
# (Hoặc cài thủ công: flask, flask-login, sqlite3, sendgrid, requests)


4.2. Khởi động Chatbot (Ollama)

Hệ thống sử dụng Ollama để cung cấp dịch vụ Chatbot AI. Bạn cần cài đặt Ollama và đảm bảo nó đang chạy:

# Chạy mô hình gemma3:1b cục bộ
ollama run gemma3:1b
# Đảm bảo dịch vụ Ollama đang hoạt động trên cổng mặc định (http://localhost:11434)


4.3. Khởi tạo Cơ sở dữ liệu

Hệ thống sẽ tự động khởi tạo CSDL (healthcare.db) và thêm dữ liệu mẫu khi chạy lần đầu. Nếu bạn đã chạy trước đó, hãy xóa healthcare.db để tạo lại các bảng mới (bao gồm medicines và orders).

4.4. Chạy ứng dụng Flask

Chạy tệp chính app.py:

python app.py


Truy cập: http://127.0.0.1:5000

4.5. Tài khoản mặc định

Admin: username: admin, password: 1

User: username: user1, password: 1

📞 5. Liên hệ

Họ tên: Nguyễn Cao Tùng.
Lớp: CNTT 16-03.
Email: nguyentungxneko@gmail.com.

© 2025 AIoTLab, Faculty of Information Technology, DaiNam University. All rights reserved.
