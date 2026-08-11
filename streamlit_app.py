import streamlit as st
import pandas as pd
import numpy as np
import datetime

st.set_page_config(page_title="Webapp Phân Công Lịch Trực SGN", layout="wide")

# --- HỆ THỐNG XÁC THỰC 2 BƯỚC ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.step = "ENTER_EMAIL" # Các bước: ENTER_EMAIL, ENTER_PASSWORD
    st.session_state.temp_email = ""
    st.session_state.user_role = ""

# Cơ sở dữ liệu Admin (Email -> Password)
ADMIN_DB = {
    "duongnikie@gmail.com": "aDuong@123",
    "duongth@vietravelairlines.vn": "123456"
}

if not st.session_state.logged_in:
    st.title("🔐 Đăng Nhập Hệ Thống")
    
    # BƯỚC 1: NHẬP EMAIL
    if st.session_state.step == "ENTER_EMAIL":
        with st.form("email_form"):
            email = st.text_input("Nhập địa chỉ Email", placeholder="ví dụ: admin@vietravelairlines.vn")
            submitted = st.form_submit_button("Tiếp tục")
            
            if submitted:
                if email:
                    clean_email = email.strip().lower()
                    st.session_state.temp_email = clean_email
                    
                    # Kiểm tra xem có phải Admin không
                    if clean_email in ADMIN_DB:
                        st.session_state.step = "ENTER_PASSWORD"
                    else:
                        # Không phải Admin -> Đăng nhập thẳng với quyền Viewer
                        st.session_state.logged_in = True
                        st.session_state.user_role = "Người xem (Viewer)"
                    st.rerun()
    
    # BƯỚC 2: NHẬP MẬT KHẨU (Nếu là Admin)
    elif st.session_state.step == "ENTER_PASSWORD":
        st.markdown(f"📧 Tài khoản: **{st.session_state.temp_email}** (Admin)")
        with st.form("password_form"):
            password = st.text_input("Nhập mật khẩu", type="password")
            col1, col2 = st.columns([1, 4])
            with col1:
                back_btn = st.form_submit_button("Quay lại")
            with col2:
                login_btn = st.form_submit_button("Đăng nhập")
            
            if back_btn:
                st.session_state.step = "ENTER_EMAIL"
                st.rerun()
            
            if login_btn:
                if password == ADMIN_DB.get(st.session_state.temp_email):
                    st.session_state.logged_in = True
                    st.session_state.user_role = "Admin"
                    st.rerun()
                else:
                    st.error("❌ Mật khẩu không chính xác!")
    
    st.stop() # Dừng lại nếu chưa đăng nhập thành công

# --- PHẦN APP CHÍNH (Sau khi đăng nhập) ---
st.sidebar.markdown(f"👤 **Email:** {st.session_state.temp_email if st.session_state.temp_email else 'Viewer'}")
st.sidebar.markdown(f"🛡️ **Quyền:** `{st.session_state.user_role}`")
if st.sidebar.button("🚪 Đăng Xuất"):
    st.session_state.logged_in = False
    st.session_state.step = "ENTER_EMAIL"
    st.session_state.temp_email = ""
    st.session_state.user_role = ""
    st.rerun()

st.sidebar.markdown("---")

# --- LOGIC CỦA APP (Giữ nguyên các chức năng cũ) ---
st.title("🛫 Webapp Quản Lý & Phân Công Lịch Trực Headset SGN")
st.markdown("Hệ thống quản lý lịch trực **(Xem lịch theo tuần - Đầu tuần chuẩn Thứ 2, tối thiểu 4 người trực/ngày, cân bằng OT, đồng bộ GMT+7)**.")

staffs = ['HS1', 'HS2', 'HS3', 'HS4', 'HS5']
shifts = ['S1', 'S2', 'S3', 'S4']
shift_info = {
    'S1': {'name': 'Ca 1 (Sáng)', 'time': '04:20 - 14:20', 'hours': 10},
    'S2': {'name': 'Ca 2 (Chiều 1)', 'time': '11:35 - 21:35', 'hours': 10},
    'S3': {'name': 'Ca 3 (Chiều 2)', 'time': '12:10 - 22:10', 'hours': 10},
    'S4': {'name': 'Ca 4 (Tối)', 'time': '16:25 - 00:25', 'hours': 8},
    'Nghỉ': {'name': 'Nghỉ định kỳ', 'time': '-', 'hours': 0},
    'Nghỉ (Đột xuất)': {'name': 'Nghỉ đột xuất', 'time': '-', 'hours': 0}
}

