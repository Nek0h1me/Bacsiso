from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sqlite3
import os
import json # Cần cho việc xử lý JSON streaming
from werkzeug.utils import secure_filename
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
from datetime import datetime, timezone, timedelta
import requests 

# ==================================
# CONFIG
# ==================================
app = Flask(__name__)
app.secret_key = 'super_secret_key'
login_manager = LoginManager(app)
login_manager.login_view = 'login'

UPLOAD_FOLDER = 'images'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

SENDGRID_API_KEY = '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'
EMAIL_FROM = '123taolambo@gmail.com'

DB_NAME = 'healthcare.db'


# ==================================
# DATABASE INIT (ĐÃ CẬP NHẬT)
# ==================================
def init_db():
    if not os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()

        # Bảng USERS (Không đổi)
        c.execute('''CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            name TEXT,
            age INTEGER,
            email TEXT NOT NULL
        )''')

        # Bảng APPOINTMENTS (Không đổi)
        c.execute('''CREATE TABLE appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            disease TEXT NOT NULL,
            datetime TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            image_path TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )''')

        # Bảng MỚI: QUẢN LÝ THUỐC (Tồn kho)
        c.execute('''CREATE TABLE medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            stock INTEGER NOT NULL
        )''')
        
        # Bảng MỚI: ĐƠN HÀNG
        c.execute('''CREATE TABLE orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            medicine_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            total_price REAL NOT NULL,
            order_date TEXT NOT NULL,
            status TEXT DEFAULT 'pending', -- pending, processed, cancelled
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(medicine_id) REFERENCES medicines(id)
        )''')

        # sample data
        c.execute("INSERT INTO users VALUES (NULL,'admin','1','admin','Admin',0,'admin@example.com')")
        c.execute("INSERT INTO users VALUES (NULL,'user1','1','user','Patient One',30,'user1@example.com')")
        c.execute("INSERT INTO users VALUES (NULL,'user2','1','user','Patient Two',45,'user2@example.com')")
        c.execute("INSERT INTO users VALUES (NULL,'user3','1','user','Patient Three',25,'user3@example.com')")
        
        # Dữ liệu mẫu cho thuốc
        c.execute("INSERT INTO medicines (name, description, price, stock) VALUES ('Paracetamol 500mg', 'Giảm đau, hạ sốt', 50000.0, 100)")
        c.execute("INSERT INTO medicines (name, description, price, stock) VALUES ('Kháng sinh Amoxicillin', 'Điều trị nhiễm khuẩn', 120000.0, 50)")
        c.execute("INSERT INTO medicines (name, description, price, stock) VALUES ('Vitamin C', 'Bổ sung Vitamin', 35000.0, 200)")


        conn.commit()
        conn.close()

init_db()


# ==================================
# USER MODEL
# ==================================
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


# ==================================
# HELPERS
# ==================================
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# --- HÀM SEND_EMAIL ĐÃ SỬA LỖI GHI NHẬT KÝ ---
def send_email(to, subject, body):
    sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
    mail = Mail(Email(EMAIL_FROM), To(to), subject, Content("text/plain", body))

    try:
        response = sg.client.mail.send.post(request_body=mail.get())
        print(f"EMAIL SENT successfully to {to}, Status Code: {response.status_code}")
    except Exception as e:
        # THÊM: In lỗi ra console để debug
        print(f"EMAIL ERROR: Failed to send email to {to}. Reason: {e}")
# ---------------------------------------------


