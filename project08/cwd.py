import os
import requests
import vonage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import streamlit as st
import time
import re
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from threading import Thread
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo  # Python 3.9 이상
import matplotlib.font_manager as fm

# ---------------------------------
# 1. API 설정 (stn_id와 auth_key 정의)
# ---------------------------------
auth_key = "njld-D40Rb25Xfg-NAW9hA"  # 발급받은 인증키
stn_id = "146"  # 지점 ID를 고정합니다
url = "https://apihub.kma.go.kr/api/typ01/url/kma_sfctm3.php"

# ---------------------------------
# Streamlit UI에 'Noto Sans KR' 폰트 적용
# ---------------------------------
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR&display=swap" rel="stylesheet">
    <style>
    /* Streamlit 전체에 'Noto Sans KR' 폰트 적용 */
    body, div, span, p, h1, h2, h3, h4, h5, h6 {
        font-family: 'Noto Sans KR', sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------
# matplotlib에서 'Noto Sans KR' 폰트 사용 설정
# ---------------------------------
font_path = 'project08/NotoSansKR-VariableFont_wght.ttf'  # 업로드된 폰트 파일 경로
if os.path.exists(font_path):
    font_prop = fm.FontProperties(fname=font_path)
    plt.rcParams['font.family'] = font_prop.get_name()
    plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 정상 표시
else:
    st.warning("'Noto Sans KR' 폰트 파일을 찾을 수 없습니다. 기본 폰트로 설정됩니다.")
    plt.rcParams['font.family'] = 'DejaVu Sans'
    plt.rcParams['axes.unicode_minus'] = False

# ---------------------------------
# 3. 발신자 이메일과 앱 비밀번호
# ---------------------------------
SENDER_EMAIL = "jbnushading@gmail.com"
SENDER_PASSWORD = "zvrx ilcp jmfv qfrm"

# ---------------------------------
# 4. Vonage API 설정
# ---------------------------------
client = vonage.Client(key="a2b8f260", secret="X1ly0LQHIJRtY1Vp")
sms = vonage.Sms(client)

# ---------------------------------
# 5. 실시간 데이터를 저장할 데이터프레임 생성
# ---------------------------------
data = pd.DataFrame(columns=["시간", "온도 (°C)", "습도 (%)", "일사 (W/m²)", "풍속 (m/s)", "전운 (1/10)"])

# ---------------------------------
# 6. 사용자 알림 상태 저장 (중복 알림 방지)
# ---------------------------------
if 'alert_sent' not in st.session_state:
    st.session_state.alert_sent = {}

# ---------------------------------
# 7. 실시간 기상 데이터 초기화 (session state)
# ---------------------------------
if 'thread_started' not in st.session_state:
    st.session_state.thread_started = False

# ---------------------------------
# 8. 냉해 발생 조건 정의
# ---------------------------------
frost_conditions = {
    "temperature_max": -2,  # 기온 -2°C 이하 (필수)
    "humidity_min": 70,  # 습도 70% 이상 (필수)
    "cloud_amount_max": 3,  # 전운량 3 이하 (필수)
    "wind_speed_threshold": 2,  # 풍속 2m/s 이하 (선택)
    "wind_speed_max": 5,  # 풍속 5m/s 초과 시 알림 제외 (예외)
    "irradiance_threshold_day": 300,  # 일사량 300W/m² 이하 (선택, 오전 9시~오후 6시)
    "irradiance_max_day": 500,  # 일사량 500W/m² 초과 시 알림 제외 (예외)
    "day_start_hour": 9,  # 낮 시작 시간
    "day_end_hour": 18  # 낮 종료 시간
}

# ---------------------------------
# 9. 이메일 및 전화번호 형식 검증 함수
# ---------------------------------
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

def is_valid_phone(phone):
    return re.match(r'^82\d{10}$', phone) is not None

# ---------------------------------
# 10. 발신 이메일 서비스 설정 함수
# ---------------------------------
def get_smtp_settings():
    return {
        'smtp_server': 'smtp.gmail.com',
        'port': 587,
        'email': SENDER_EMAIL,
        'password': SENDER_PASSWORD
    }

# ---------------------------------
# 11. SMS 전송 함수
# ---------------------------------
def send_sms(message, phone_number):
    if phone_number and is_valid_phone(phone_number):
        try:
            to_number = '+' + phone_number  # '+'를 앞에 추가하여 국제 형식으로 변환
            response_data = sms.send_message({
                "from": "AgriFrost",
                "to": to_number,
                "text": message[:70],
                "type": "unicode"
            })
            if response_data["messages"][0]["status"] == "0":
                st.success("SMS 전송 성공!")
            else:
                st.error(f"SMS 전송 실패: {response_data['messages'][0]['error-text']}")
        except Exception as e:
            st.error(f"SMS 전송 실패: {e}")
    elif phone_number and not is_valid_phone(phone_number):
        st.error("올바른 전화번호 형식이 아닙니다. 82로 시작하는 12자리 숫자를 입력하세요.")

# ---------------------------------
# 12. 이메일 발송 함수
# ---------------------------------
def send_email(message, recipient_email):
    smtp_settings = get_smtp_settings()
    if smtp_settings is None:
        st.error("올바른 이메일 서비스를 선택하세요.")
        return

    if recipient_email and is_valid_email(recipient_email):
        try:
            msg = MIMEMultipart()
            msg['From'] = smtp_settings['email']
            msg['To'] = recipient_email
            msg['Subject'] = 'AgriFrost Alert'
            msg.attach(MIMEText(message, 'plain'))

            with smtplib.SMTP(smtp_settings['smtp_server'], smtp_settings['port']) as server:
                server.starttls()
                server.login(smtp_settings['email'], smtp_settings['password'])
                server.sendmail(smtp_settings['email'], recipient_email, msg.as_string())
            st.success("이메일 전송 완료!")
        except Exception as e:
            st.error(f"이메일 전송 오류: {e}")
    elif recipient_email and not is_valid_email(recipient_email):
        st.error("올바른 이메일 형식이 아닙니다.")

# ---------------------------------
# 13. 현재 시간을 기준으로 tm1과 tm2를 설정하는 함수 (한국 시간 기준)
# ---------------------------------
def get_tm1_tm2():
    try:
        # 한국 시간대 설정
        current_time = datetime.now(ZoneInfo("Asia/Seoul"))
    except Exception as e:
        st.error(f"시간대 설정 오류: {e}")
        return None, None

    current_time = current_time.replace(minute=0, second=0, microsecond=0)  # 현재 시간의 정각으로 설정

    # 가장 가까운 8개의 정각 시간 계산 (7시간 전부터 현재 시간까지)
    timestamps = [(current_time - timedelta(hours=i)) for i in range(7, -1, -1)]
    tm1_dt = timestamps[0]
    tm2_dt = timestamps[-1]

    tm1 = tm1_dt.strftime("%Y%m%d%H%M")
    tm2 = tm2_dt.strftime("%Y%m%d%H%M")

    return tm1, tm2

# ---------------------------------
# 14. 텍스트 데이터 파싱 함수
# ---------------------------------
def extract_weather_data(response_text):
    # 데이터 라인 추출 (#으로 시작하지 않는 라인)
    data_lines = [line for line in response_text.splitlines() if not line.startswith('#') and line.strip()]

    # 컬럼 인덱스 정의 (0부터 시작)
    desired_columns = {
        '시간': 0,
        '풍속(m/s)': 3,
        '기온(°C)': 11,
        '습도(%)': 13,
        '일사(MJ/m²)': 34,
        '전운량(1/10)': 25
    }

    weather_data = []

    for line in data_lines:
        # 데이터 라인을 공백으로 분할
        parts = line.split()

        # 데이터 라인의 길이가 충분한지 확인
        if len(parts) < max(desired_columns.values()) + 1:
            st.warning(f"데이터 라인 길이 부족: {line}")
            continue

        try:
            시간 = parts[desired_columns['시간']]
            풍속 = parts[desired_columns['풍속(m/s)']]
            기온 = parts[desired_columns['기온(°C)']]
            습도 = parts[desired_columns['습도(%)']]
            일사 = parts[desired_columns['일사(MJ/m²)']]
            전운량 = parts[desired_columns['전운량(1/10)']]

            # 값이 -9로 표시된 경우 결측치로 간주
            기온 = None if 기온 == '-9' else float(기온)
            습도 = None if 습도 == '-9' else float(습도)
            일사 = None if 일사 == '-9' else max(0.0, float(일사) * 277.78)  # MJ/m² -> W/m² 변환 및 최소 0으로 설정
            풍속 = None if 풍속 == '-9' else float(풍속)
            전운량 = None if 전운량 == '-9' else float(전운량)

            # 시간 문자열을 datetime 객체로 변환 (한국 시간대)
            시간_dt = datetime.strptime(시간, "%Y%m%d%H%M")
            시간_dt = 시간_dt.replace(tzinfo=ZoneInfo("Asia/Seoul")).astimezone(ZoneInfo("Asia/Seoul")).replace(tzinfo=None)

            weather_data.append({
                "time": 시간_dt,
                "온도 (°C)": 기온,
                "습도 (%)": 습도,
                "풍속 (m/s)": 풍속,
                "일사 (W/m²)": 일사,  # 항상 일사량 저장
                "전운 (1/10)": 전운량  # 항상 전운량 저장
            })
        except (IndexError, ValueError) as e:
            st.warning(f"데이터 처리 오류 ({e}): {line}")

    return weather_data

# ---------------------------------
# 15. 8개의 정각 시간을 가져오는 함수
# ---------------------------------
def fetch_past_weather_data():
    tm1, tm2 = get_tm1_tm2()
    if tm1 is None or tm2 is None:
        return None
    params = {
        "tm1": tm1,
        "tm2": tm2,
        "stn": stn_id,  # 여기서 stn_id 사용
        "help": "1",
        "authKey": auth_key
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            response_text = response.text
            st.success(f"데이터 불러오기 성공: {tm1} ~ {tm2}")
            weather_data = extract_weather_data(response_text)
            return weather_data if weather_data else None
        else:
            st.warning(f"데이터 요청에 실패했습니다. 상태 코드: {response.status_code}")
            st.warning(response.text)
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"요청 중 오류 발생: {e}")
        return None

# ---------------------------------
# 16. 낮 시간 여부 확인 함수
# ---------------------------------
def is_daytime(time_point):
    return frost_conditions["day_start_hour"] <= time_point.hour < frost_conditions["day_end_hour"]

# ---------------------------------
# 17. 냉해 발생 조건 체크 및 알림 함수
# ---------------------------------
def check_frost_and_alert(weather_entry, phone_number, recipient_email):
    # 필수 조건
    temperature_condition = weather_entry["온도 (°C)"] is not None and weather_entry["온도 (°C)"] <= frost_conditions["temperature_max"]
    humidity_condition = weather_entry["습도 (%)"] is not None and weather_entry["습도 (%)"] >= frost_conditions["humidity_min"]
    cloud_condition = weather_entry["전운 (1/10)"] is not None and weather_entry["전운 (1/10)"] <= frost_conditions["cloud_amount_max"]

    # 선택 조건
    wind_speed_condition = weather_entry["풍속 (m/s)"] is not None and weather_entry["풍속 (m/s)"] <= frost_conditions["wind_speed_threshold"]

    # 낮 시간일 경우 일사량 조건 적용
    if is_daytime(weather_entry["time"]):
        irradiance_condition = weather_entry["일사 (W/m²)"] is not None and weather_entry["일사 (W/m²)"] <= \
                               frost_conditions["irradiance_threshold_day"]
    else:
        irradiance_condition = True  # 낮 시간이 아니면 일사량 조건 무시

    # 예외 조건
    if weather_entry["풍속 (m/s)"] is not None and weather_entry["풍속 (m/s)"] > frost_conditions["wind_speed_max"]:
        return  # 풍속이 5m/s를 초과하면 알림을 보내지 않음
    if is_daytime(weather_entry["time"]) and weather_entry["일사 (W/m²)"] is not None and weather_entry["일사 (W/m²)"] > \
            frost_conditions["irradiance_max_day"]:
        return  # 낮 시간에 일사량이 500W/m²를 초과하면 알림을 보내지 않음

    # 모든 필수 조건과 선택 조건이 만족될 때만 냉해 가능성
    frost_possible = temperature_condition and humidity_condition and cloud_condition and wind_speed_condition and irradiance_condition

    if frost_possible and "냉해" not in st.session_state.alert_sent:
        alert_message = "경고: 냉해 발생 가능성이 높습니다! 주의하세요."
        send_sms(alert_message, phone_number)
        send_email(alert_message, recipient_email)
        st.session_state.alert_sent["냉해"] = True
    elif not frost_possible and "냉해" in st.session_state.alert_sent:
        del st.session_state.alert_sent["냉해"]

# ---------------------------------
# 18. 실시간 데이터 모니터링 및 업데이트 함수
# ---------------------------------
def monitor_frost(phone_number, recipient_email):
    while st.session_state.get('thread_started', False):
        weather_data = fetch_past_weather_data()
        if weather_data:
            for entry in weather_data:
                update_data(entry)
                check_frost_and_alert(entry, phone_number, recipient_email)
        time.sleep(600)  # 10분마다 업데이트

# ---------------------------------
# 19. 데이터 업데이트 함수
# ---------------------------------
def update_data(new_data):
    global data
    new_data_df = pd.DataFrame({
        "시간": [new_data["time"]],
        "온도 (°C)": [new_data["온도 (°C)"]],
        "습도 (%)": [new_data["습도 (%)"]],
        "풍속 (m/s)": [new_data["풍속 (m/s)"]],
        "일사 (W/m²)": [new_data["일사 (W/m²)"]],
        "전운 (1/10)": [new_data["전운 (1/10)"]]
    })
    data = pd.concat([data, new_data_df], ignore_index=True)
    data.drop_duplicates(subset=["시간"], inplace=True)
    data.sort_values(by="시간", inplace=True)
    data.reset_index(drop=True, inplace=True)

    # 최신 8시간 데이터만 유지
    if len(data) > 8:
        data = data.tail(8)

# ---------------------------------
# 20. X축 레이블 간격 조정 및 데이터가 None인 경우 처리
# ---------------------------------
def plot_graph(parameter, ylabel, actual_color, min_value, max_value, y_ticks, threshold=None, max_threshold=None):

    plt.rc('font', family='Malgun Gothic')  
    plt.rcParams['axes.unicode_minus'] = False  
    
    if data.empty:
        st.write(f"{parameter} 데이터를 가져오는 중입니다...")
        return

    try:
        fig, ax = plt.subplots(figsize=(8, 6))  # 크기를 조정하여 가독성 향상

        # 시간 기준으로 데이터 정렬
        data_sorted = data.sort_values(by="시간")

        # 해당 파라미터 데이터 추가
        ax.plot(data_sorted["시간"], data_sorted[parameter], label=parameter, color=actual_color, marker='o')

        # 기본 임계값 선 추가
        if threshold is not None:
            ax.axhline(y=threshold, color='green', linestyle='--', label=f'임계값 ({threshold})')

        # 최대 임계값 선 추가
        if max_threshold is not None:
            ax.axhline(y=max_threshold, color='red', linestyle=':', label=f'최대 임계값 ({max_threshold})')

        ax.set_xlabel("시간", fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)

        # X축 레이블 간격 조정
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))  # 1시간 간격으로 표시
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        fig.autofmt_xdate(rotation=45)  # X축 레이블 회전

        # Y축 범위 설정 및 틱 설정
        ax.set_ylim(min_value, max_value)
        ax.set_yticks(y_ticks)

        # 배경을 흰색으로 설정
        ax.set_facecolor('white')
        fig.patch.set_facecolor('white')

        # 레전드를 그래프 내 우측 상단에 배치
        ax.legend(loc='upper right', fontsize='small')

        plt.title(f"{parameter} 모니터링", fontsize=14)
        st.pyplot(fig)
    except Exception as e:
        st.error(f"그래프를 그리는 중 오류가 발생했습니다: {e}")

