from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sqlite3
import os
from werkzeug.utils import secure_filename
# Import thư viện SendGrid
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
# --- IMPORT MỚI ĐỂ XỬ LÝ THỜI GIAN ---
from datetime import datetime, timezone, timedelta 

# ========== Config ==========
app = Flask(__name__)
app.secret_key = 'super_secret_key'
login_manager = LoginManager(app)
login_manager.login_view = 'login'

UPLOAD_FOLDER = 'images'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- Cấu hình SendGrid ---
SENDGRID_API_KEY = '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'
EMAIL_FROM = '123taolambo@gmail.com' # Email bạn đã xác thực với SendGrid

DB_NAME = 'healthcare.db'

# ========== Database init ==========
def init_db():
    if not os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('''CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            name TEXT,
            age INTEGER,
            email TEXT NOT NULL
        )''')
        c.execute('''CREATE TABLE appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            disease TEXT NOT NULL,
            datetime TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            image_path TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )''')
        # Pre-populate data
        c.execute("INSERT INTO users (username, password, role, name, age, email) VALUES (?, ?, ?, ?, ?, ?)",
                  ('admin', '1', 'admin', 'Admin', 0, 'admin@example.com'))
        c.execute("INSERT INTO users (username, password, role, name, age, email) VALUES (?, ?, ?, ?, ?, ?)",
                  ('user1', '1', 'user', 'Patient One', 30, 'user1@example.com'))
        c.execute("INSERT INTO users (username, password, role, name, age, email) VALUES (?, ?, ?, ?, ?, ?)",
                  ('user2', '1', 'user', 'Patient Two', 45, 'user2@example.com'))
        c.execute("INSERT INTO users (username, password, role, name, age, email) VALUES (?, ?, ?, ?, ?, ?)",
                  ('user3', '1', 'user', 'Patient Three', 25, 'user3@example.com'))
        conn.commit()
        conn.close()
        print("Database initialized.")

init_db()

# ========== User model ==========
class User(UserMixin):
    def __init__(self, id, username, role, name, age, email):
        self.id = id
        self.username = username
        self.role = role
        self.name = name
        self.age = age
        self.email = email

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return User(row[0], row[1], row[3], row[4], row[5], row[6])
    return None

# ========== Helpers ==========
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def send_email(to, subject, body):
    sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
    from_email = Email(EMAIL_FROM)
    to_email = To(to)
    content = Content("text/plain", body)
    mail = Mail(from_email, to_email, subject, content)
    try:
        response = sg.client.mail.send.post(request_body=mail.get())
        print(f"Email sent to {to}, Status Code: {response.status_code}")
    except Exception as e:
        print(f"Email error: {e}")
        raise e

# ========== Routes ==========
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        age = int(request.form['age'])
        email = request.form['email']
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password, role, name, age, email) VALUES (?, ?, 'user', ?, ?, ?)",
                      (username, password, name, age, email))
            conn.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists.', 'danger')
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        row = c.fetchone()
        conn.close()
        if row:
            user = User(row[0], row[1], row[3], row[4], row[5], row[6])
            login_user(user)
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# ========== Admin ==========
@app.route('/admin')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        return redirect(url_for('user_dashboard'))
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT name, age, email FROM users WHERE role = 'user'")
    patients = c.fetchall()
    c.execute('''SELECT a.id, u.name, u.email, a.disease, a.datetime, a.status, a.image_path
                 FROM appointments a JOIN users u ON a.user_id = u.id''')
    appointments = c.fetchall()
    conn.close()

    # Thống kê
    total_patients = len(patients)
    pending = sum(1 for a in appointments if a[5] == 'pending')
    approved = sum(1 for a in appointments if a[5] == 'approved')
    rejected = sum(1 for a in appointments if a[5] == 'rejected')

    return render_template('admin.html', patients=patients, appointments=appointments,
                           total_patients=total_patients, pending=pending,
                           approved=approved, rejected=rejected)