# ==================================
# ROUTES: AUTH (Không đổi)
# ==================================
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
            c.execute("INSERT INTO users (username,password,role,name,age,email) VALUES (?,?, 'user',?,?,?)",
                      (username, password, name, age, email))
            conn.commit()
            flash("Registration successful!", "success")
            return redirect(url_for('login'))
        except:
            flash("Username already exists!", "danger")
        finally:
            conn.close()

    return render_template('register.html')


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username,password))
        row = c.fetchone()
        conn.close()

        if row:
            user = User(row[0], row[1], row[3], row[4], row[5], row[6])
            login_user(user)

            return redirect(url_for("admin_dashboard" if user.role == "admin" else "user_dashboard"))

        flash("Invalid credentials", "danger")

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# ==================================
# ADMIN DASHBOARD (ĐÃ CẬP NHẬT)
# ==================================
@app.route('/admin')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        return redirect(url_for('user_dashboard'))

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Lấy thông tin bệnh nhân
    c.execute("SELECT name, age, email FROM users WHERE role='user'")
    patients = c.fetchall()

    # Lấy thông tin lịch hẹn
    c.execute("""
        SELECT a.id, u.name, u.email, a.disease, a.datetime, a.status, a.image_path
        FROM appointments a
        JOIN users u ON a.user_id = u.id
    """)
    appointments = c.fetchall()
    
    # Lấy thông tin Thuốc và Đơn hàng
    c.execute("SELECT id, name, price, stock, description FROM medicines ORDER BY name")
    medicines = c.fetchall()
    
    c.execute("""
        SELECT o.id, u.name, m.name, o.quantity, o.total_price, o.order_date, o.status
        FROM orders o
        JOIN users u ON o.user_id = u.id
        JOIN medicines m ON o.medicine_id = m.id
        ORDER BY o.order_date DESC
    """)
    orders = c.fetchall()

    conn.close()

    total_patients = len(patients)
    pending_appt = sum(1 for a in appointments if a[5] == 'pending')
    pending_order = sum(1 for o in orders if o[6] == 'pending')
    
    # Tổng hợp thống kê
    total_items = {
        'total_patients': total_patients,
        'pending_appt': pending_appt,
        'pending_order': pending_order,
        'approved_appt': sum(1 for a in appointments if a[5] == 'approved'),
        'rejected_appt': sum(1 for a in appointments if a[5] == 'rejected'),
        'processed_order': sum(1 for o in orders if o[6] == 'processed'),
    }

    return render_template('admin.html',
                           patients=patients,
                           appointments=appointments,
                           medicines=medicines,
                           orders=orders,
                           stats=total_items)

@app.route('/admin/update_status/<string:type>/<int:item_id>/<string:status>', methods=['POST'])
@login_required
def update_status(type, item_id, status):
    if current_user.role != 'admin':
        return redirect(url_for('user_dashboard'))

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    if type == 'appt':
        c.execute("UPDATE appointments SET status=? WHERE id=?", (status, item_id))
        conn.commit()
        
        # Lấy thông tin lịch hẹn để gửi email
        c.execute("SELECT u.email, u.name, a.disease, a.datetime FROM appointments a JOIN users u ON a.user_id = u.id WHERE a.id = ?", (item_id,))
        row = c.fetchone()
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
                send_email(email_to, subject, body)
        
        flash(f'Appointment {status}', 'success')
        return redirect(url_for('admin_dashboard'))
    
    elif type == 'order':
        # Xử lý đơn hàng: Kiểm tra tồn kho trước khi xử lý
        if status == 'processed':
            c.execute("SELECT m.id, m.stock, o.quantity, u.email, u.name, m.name FROM orders o JOIN medicines m ON o.medicine_id = m.id JOIN users u ON o.user_id = u.id WHERE o.id = ?", (item_id,))
            order_info = c.fetchone()
            if order_info:
                med_id, current_stock, order_qty, email_to, user_name, med_name = order_info
                
                if current_stock >= order_qty:
                    new_stock = current_stock - order_qty
                    c.execute("UPDATE medicines SET stock = ? WHERE id = ?", (new_stock, med_id))
                    c.execute("UPDATE orders SET status = ? WHERE id = ?", (status, item_id))
                    conn.commit()
                    
                    # Gửi email xác nhận xử lý
                    send_email(email_to, "Xử lý Đơn Hàng Thành Công", f"Đơn hàng mua {order_qty}x {med_name} của bạn đã được xử lý thành công. Chúng tôi sẽ sớm giao hàng!")
                    flash(f'Đơn hàng #{item_id} đã được xử lý thành công. Tồn kho mới: {new_stock}', 'success')
                else:
                    flash(f'Lỗi: Thuốc {med_name} không đủ tồn kho ({current_stock} < {order_qty}).', 'danger')
            else:
                flash('Không tìm thấy đơn hàng.', 'danger')
        
        elif status == 'cancelled':
            # Chỉ cập nhật trạng thái
            c.execute("UPDATE orders SET status = ? WHERE id = ?", (status, item_id))
            conn.commit()
            flash(f'Đơn hàng #{item_id} đã bị hủy.', 'success')
            
    conn.close()
    return redirect(url_for('admin_dashboard'))