# ---------------------------------
# 21. 실시간 데이터를 업데이트하고 그래프를 그리는 함수
# ---------------------------------
def update_and_plot_graphs():
    if data.empty:
        weather_data = fetch_past_weather_data()
        if weather_data:
            for entry in weather_data:
                update_data(entry)

    tabs = st.tabs(["외부 기온", "외부 습도", "풍속", "일사량", "전운량"])

    with tabs[0]:
        plot_graph(
            parameter="온도 (°C)",
            ylabel="온도 (°C)",
            actual_color="#FF0000",
            min_value=-10,
            max_value=40,
            y_ticks=list(range(-10, 41, 5)),
            threshold=frost_conditions["temperature_max"],
            max_threshold=None  # 온도는 최대 임계값이 없음
        )

    with tabs[1]:
        plot_graph(
            parameter="습도 (%)",
            ylabel="습도 (%)",
            actual_color="#0000FF",
            min_value=0,
            max_value=100,
            y_ticks=list(range(0, 101, 10)),
            threshold=frost_conditions["humidity_min"],
            max_threshold=None  # 습도는 최대 임계값이 없음
        )

    with tabs[2]:
        plot_graph(
            parameter="풍속 (m/s)",
            ylabel="풍속 (m/s)",
            actual_color="#800080",
            min_value=0,
            max_value=10,
            y_ticks=list(range(0, 11, 1)),
            threshold=frost_conditions["wind_speed_threshold"],
            max_threshold=frost_conditions["wind_speed_max"]
        )

    with tabs[3]:
        # 현재 시간이 낮 시간인지 확인 (한국 시간 기준)
        try:
            current_time = datetime.now(ZoneInfo("Asia/Seoul"))
        except Exception as e:
            st.error(f"시간대 설정 오류: {e}")
            return

        if frost_conditions["day_start_hour"] <= current_time.hour < frost_conditions["day_end_hour"]:
            threshold = frost_conditions["irradiance_threshold_day"]
            max_threshold = frost_conditions["irradiance_max_day"]
        else:
            threshold = None
            max_threshold = None

        plot_graph(
            parameter="일사 (W/m²)",
            ylabel="일사량 (W/m²)",
            actual_color="#FFD700",
            min_value=0,  # 최소값을 0으로 고정
            max_value=1000,
            y_ticks=list(range(0, 1001, 100)),
            threshold=threshold,
            max_threshold=max_threshold
        )

    with tabs[4]:
        plot_graph(
            parameter="전운 (1/10)",
            ylabel="전운량 (1/10)",
            actual_color="#808080",
            min_value=0,  # Y축 시작을 0으로 설정하여 모든 데이터 포인트 표시
            max_value=10,  # Y축 끝을 10으로 설정
            y_ticks=list(range(0, 11, 1)),
            threshold=frost_conditions["cloud_amount_max"],
            max_threshold=None  # 전운량은 최대 임계값이 없음
        )

    # 그래프 아래에 데이터프레임 표시하지 않음