@app.route('/admin/update_status/<int:appt_id>/<string:status>', methods=['POST'])
@login_required
def update_status(appt_id, status):
    if current_user.role != 'admin':
        return redirect(url_for('user_dashboard'))
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE appointments SET status = ? WHERE id = ?", (status, appt_id))
    conn.commit()
    c.execute("SELECT u.email, u.name, a.disease, a.datetime FROM appointments a JOIN users u ON a.user_id = u.id WHERE a.id = ?", (appt_id,))
    row = c.fetchone()
    conn.close()
    if row:
        email_to = row[0]
        user_name = row[1]
        disease = row[2]
        datetime_info = row[3] 
        subject = ""
        body = ""
        try:
            dt_obj = datetime.strptime(datetime_info, '%Y-%m-%d %H:%M')
            formatted_time = dt_obj.strftime("lúc %H:%M ngày %d tháng %m năm %Y")
        except ValueError:
            formatted_time = datetime_info
        if status == 'approved':
            subject = "Lịch hẹn của bạn đã được chấp thuận"
            body = (f"Kính thưa Anh/Chị {user_name},\n\n"
                    f"Chúng tôi đã chấp nhận hẹn gặp anh/chị vào {formatted_time} "
                    f"về vấn đề: {disease}.\n\n"
                    "Trân trọng,\nPhòng khám Neko")
        elif status == 'rejected':
            subject = "Lịch hẹn của bạn đã bị từ chối"
            body = (f"Kính thưa Anh/Chị {user_name},\n\n"
                    f"Chúng tôi xin phép từ chối đơn hẹn của anh/chị (vấn đề: {disease}, thời gian: {formatted_time}).\n\n"
                    "Mong anh/chị thông cảm.\n\nTrân trọng,\nPhòng khám Neko")
        if subject:
            try:
                send_email(email_to, subject, body)
            except Exception as e:
                print(f"Lỗi gửi email admin: {e}")
    flash(f'Appointment {status}', 'success')
    return redirect(url_for('admin_dashboard'))

# ========== User ==========
@app.route('/user')
@login_required
def user_dashboard():
    if current_user.role == 'admin':
        return redirect(url_for('admin_dashboard'))

    # --- CẬP NHẬT: Lấy ngày giờ VN (GMT+7) ---
    vn_timezone = timezone(timedelta(hours=7))
    now_vn = datetime.now(vn_timezone)
    # Lấy ngày hôm nay theo định dạng YYYY-MM-DD
    today_date = now_vn.strftime('%Y-%m-%d')
    # Lấy giờ hiện tại theo định dạng HH:MM
    current_time = now_vn.strftime('%H:%M')
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Sửa lại câu query để lấy đúng cột
    c.execute("SELECT disease, datetime, status, image_path, id FROM appointments WHERE user_id = ?", (current_user.id,))
    appointments = c.fetchall()
    conn.close()
    
    # Trả ngày giờ hiện tại sang template
    return render_template('user.html', 
                           appointments=appointments, 
                           today_date=today_date, 
                           current_time=current_time)

@app.route('/book', methods=['POST'])
@login_required
def book():
    if current_user.role == 'admin':
        return redirect(url_for('admin_dashboard'))

    disease = request.form['disease']
    date = request.form['date']
    time = request.form['time']
    datetime_str = f"{date} {time}"
    image_filename = None

    # --- CẬP NHẬT: VALIDATION THỜI GIAN (BACKEND) ---
    try:
        vn_timezone = timezone(timedelta(hours=7))
        # Lấy thời gian hiện tại ở VN
        now_vn = datetime.now(vn_timezone)
        
        # Chuyển string từ form thành datetime object
        selected_dt = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')
        
        # Gán múi giờ VN cho thời gian user chọn
        selected_dt_aware = selected_dt.replace(tzinfo=vn_timezone)
        
        # So sánh: Nếu chọn thời gian trong quá khứ
        # (Cho phép chênh lệch 1 phút phòng trường hợp server/client chậm)
        if selected_dt_aware < (now_vn - timedelta(minutes=1)):
            flash('Bạn không thể đặt lịch hẹn trong quá khứ. Vui lòng chọn ngày giờ trong tương lai.', 'danger')
            return redirect(url_for('user_dashboard'))
            
    except ValueError:
        flash('Định dạng ngày hoặc giờ không hợp lệ.', 'danger')
        return redirect(url_for('user_dashboard'))
    # --- KẾT THÚC VALIDATION ---

    if 'image' in request.files:
        file = request.files['image']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(save_path)
            image_filename = filename

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO appointments (user_id, disease, datetime, image_path) VALUES (?, ?, ?, ?)",
              (current_user.id, disease, datetime_str, image_filename))
    conn.commit()
    conn.close()

    # --- Gửi email xác nhận (Đã bọc try/except cẩn thận) ---
    try:
        subject = "Xác nhận đặt lịch hẹn"
        body = (f"Kính thưa Anh/Chị {current_user.name},\n\n"
                "Cảm ơn Anh/Chị đã đặt hẹn.\n"
                "Chúng tôi sẽ gửi thông báo cho Anh/Chị trong thời gian sớm nhất.\n\n"
                "Trân trọng,\nPhòng khám Neko")
        send_email(current_user.email, subject, body)
    except Exception as e:
        print(f"Lỗi gửi email xác nhận đặt hẹn: {e}")
    # --- KẾT THÚC PHẦN GỬI MAIL ---

    flash('Appointment booked', 'success')
    return redirect(url_for('user_dashboard'))

@app.route('/images/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ========== Run ==========
if __name__ == '__main__':
    app.run(debug=True)   