# Đồng bộ thời gian thực GMT+7
tz_vn = datetime.timezone(datetime.timedelta(hours=7))
now_vn = datetime.datetime.now(tz_vn)
current_year = now_vn.year
current_month = now_vn.month

month_options = []
for i in range(-6, 3):
    target_y = current_year
    target_m = current_month + i
    while target_m > 12:
        target_m -= 12
        target_y += 1
    while target_m < 1:
        target_m += 12
        target_y -= 1
        
    m_str = f"Tháng {target_m}/{target_y}"
    if m_str not in month_options:
        month_options.append(m_str)

def parse_month_str(m_str):
    parts = m_str.replace("Tháng ", "").split("/")
    return int(parts[1]), int(parts[0])

month_options.sort(key=parse_month_str)
current_month_str = f"Tháng {current_month}/{current_year}"

# Sidebar chọn thời gian
st.sidebar.header("📅 Chọn Thời Gian")
default_idx = month_options.index(current_month_str) if current_month_str in month_options else len(month_options)-1
selected_month = st.sidebar.selectbox("Chọn tháng trực", month_options, index=default_idx)

sel_year, sel_month = parse_month_str(selected_month)
is_past_month = (sel_year < current_year) or (sel_year == current_year and sel_month < current_month)

# Phân quyền menu tùy thuộc vào Role (Admin hay Viewer) và Tháng cũ/mới
st.sidebar.markdown("---")
st.sidebar.header("🛠️ Quản lý Lịch")

if st.session_state.user_role == "Admin":
    if is_past_month:
        st.sidebar.warning(f"🔒 **{selected_month}** đã qua (Chỉ xem).")
        menu_options = ["Xem Lịch Theo Tuần", "Xem Chi Tiết Theo Ngày", "Thống Kê Giờ Làm Việc"]
    else:
        st.sidebar.success(f"🔓 **{selected_month}** (Toàn quyền Admin).")
        menu_options = ["Xem Lịch Theo Tuần", "Xem Chi Tiết Theo Ngày", "Xử lý Nghỉ Đột Xuất (Emergency Leave)", "Thống Kê Giờ Làm Việc"]
else:
    st.sidebar.info("👁️ Chế độ Người xem (Chỉ đọc).")
    menu_options = ["Xem Lịch Theo Tuần", "Xem Chi Tiết Theo Ngày", "Thống Kê Giờ Làm Việc"]

menu = st.sidebar.selectbox("Chọn chức năng", menu_options)