# ---------------------------------
# 22. Streamlit UI 설정
# ---------------------------------
st.markdown(
    """
    <style>
    .title {
        font-size: 35px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
        width: 100%;
    }
    </style>
    <div class="title">냉해 모니터링 및 알림 시스템</div>
    """,
    unsafe_allow_html=True
)

# ---------------------------------
# 23. 사용자 입력
# ---------------------------------
recipient_phone = st.text_input('전화번호 입력 (82로 시작하는 12자리 숫자, 예: 821012345678)', max_chars=12)
recipient_email = st.text_input('수신 이메일 입력')

# ---------------------------------
# 24. 모니터링 시작 버튼
# ---------------------------------
if st.button('모니터링 시작') and not st.session_state.get('thread_started', False):
    if not (recipient_phone or recipient_email):
        st.error("전화번호 또는 이메일을 입력하세요.")
    else:
        valid_phone = is_valid_phone(recipient_phone)
        valid_email = is_valid_email(recipient_email)

        if valid_phone or valid_email:
            if valid_phone:
                send_sms("냉해 모니터링이 시작되었습니다.", recipient_phone)
            if valid_email:
                send_email("냉해 모니터링이 시작되었습니다.", recipient_email)

            thread = Thread(target=monitor_frost, args=(recipient_phone, recipient_email), daemon=True)
            thread.start()
            st.session_state.thread_started = True
            st.success("모니터링이 시작되었습니다.")

# ---------------------------------
# 25. Streamlit UI (모니터링 시작 후 추가 UI 표시 부분)
# ---------------------------------
if st.session_state.get('thread_started', False):
    st.markdown("---")

    # "모니터링 중지" 버튼 추가
    if st.button("모니터링 중지"):
        st.session_state.thread_started = False
        st.experimental_rerun()

    # 그래프 시각화
    st.subheader("실시간 기상 데이터 그래프")
    update_and_plot_graphs()

    # 최근 8시간 기상 데이터 테이블 표시
    st.subheader("최근 8시간 기상 데이터")

    # 데이터 표시 준비
    if not data.empty:
        data_display = data.copy()
        # '시간' 컬럼 포맷팅
        data_display['시간'] = data_display['시간'].dt.strftime('%Y-%m-%d %H:%M')
        # 컬럼 순서 재정렬 (선택 사항)
        data_display = data_display[["시간", "온도 (°C)", "습도 (%)", "풍속 (m/s)", "일사 (W/m²)", "전운 (1/10)"]]
        # 데이터프레임 표시
        st.dataframe(data_display.reset_index(drop=True))
    else:
        st.write("기상 데이터를 가져오는 중입니다...")