# Các route quản lý thuốc mới
@app.route('/admin/medicine', methods=['POST'])
@login_required
def manage_medicine():
    if current_user.role != 'admin': return redirect(url_for('user_dashboard'))
    
    name = request.form.get('name')
    price = request.form.get('price', type=float) # Sử dụng type=float
    stock = request.form.get('stock', type=int)   # Sử dụng type=int
    description = request.form.get('description')
    med_id = request.form.get('id')
    
    # Validation cơ bản
    if not name or price is None or stock is None or price < 0 or stock < 0:
        flash('Lỗi: Dữ liệu nhập vào không hợp lệ.', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    try:
        if med_id:
            # Update existing medicine
            c.execute("UPDATE medicines SET name=?, description=?, price=?, stock=? WHERE id=?", 
                      (name, description, price, stock, med_id))
            flash('Cập nhật thuốc thành công!', 'success')
        else:
            # Add new medicine
            c.execute("INSERT INTO medicines (name, description, price, stock) VALUES (?, ?, ?, ?)", 
                      (name, description, price, stock))
            flash('Thêm thuốc mới thành công!', 'success')
        
        conn.commit()
    except sqlite3.IntegrityError:
        flash('Lỗi: Tên thuốc đã tồn tại.', 'danger')
    except Exception as e:
        flash(f'Lỗi: {e}', 'danger')
    finally:
        conn.close()
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/medicine/delete/<int:med_id>', methods=['POST'])
@login_required
def delete_medicine(med_id):
    if current_user.role != 'admin': return redirect(url_for('user_dashboard'))
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM medicines WHERE id=?", (med_id,))
    conn.commit()
    conn.close()
    flash('Đã xóa thuốc thành công!', 'success')
    return redirect(url_for('admin_dashboard'))


# ==================================
# USER DASHBOARD (ĐÃ CẬP NHẬT)
# ==================================
@app.route('/user')
@login_required
def user_dashboard():
    if current_user.role == 'admin':
        return redirect(url_for('admin_dashboard'))

    vn = timezone(timedelta(hours=7))
    now_vn = datetime.now(vn)

    today_date = now_vn.strftime('%Y-%m-%d')
    current_time = now_vn.strftime('%H:%M')

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Lịch hẹn
    c.execute("SELECT disease, datetime, status, image_path, id FROM appointments WHERE user_id=?",
              (current_user.id,))
    appointments = c.fetchall()
    
    # Danh sách Thuốc có sẵn
    c.execute("SELECT id, name, description, price, stock FROM medicines WHERE stock > 0 ORDER BY name")
    medicines = c.fetchall()
    
    # Lịch sử Đơn hàng
    c.execute("""
        SELECT o.id, m.name, o.quantity, o.total_price, o.order_date, o.status
        FROM orders o
        JOIN medicines m ON o.medicine_id = m.id
        WHERE o.user_id = ?
        ORDER BY o.order_date DESC
    """, (current_user.id,))
    orders = c.fetchall()
    
    conn.close()

    return render_template("user.html",
                           appointments=appointments,
                           medicines=medicines,
                           orders=orders,
                           today_date=today_date,
                           current_time=current_time)


@app.route('/order', methods=['POST'])
@login_required
def order_medicine():
    if current_user.role == 'admin': return redirect(url_for('admin_dashboard'))

    med_id = request.form.get('medicine_id', type=int)
    quantity = request.form.get('quantity', type=int)
    
    if quantity is None or quantity <= 0:
        flash("Số lượng không hợp lệ.", "danger")
        return redirect(url_for('user_dashboard'))

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT price, stock, name FROM medicines WHERE id = ?", (med_id,))
    med_info = c.fetchone()
    
    if not med_info:
        conn.close()
        flash("Thuốc không tồn tại.", "danger")
        return redirect(url_for('user_dashboard'))
        
    price, stock, med_name = med_info
    
    if quantity > stock:
        conn.close()
        flash(f"Số lượng tồn kho của {med_name} không đủ. Chỉ còn {stock} đơn vị.", "danger")
        return redirect(url_for('user_dashboard'))
        
    total_price = price * quantity
    order_date = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        c.execute("INSERT INTO orders (user_id, medicine_id, quantity, total_price, order_date, status) VALUES (?, ?, ?, ?, ?, 'pending')",
                  (current_user.id, med_id, quantity, total_price, order_date))
        conn.commit()
        
        # Gửi email xác nhận đơn hàng
        send_email(current_user.email, "Xác nhận Đơn Hàng Mới", f"Anh/Chị {current_user.name}, đơn hàng mua {quantity}x {med_name} của bạn ({total_price:,.0f} VNĐ) đã được tạo thành công và đang chờ xử lý.")

        flash('Đã đặt hàng thành công! Đang chờ xử lý.', 'success')
    except Exception as e:
        flash(f'Lỗi khi tạo đơn hàng: {e}', 'danger')
    finally:
        conn.close()
        
    return redirect(url_for('user_dashboard'))


# Các route cũ (book, uploaded_file, chatbot) không đổi

@app.route('/book', methods=['POST'])
@login_required
def book():
    if current_user.role == 'admin':
        return redirect(url_for('admin_dashboard'))

    disease = request.form['disease']
    date = request.form['date']
    time = request.form['time']

    datetime_str = f"{date} {time}"

    # validate time
    vn = timezone(timedelta(hours=7))
    now_vn = datetime.now(vn)

    try:
        chosen = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M").replace(tzinfo=vn)
        if chosen < now_vn - timedelta(minutes=1):
            flash("Không thể đặt giờ trong quá khứ!", "danger")
            return redirect(url_for('user_dashboard'))
    except:
        flash("Sai định dạng ngày giờ!", "danger")
        return redirect(url_for('user_dashboard'))

    filename = None
    if 'image' in request.files:
        file = request.files['image']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO appointments (user_id,disease,datetime,image_path) VALUES (?,?,?,?)",
              (current_user.id, disease, datetime_str, filename))
    conn.commit()
    conn.close()

    # send email confirm
    send_email(current_user.email, "Xác nhận đặt lịch",
               f"Anh/Chị {current_user.name}, cảm ơn bạn đã đặt lịch!")

    flash("Đặt lịch thành công!", "success")
    return redirect(url_for('user_dashboard'))