# Hàm tạo lịch
@st.cache_data
def generate_roster_for_month(month_str):
    y, m = parse_month_str(month_str)
    start_date = datetime.date(y, m, 1)
    if m == 12:
        next_month_start = datetime.date(y + 1, 1, 1)
    else:
        next_month_start = datetime.date(y, m + 1, 1)
    periods = (next_month_start - start_date).days

    dates = pd.date_range(start=start_date, periods=periods, freq='D')
    days_vn = {'Monday': 'T2', 'Tuesday': 'T3', 'Wednesday': 'T4', 'Thursday': 'T5', 'Friday': 'T6', 'Saturday': 'T7', 'Sunday': 'CN'}
    
    np.random.seed(y * 100 + m)
    roster_data = []
    date_to_col = {}
    
    off_counts = {s: 0 for s in staffs}
    cumulative_hours = {s: 0 for s in staffs}
    night_count = {s: 0 for s in staffs}
    force_rest = {s: False for s in staffs}
    force_s1 = {s: False for s in staffs}
    
    for idx, d in enumerate(dates):
        num_off = 1 
        off_staffs = []
        
        for s in staffs:
            if force_rest[s] and len(off_staffs) < num_off:
                off_staffs.append(s)
                force_rest[s] = False
                force_s1[s] = True
                night_count[s] = 0
                
        if not off_staffs:
            candidates = sorted(staffs, key=lambda x: (off_counts[x], cumulative_hours[x]))
            s_off = candidates[0]
            off_staffs.append(s_off)
            night_count[s_off] = max(0, night_count[s_off] - 1)
            
        for s in off_staffs:
            off_counts[s] += 1
            
        working_staffs = [s for s in staffs if s not in off_staffs]
        active_shifts = list(shifts)
        
        shift_assignment = {}
        rem_staff = list(working_staffs)
        
        for s in working_staffs:
            if force_s1[s] and 'S1' in active_shifts:
                shift_assignment['S1'] = s
                active_shifts.remove('S1')
                rem_staff.remove(s)
                force_s1[s] = False
                
        rem_staff.sort(key=lambda x: cumulative_hours[x])
        for sh in active_shifts:
            if rem_staff:
                s = rem_staff.pop(0)
                shift_assignment[sh] = s
                
        for sh, s in shift_assignment.items():
            cumulative_hours[s] += shift_info[sh]['hours']
            if sh == 'S4':
                night_count[s] += 1
                if night_count[s] >= 2:
                    force_rest[s] = True
            else:
                night_count[s] = 0
                
        col_name = f"{d.strftime('%d/%m')} ({days_vn[d.strftime('%A')]})"
        date_to_col[d.date()] = col_name
        
        for s in staffs:
            if s in off_staffs:
                assign = 'Nghỉ'
            else:
                assign = [sh for sh, assigned_s in shift_assignment.items() if assigned_s == s][0]
            roster_data.append({'Staff': s, 'Date': col_name, 'RawDate': d.date(), 'Assignment': assign})
            
    df_long = pd.DataFrame(roster_data)
    df_wide = df_long.pivot(index='Staff', columns='Date', values='Assignment')
    return df_wide, start_date, (start_date + datetime.timedelta(days=periods-1)), date_to_col, dates

if 'roster_dict' not in st.session_state:
    st.session_state.roster_dict = {}

if selected_month not in st.session_state.roster_dict:
    st.session_state.roster_dict[selected_month] = generate_roster_for_month(selected_month)

current_roster, min_date, max_date, date_to_col, month_dates = st.session_state.roster_dict[selected_month]

# --- Giao diện chức năng ---
if menu == "Xem Lịch Theo Tuần":
    st.subheader(f"📅 Lịch Trực Theo Tuần (Đầu tuần: Thứ Hai) - {selected_month}")
    
    all_cols = list(current_roster.columns)
    weeks = []
    current_week_cols = []
    
    for d, col in zip(month_dates, all_cols):
        if d.weekday() == 0 and current_week_cols:
            weeks.append(current_week_cols)
            current_week_cols = []
        current_week_cols.append(col)
    if current_week_cols:
        weeks.append(current_week_cols)
        
    week_options = [f"Tuần {i+1} ({w[0].split(' ')[0]} - {w[-1].split(' ')[0]})" for i, w in enumerate(weeks)]
    selected_week_label = st.selectbox("Chọn tuần xem lịch", week_options)
    
    selected_week_idx = week_options.index(selected_week_label)
    cols_in_week = weeks[selected_week_idx]
    
    st.dataframe(current_roster[cols_in_week], use_container_width=True)
    st.info("💡 **Chú thích ca trực:**\n- **S1**: Ca 1 (10h)\n- **S2**: Ca 2 (10h)\n- **S3**: Ca 3 (10h)\n- **S4**: Ca 4 / Tối (8h)")

elif menu == "Xem Chi Tiết Theo Ngày":
    st.subheader(f"🔍 Xem Chi Tiết Lịch Trực Theo Ngày ({selected_month})")
    picked_date = st.date_input("Chọn ngày xem lịch trực", value=min_date, min_value=min_date, max_value=max_date)
    
    if picked_date in date_to_col:
        chosen_col = date_to_col[picked_date]
        st.markdown(f"### 📋 Chi tiết lịch trực ngày: **{picked_date.strftime('%d/%m/%Y')} ({chosen_col.split(' ')[-1]})**")
        
        day_data = current_roster[chosen_col]
        detail_records = []
        for s in staffs:
            code = day_data[s]
            info = shift_info.get(code, {'name': code, 'time': '-', 'hours': 0})
            detail_records.append({
                'Nhân sự': s,
                'Mã ca': code,
                'Tên ca trực': info['name'],
                'Khung giờ': info['time'],
                'Số giờ': info['hours']
            })
            
        df_detail = pd.DataFrame(detail_records)
        st.dataframe(df_detail, use_container_width=True)

elif menu == "Xử lý Nghỉ Đột Xuất (Emergency Leave)":
    st.subheader(f"🚨 Xử Lý Nhân Sự Nghỉ Đột Xuất & Phân Chia Lại Ca ({selected_month})")
    col1, col2 = st.columns(2)
    with col1:
        leave_date = st.date_input("Chọn ngày nghỉ đột xuất", value=min_date, min_value=min_date, max_value=max_date, key="emergency_date")
    with col2:
        staff_on_leave = st.selectbox("Chọn nhân sự xin nghỉ đột xuất", staffs)
        
    if st.button("🔄 Xử lý & Phân công lại tự động"):
        if leave_date in date_to_col:
            selected_date_col = date_to_col[leave_date]
            current_assignment = current_roster.loc[staff_on_leave, selected_date_col]
            
            if 'Nghỉ' in current_assignment:
                st.warning(f"Nhân sự **{staff_on_leave}** vào ngày đã là **Nghỉ**.")
            else:
                day_col = current_roster[selected_date_col]
                off_staffs = [s for s, val in day_col.items() if val == 'Nghỉ' and s != staff_on_leave]
                
                if off_staffs:
                    replacement = off_staffs[0]
                    st.success(f"Đã phân công **{replacement}** thay thế ca của **{staff_on_leave}**.")
                    current_roster.loc[staff_on_leave, selected_date_col] = 'Nghỉ (Đột xuất)'
                    current_roster.loc[replacement, selected_date_col] = current_assignment
                else:
                    st.error("Không có nhân sự đang nghỉ để thay thế.")

    st.markdown("---")
    st.subheader("Bảng Lịch Trực Sau Cập Nhật")
    st.dataframe(current_roster, use_container_width=True)

elif menu == "Thống Kê Giờ Làm Việc":
    st.subheader(f"📊 Thống Kê Giờ Làm Việc & Cân Bằng OT - {selected_month}")
    st.markdown("Quy định chuẩn: **Chuẩn 40 giờ/tuần**. **Số ngày OT** được tính bằng **Tổng số giờ OT chia cho 8**.")
    
    total_days_in_month = len(current_roster.columns)
    num_weeks = total_days_in_month / 7.0
    standard_monthly_hours = 40.0 * num_weeks
    
    stats_data = []
    cols = list(current_roster.columns)
    for s in staffs:
        total_hours = 0
        total_days = 0
        
        for col in cols:
            val = current_roster.loc[s, col]
            if val in shift_info:
                hrs = shift_info[val]['hours']
                total_hours += hrs
                if hrs > 0:
                    total_days += 1
                        
        ot_hours = max(0.0, total_hours - standard_monthly_hours)
        ot_days = ot_hours / 8.0 
        
        stats_data.append({
            'Nhân sự': s,
            'Tổng ngày công': total_days,
            'Tổng số giờ làm': total_hours,
            'Giờ chuẩn (Tháng)': round(standard_monthly_hours, 1),
            'Số giờ OT': round(ot_hours, 1),
            'Số ngày OT (Quy đổi / 8h)': round(ot_days, 2)
        })
        
    df_stats = pd.DataFrame(stats_data)
    st.dataframe(df_stats, use_container_width=True)
    
    st.markdown("### Biểu đồ so sánh Tổng Giờ Làm và Số Giờ OT")
    st.bar_chart(df_stats.set_index('Nhân sự')[['Tổng số giờ làm', 'Số giờ OT']])