# ==================================
# SERVE IMAGE
# ==================================
@app.route('/images/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


# ==================================
# CHATBOT OLLAMA (ĐÃ SỬA STREAMING)
# ==================================
@app.route("/chatbot", methods=["POST"])
@login_required
def chatbot():
    message = request.json.get("message", "")

    if not message:
        return jsonify({"reply": "Bạn muốn hỏi gì ạ? 😊"})

    full_response = ""
    
    try:
        # Gửi request tới Ollama với streaming được bật
        res = requests.post(
            "http://localhost:11434/api/generate",
            # Bật stream=True trong payload để nhận phản hồi theo từng chunk
            json={"model": "gemma3:1b", "prompt": message, "stream": True}, 
            timeout=60,
            stream=True # Bật streaming cho requests
        )
        
        # Lặp qua phản hồi từng dòng
        for line in res.iter_lines():
            if line:
                try:
                    # Parse dòng JSON
                    data = json.loads(line) 
                    
                    # Trích xuất phần 'response'
                    chunk = data.get("response", "")
                    full_response += chunk
                    
                    # Dừng lại nếu hoàn thành (Ollama gửi done: true)
                    if data.get("done"):
                        break
                        
                except json.JSONDecodeError:
                    # Bỏ qua các dòng không phải JSON, ngăn lỗi "Extra data"
                    continue

        return jsonify({"reply": full_response.strip()})
        
    except requests.exceptions.ConnectionError:
        return jsonify({"reply": "Lỗi kết nối: Ollama chưa chạy hoặc bị chặn (cổng 11434)."}), 503
    except Exception as e:
        # Bắt các lỗi khác (như lỗi timeout)
        print(f"Lỗi xử lý Chatbot: {e}")
        return jsonify({"reply": f"Lỗi xử lý LLM: {type(e).__name__}."}), 500


# ==================================
# RUN
# ==================================
if __name__ == "__main__":
    app.run(debug=True)