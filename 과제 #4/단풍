import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
import streamlit as st
import matplotlib.pyplot as plt

# 고도에 따른 기온감률 설정 (약 1000m당 6.5°C 감소)
lapse_rate = 6.5 / 1000

# 단풍 및 기상 데이터 로드
foliage_data = pd.read_csv('fall_2014_2023.csv')
altitude_data = pd.read_csv('mt_height_posit.csv')
weather_data = pd.read_csv('weather_2014_2023.csv')

# 고도 데이터를 포함한 단풍 데이터 병합
foliage_data = foliage_data.merge(altitude_data, on='산', how='left')

# 각 산과 관측 지점 매핑
mountain_to_observation = {
    '북한산': '서울', '오대산': '홍천', '설악산': '인제', '치악산': '원주', '월악산': '제천', '속리산': '보은',
    '계룡산': '대전', '팔공산': '영천', '가야산': '합천', '내장산': '정읍', '지리산': '산청', '무등산': '광주',
    '두륜산': '해남', '한라산': '서귀포'
}

# 단풍 데이터에 관측 지점 추가
foliage_data['관측지점'] = foliage_data['산'].map(mountain_to_observation)

# 8월과 9월 기상 데이터 필터링
august_data = weather_data[weather_data['시점'].astype(str).str.contains('08')]
september_data = weather_data[weather_data['시점'].astype(str).str.contains('09')]

# 각 관측 지점의 8월과 9월 평균 기상 데이터를 저장하는 딕셔너리 생성
august_weather = august_data.groupby('관측지점')[['평균기온(℃)', '합계강수량(mm)', '합계일조시간(hr)']].mean().to_dict(orient='index')
september_weather = september_data.groupby('관측지점')[['평균기온(℃)', '합계강수량(mm)', '합계일조시간(hr)']].mean().to_dict(orient='index')

# 단풍 데이터에 8월과 9월의 기상 정보 추가
foliage_data['8월 평균기온'] = foliage_data['관측지점'].map(lambda x: august_weather.get(x, {}).get('평균기온(℃)', None))
foliage_data['8월 합계강수량'] = foliage_data['관측지점'].map(lambda x: august_weather.get(x, {}).get('합계강수량(mm)', None))
foliage_data['8월 합계일조시간'] = foliage_data['관측지점'].map(lambda x: august_weather.get(x, {}).get('합계일조시간(hr)', None))

foliage_data['9월 평균기온'] = foliage_data['관측지점'].map(lambda x: september_weather.get(x, {}).get('평균기온(℃)', None))
foliage_data['9월 합계강수량'] = foliage_data['관측지점'].map(lambda x: september_weather.get(x, {}).get('합계강수량(mm)', None))
foliage_data['9월 합계일조시간'] = foliage_data['관측지점'].map(lambda x: september_weather.get(x, {}).get('합계일조시간(hr)', None))

# 고도에 따른 8월과 9월 산 정상 기온 계산
foliage_data['8월 산정상 평균기온'] = foliage_data['8월 평균기온'] - (foliage_data['고도(m)'] * lapse_rate)
foliage_data['9월 산정상 평균기온'] = foliage_data['9월 평균기온'] - (foliage_data['고도(m)'] * lapse_rate)

# 최종 feature set 업데이트
X_final = foliage_data[['위도', '경도', '고도(m)', '8월 산정상 평균기온', '9월 산정상 평균기온', '8월 합계강수량', '9월 합계강수량', '8월 합계일조시간', '9월 합계일조시간']]

# 결측값 처리 (선형 보간 사용)
X_final = X_final.interpolate(method='linear')

# 데이터 정규화
scaler = MinMaxScaler()
X_final = scaler.fit_transform(X_final)

# 반응 변수 준비 (단풍 시작일과 절정일을 dayofyear 형식으로 변환)
y_start_final = foliage_data['2023년 단풍시작일'].apply(lambda x: pd.to_datetime(x).dayofyear)
y_peak_final = foliage_data['2023년 단풍절정일'].apply(lambda x: pd.to_datetime(x).dayofyear)

# 2014-2023 데이터로 학습용 데이터 분리
X_train = X_final[:-1]  # 2014-2023 데이터를 학습에 사용
y_train_start = y_start_final.iloc[:-1]  # 단풍 시작일 학습용 데이터
y_train_peak = y_peak_final.iloc[:-1]  # 단풍 절정일 학습용 데이터

# 랜덤 포레스트 모델 정의 (n_estimators를 200으로 증가)
rf_start = RandomForestRegressor(n_estimators=200, random_state=42)
rf_peak = RandomForestRegressor(n_estimators=200, random_state=42)

# 2014-2023 데이터로 랜덤 포레스트 모델 학습
rf_start.fit(X_train, y_train_start)
rf_peak.fit(X_train, y_train_peak)

# 2024년 기상 데이터 로드
weather_2024 = pd.read_csv('weather_2024.csv', encoding='euc-kr')

# '시점' 컬럼을 문자열로 변환하여 필터링에 사용
weather_2024['시점'] = weather_2024['시점'].astype(str)

# 2024년 8월과 9월 기상 데이터 저장하는 딕셔너리 생성
august_weather_2024 = weather_2024[weather_2024['시점'].str.contains('08')].groupby('관측지점')[['평균기온(℃)', '합계강수량(mm)', '합계일조시간(hr)']].mean().to_dict(orient='index')
september_weather_2024 = weather_2024[weather_2024['시점'].str.contains('09')].groupby('관측지점')[['평균기온(℃)', '합계강수량(mm)', '합계일조시간(hr)']].mean().to_dict(orient='index')

# 2024년 예측을 위한 새로운 DataFrame 생성
X_2024 = foliage_data.copy()

# 2024년 8월과 9월의 기상 정보 추가
X_2024['8월 평균기온'] = X_2024['관측지점'].map(lambda x: august_weather_2024.get(x, {}).get('평균기온(℃)', None))
X_2024['8월 합계강수량'] = X_2024['관측지점'].map(lambda x: august_weather_2024.get(x, {}).get('합계강수량(mm)', None))
X_2024['8월 합계일조시간'] = X_2024['관측지점'].map(lambda x: august_weather_2024.get(x, {}).get('합계일조시간(hr)', None))

X_2024['9월 평균기온'] = X_2024['관측지점'].map(lambda x: september_weather_2024.get(x, {}).get('평균기온(℃)', None))
X_2024['9월 합계강수량'] = X_2024['관측지점'].map(lambda x: september_weather_2024.get(x, {}).get('합계강수량(mm)', None))
X_2024['9월 합계일조시간'] = X_2024['관측지점'].map(lambda x: september_weather_2024.get(x, {}).get('합계일조시간(hr)', None))

# 고도에 따른 산 정상 기온 계산
X_2024['8월 산정상 평균기온'] = X_2024['8월 평균기온'] - (X_2024['고도(m)'] * lapse_rate)
X_2024['9월 산정상 평균기온'] = X_2024['9월 평균기온'] - (X_2024['고도(m)'] * lapse_rate)

# 평균 기온 컬럼을 삭제하고 정상 기온을 사용
X_2024.drop(columns=['8월 평균기온', '9월 평균기온'], inplace=True)

# 2024년 예측을 위한 feature set 최종화
X_2024 = X_2024[['위도', '경도', '고도(m)', '8월 산정상 평균기온', '9월 산정상 평균기온', '8월 합계강수량', '9월 합계강수량', '8월 합계일조시간', '9월 합계일조시간']]

# 결측값 처리 (선형 보간 사용)
X_2024 = X_2024.interpolate(method='linear')

# 데이터 정규화
X_2024 = scaler.transform(X_2024)

# 학습된 랜덤 포레스트 모델을 사용하여 2024년 예측 수행
y_pred_start_2024 = rf_start.predict(X_2024)
y_pred_peak_2024 = rf_peak.predict(X_2024)

# 2024년 단풍 예측을 표 형식으로 출력
predictions_2024 = foliage_data[['산']].copy()

# 예측된 값을 2024년 1월 1일을 기준으로 날짜 형식으로 변환
predictions_2024['2024년 단풍시작일'] = pd.to_datetime('2024-01-01') + pd.to_timedelta(y_pred_start_2024 - 1, unit='D')
predictions_2024['2024년 단풍절정일'] = pd.to_datetime('2024-01-01') + pd.to_timedelta(y_pred_peak_2024 - 1, unit='D')

# 인덱스 1부터 시작하도록 설정
predictions_2024.index = range(1, len(predictions_2024) + 1)

# Streamlit 테이블로 출력 (테이블 크기를 전체 너비로 설정)
st.title("2024 Fall Foliage Start and Peak Date Prediction Table")
st.dataframe(predictions_2024, use_container_width=True)

# 2024년 단풍 예측 결과를 터미널에 출력
print("2024년 산별 단풍 예측 결과:")
print(predictions_2024[['산', '2024년 단풍시작일', '2024년 단풍절정일']])

# RMSE 출력
rmse_start = np.sqrt(mean_squared_error(y_train_start, rf_start.predict(X_train)))
rmse_peak = np.sqrt(mean_squared_error(y_train_peak, rf_peak.predict(X_train)))

# Streamlit의 title 설정
st.title("RMSE for 2024 Fall Foliage Start and Peak Date")
st.write(f"RMSE for Start Date: {rmse_start:.2f}")
st.write(f"RMSE for Peak Date: {rmse_peak:.2f}")

# 예측 결과를 DataFrame 형태로 저장합니다.
predictions_2024 = pd.DataFrame({
    'Mountain': ['Seoraksan', 'Odaesan', 'Bukhansan', 'Chiaksan', 'Woraksan', 'Sokrisan',
                 'Gyeryongsan', 'Palgongsan', 'Gayasan', 'Naejangsan', 'Jirisan',
                 'Mudeungsan', 'Duryunsan', 'Hallasan'],
    '2024 Start Date': pd.to_datetime(y_pred_start_2024, unit='D', origin='2024-01-01'),
    '2024 Peak Date': pd.to_datetime(y_pred_peak_2024, unit='D', origin='2024-01-01')
})

# Streamlit의 title 설정
st.title("2024 Fall Foliage Start and Peak Date Prediction Graph")

# 그래프 생성
fig, ax = plt.subplots(figsize=(12, 8))  # 그래프 크기 조정
ax.plot(predictions_2024['2024 Start Date'], label='Start Date', marker='o', color='blue')
ax.plot(predictions_2024['2024 Peak Date'], label='Peak Date', marker='x', color='orange')

# x축 레이블 설정r
ax.set_xticks(range(len(predictions_2024)))  # x축 위치 설정
ax.set_xticklabels(predictions_2024['Mountain'].tolist(), rotation=45, fontsize=10, fontweight='bold')  # 산 이름 설정

# Y축 값 설정
start_date = pd.to_datetime('2024-10-10')  # 시작 날짜 설정
date_range = [start_date + pd.Timedelta(days=i*1) for i in range(0, 30)]  # 5일 간격으로 날짜 생성 
ax.set_yticks(date_range)  # Y축 값 설정
ax.set_yticklabels([date.strftime('%Y-%m-%d') for date in date_range])  # 날짜 형식 설정
ax.set_ylabel("Date", fontsize=12)  # Y축 레이블 추가

# 그래프 제목 및 범례
ax.set_title("2024 Fall Foliage Start and Peak Date Prediction", fontsize=16)
ax.set_xlabel("Mountain", fontsize=12)
ax.legend()

# Streamlit에 그래프 출력
st.pyplot(fig)

import pandas as pd
import folium
import branca.colormap as cm
import streamlit as st
from streamlit_folium import folium_static

# Streamlit 페이지 제목
st.title("2024 Fall Foliage Prediction Map Starting From 10/10")

# 산 위치 데이터 (위도, 경도 파일 로드)
mt_height_posit = pd.read_csv("mt_height_posit.csv", encoding='utf-8')

# 예측 결과를 DataFrame 형태로 저장합니다.
predictions_2024 = pd.DataFrame({
    'Mountain': ['Seoraksan', 'Odaesan', 'Bukhansan', 'Chiaksan', 'Woraksan', 'Sokrisan',
                 'Gyeryongsan', 'Palgongsan', 'Gayasan', 'Naejangsan', 'Jirisan',
                 'Mudeungsan', 'Duryunsan', 'Hallasan'],
    '2024 Start Date': pd.to_datetime(y_pred_start_2024, unit='D', origin='2024-01-01'),
    '2024 Peak Date': pd.to_datetime(y_pred_peak_2024, unit='D', origin='2024-01-01')
})

# 한국어 산 이름을 영어로 변환하는 딕셔너리
mountain_translation = {
    '북한산': 'Bukhansan', '오대산': 'Odaesan', '설악산': 'Seoraksan', '치악산': 'Chiaksan',
    '월악산': 'Woraksan', '속리산': 'Sokrisan', '계룡산': 'Gyeryongsan', '팔공산': 'Palgongsan',
    '가야산': 'Gayasan', '내장산': 'Naejangsan', '지리산': 'Jirisan', '무등산': 'Mudeungsan',
    '두륜산': 'Duryunsan', '한라산': 'Hallasan'
}

# 산 이름을 영어로 변환
mt_height_posit['산'] = mt_height_posit['산'].map(mountain_translation)

# 산 이름을 기준으로 두 데이터 합치기 (위도, 경도 데이터와 예측 결과 합침)
merged_data = pd.merge(mt_height_posit, predictions_2024, left_on='산', right_on='Mountain')

# 단풍 시작일을 날짜의 일수로 변환
min_date = pd.to_datetime("2024-10-10")
max_date = pd.to_datetime("2024-10-25")
merged_data['days_from_min'] = (merged_data['2024 Start Date'] - min_date).dt.days

# 컬러맵 설정 (노란색 -> 빨간색)
colormap = cm.LinearColormap(colors=['yellow', 'red'], vmin=0, vmax=15)

# 지도 생성
map_center = [36.5, 127.5]  # 한국 중심 좌표
m = folium.Map(location=map_center, zoom_start=7)

# 산별로 마커를 추가하면서 색상 설정
for i, row in merged_data.iterrows():
    folium.CircleMarker(
        location=[row['위도'], row['경도']],
        radius=8,
        popup=f"{row['산']}<br>Start: {row['2024 Start Date'].strftime('%Y-%m-%d')}",
        color=colormap(row['days_from_min']),
        fill=True,
        fill_color=colormap(row['days_from_min'])
    ).add_to(m)

# 날짜를 기준으로 하는 컬러바 추가
colormap.caption = 'Foliage Start Date'
colormap.add_to(m)

# 날짜 눈금으로 설정하기 위해 HTML로 컬러바 커스텀
from branca.element import Template, MacroElement

color_scale_template = """
{% macro html(this, kwargs) %}
<div style="
    position: absolute;
    top: 10px;
    left: 10%;
    width: 80%;
    height: 50px;
    background-color: rgba(255, 255, 255, 0.8);
    z-index: 1000;
    font-size: 14px;
    font-weight: bold;
">
    <div style="text-align: center;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span>2024-10-10</span>
            <div style="width: 100%; height: 10px; background: linear-gradient(to right, yellow, red);"></div>
            <span>2024-10-25</span>
        </div>
        <div style="text-align: center;">Foliage Start Date</div>
    </div>
</div>
{% endmacro %}
"""

macro = MacroElement()
macro._template = Template(color_scale_template)

# 지도의 상단에 컬러바를 추가
m.get_root().add_child(macro)

# Streamlit에 지도 표시
folium_static(m)


# 예측 결과를 DataFrame 형태로 저장합니다.
predictions_2024 = pd.DataFrame({
    'Mountain': ['Seoraksan', 'Odaesan', 'Bukhansan', 'Chiaksan', 'Woraksan', 'Sokrisan',
                 'Gyeryongsan', 'Palgongsan', 'Gayasan', 'Naejangsan', 'Jirisan',
                 'Mudeungsan', 'Duryunsan', 'Hallasan'],
    '2024 Start Date': pd.to_datetime(y_pred_start_2024, unit='D', origin='2024-01-01'),
    '2024 Peak Date': pd.to_datetime(y_pred_peak_2024, unit='D', origin='2024-01-01')
})

# 산림청의 50% 물들었을 때의 날짜
forest_service_dates = pd.DataFrame({
    'Mountain': ['Seoraksan', 'Odaesan', 'Bukhansan', 'Chiaksan', 'Woraksan', 'Sokrisan',
                 'Gyeryongsan', 'Palgongsan', 'Gayasan', 'Naejangsan', 'Jirisan',
                 'Mudeungsan', 'Duryunsan', 'Hallasan'],
    'Forest Service Date': pd.to_datetime(['2024-10-22', '2024-10-28', '2024-10-29', '2024-10-28',
                                             '2024-10-30', '2024-10-24', '2024-10-25', '2024-11-01',
                                             '2024-11-06', '2024-10-24', '2024-10-25', '2024-11-08',
                                             '2024-11-05', '2024-10-29'])
})

# 산림청 데이터와 예측 데이터 병합
comparison_data = predictions_2024.merge(forest_service_dates, on='Mountain')

# 50% 물들었을 때의 날짜를 기준으로 20%와 80%의 물들었을 때 날짜 계산
comparison_data['Foliage Start Date (20%)'] = comparison_data['Forest Service Date'] - pd.Timedelta(days=7)
comparison_data['Foliage Peak Date (80%)'] = comparison_data['Forest Service Date'] + pd.Timedelta(days=7)

# Streamlit 제목
st.title('2024 Foliage Start and Peak Date Prediction Comparison with Forest Service')

# 그래프 생성
fig, ax = plt.subplots(figsize=(14, 8))

# 예측된 단풍 시작일과 절정일
ax.plot(comparison_data['Mountain'], comparison_data['2024 Start Date'], label='User Foliage Start Date (20%)', marker='o', color='blue')
ax.plot(comparison_data['Mountain'], comparison_data['2024 Peak Date'], label='User Foliage Peak Date (80%)', marker='x', color='blue')

# 산림청의 20%와 80% 물들었을 때 날짜
ax.plot(comparison_data['Mountain'], comparison_data['Foliage Start Date (20%)'], label='Forest Service Foliage Start Date (20%)', marker='o', color='green')
ax.plot(comparison_data['Mountain'], comparison_data['Foliage Peak Date (80%)'], label='Forest Service Foliage Peak Date (80%)', marker='x', color='green')

# 그래프 세부사항 설정
ax.set_title('2024 Foliage Start and Peak Date Prediction Comparison with Forest Service', fontsize=16)
ax.set_xlabel('Mountain', fontsize=14)
ax.set_ylabel('Date', fontsize=14)
ax.set_xticklabels(comparison_data['Mountain'], rotation=45)
ax.grid(True)
ax.legend()

# 그래프 출력
st.pyplot(fig)

# 기존 예측된 단풍일 데이터 불러오기
# (여기서는 predictions_2024 DataFrame이 있다고 가정합니다)
# 예측 결과를 DataFrame 형태로 저장합니다.
predictions_2024 = pd.DataFrame({
    'Mountain': ['Seoraksan', 'Odaesan', 'Bukhansan', 'Chiaksan', 'Woraksan', 'Sokrisan',
                 'Gyeryongsan', 'Palgongsan', 'Gayasan', 'Naejangsan', 'Jirisan',
                 'Mudeungsan', 'Duryunsan', 'Hallasan'],
    '2024 Start Date': pd.to_datetime(y_pred_start_2024, unit='D', origin='2024-01-01'),
    '2024 Peak Date': pd.to_datetime(y_pred_peak_2024, unit='D', origin='2024-01-01')
})

# 웨더아이 데이터 입력
weathereye_data = {
    'Mountain': ['Seoraksan', 'Odaesan', 'Bukhansan', 'Chiaksan', 'Woraksan',
                 'Sokrisan', 'Gyeryongsan', 'Palgongsan', 'Gayasan', 'Naejangsan',
                 'Jirisan', 'Mudeungsan', 'Duryunsan', 'Hallasan'],
    'Start Date': ['2024-09-29', '2024-10-04', '2024-10-16', '2024-10-09', '2024-10-15',
                   '2024-10-17', '2024-10-16', '2024-10-18', '2024-10-16', '2024-10-24',
                   '2024-10-14', '2024-10-21', '2024-10-29', '2024-10-14'],
    'Peak Date': ['2024-10-20', '2024-10-17', '2024-10-28', '2024-10-23', '2024-10-28',
                  '2024-10-30', '2024-10-29', '2024-10-29', '2024-10-27', '2024-11-05',
                  '2024-10-23', '2024-11-04', '2024-11-11', '2024-10-28']
}

# DataFrame으로 변환
weathereye_df = pd.DataFrame(weathereye_data)

# 날짜 형식 변환
weathereye_df['Start Date'] = pd.to_datetime(weathereye_df['Start Date'])
weathereye_df['Peak Date'] = pd.to_datetime(weathereye_df['Peak Date'])

# 기존 단풍 예측 데이터와 웨더아이 데이터를 산 이름으로 정렬하고 병합
predictions_2024_sorted = predictions_2024.sort_values(by='Mountain').reset_index(drop=True)
weathereye_df_sorted = weathereye_df.sort_values(by='Mountain').reset_index(drop=True)

# Streamlit 시각화
st.title("Comparison of Foliage Predictions with Weather Eye")

# 그래프 그리기
fig, ax = plt.subplots(figsize=(12, 6))

# 기존 예측 결과 선 연결
ax.plot(predictions_2024_sorted['Mountain'], predictions_2024_sorted['2024 Start Date'], marker='o', label='User foliage Start Date', color='blue')
ax.plot(predictions_2024_sorted['Mountain'], predictions_2024_sorted['2024 Peak Date'], marker='x', label='User foliage Peak Date', color='blue')

# 웨더아이 결과 선 연결
ax.plot(weathereye_df_sorted['Mountain'], weathereye_df_sorted['Start Date'], marker='o', label='Weather Eye foliage Start Date', color='red')
ax.plot(weathereye_df_sorted['Mountain'], weathereye_df_sorted['Peak Date'], marker='x', label='Weather Eye foliage Peak Date', color='red')

# 축 레이블 및 제목 설정
ax.set_xlabel('Mountain')
ax.set_ylabel('Date')
ax.set_title('2024 Foliage Start and Peak Dates Comparison with Weather Eye')
ax.legend()

# X축 날짜 형식 설정
ax.set_xticks(range(len(predictions_2024_sorted['Mountain'])))
ax.set_xticklabels(predictions_2024_sorted['Mountain'], rotation=45)

# Y축 범위 설정 및 날짜 간격 설정 (5일 간격)
date_range = pd.date_range(start='2024-09-25', end='2024-11-15', freq='5D')
ax.set_yticks(date_range)
ax.set_yticklabels(date_range.strftime('%Y-%m-%d'))

plt.grid()
st.pyplot(fig)


# 파일 경로에 맞게 데이터 불러오기
weather_2014_2023 = pd.read_csv('weather_2014_2023.csv', encoding='utf-8')  # 2014~2023년도 기상 데이터
mt_height_posit = pd.read_csv('mt_height_posit.csv', encoding='utf-8')  # 산 고도 데이터 파일
weather_2024 = pd.read_csv('weather_2024.csv', encoding='euc-kr')  # 2024년 기상 데이터 파일

# 산과 관측지점 매핑 사전
mountain_to_observation = {
    '서울': '북한산', '홍천': '오대산', '인제': '설악산', '원주': '치악산', '제천': '월악산',
    '보은': '속리산', '대전': '계룡산', '영천': '팔공산', '합천': '가야산', '정읍': '내장산',
    '산청': '지리산', '광주': '무등산', '해남': '두륜산', '서귀포': '한라산'
}

# weather_2014_2023의 '관측지점'을 산 이름으로 매핑
weather_2014_2023['산'] = weather_2014_2023['관측지점'].map(mountain_to_observation)

# 고도 데이터를 포함한 병합 수행
weather_2014_2023 = weather_2014_2023.merge(mt_height_posit, on='산', how='left')

# 고도에 따른 산 정상 평균기온 계산
lapse_rate = 6.5 / 1000  # 고도에 따른 기온감률 (1000m 당 6.5°C 감소)
weather_2014_2023['산정상 평균기온'] = weather_2014_2023['평균기온(℃)'] - (weather_2014_2023['고도(m)'] * lapse_rate)

# 2024년도 데이터도 동일하게 처리
weather_2024['산'] = weather_2024['관측지점'].map(mountain_to_observation)
weather_2024 = weather_2024.merge(mt_height_posit, on='산', how='left')
weather_2024['산정상 평균기온'] = weather_2024['평균기온(℃)'] - (weather_2024['고도(m)'] * lapse_rate)

# 연도별로 평균기온을 계산 (중복된 값 방지)
avg_temp_2014_2023 = weather_2014_2023.groupby('시점')['산정상 평균기온'].mean().reset_index()
avg_temp_2024 = weather_2024.groupby('시점')['산정상 평균기온'].mean().reset_index()

# 2024년 데이터를 추가
comparison_data = pd.concat([avg_temp_2014_2023, avg_temp_2024])

# 스트림릿 시각화를 위한 코드
st.title('Comparison of Peak Temperatures per Year')

# 막대그래프 시각화
plt.figure(figsize=(10, 6))
plt.bar(avg_temp_2014_2023['시점'], avg_temp_2014_2023['산정상 평균기온'], label='2014-2023 Average Peak Temp', color='blue', width=0.4)
plt.bar(avg_temp_2024['시점'], avg_temp_2024['산정상 평균기온'], label='2024 Average Peak Temp', color='red', width=0.4)

# X축과 Y축 구분 및 범위 설정
plt.xlabel('Year')
plt.ylabel('Peak Temperature (°C)')
plt.title('Average Peak Temperature Comparison')

# Y축 범위를 15도에서 25도 사이로 설정
plt.ylim(15, 21)

# 0.1도 간격으로 Y축 틱 설정
y_ticks = np.arange(15, 21, 0.2)
plt.yticks(y_ticks)

# X축을 2014년부터 2024년까지 1년 단위로 구분
plt.xticks(range(2014, 2025))

plt.legend(fontsize='8')

# 그래프를 스트림릿에 표시
st.pyplot(plt)


# 1. 기상 데이터 파일 불러오기 (실제 경로로 수정 필요)
weather_2014_2023 = pd.read_csv('weather_2014_2023.csv',encoding='utf-8')  # 2014-2023 데이터
weather_2024 = pd.read_csv('weather_2024.csv', encoding='euc-kr')  # 2024 데이터

# '시점' 열을 문자열로 변환
weather_2014_2023['시점'] = weather_2014_2023['시점'].astype(str)
weather_2024['시점'] = weather_2024['시점'].astype(str)

# '시점'에서 연도 추출
weather_2014_2023['year'] = weather_2014_2023['시점'].str[:4].astype(int)

# 2014년~2023년 8월, 9월의 강수량 평균 계산
aug_sept_2014_2023 = weather_2014_2023[weather_2014_2023['시점'].str.contains('08|09')]
rainfall_2014_2023_avg = aug_sept_2014_2023.groupby('year')['합계강수량(mm)'].mean()

# 2024년도 8월, 9월의 강수량 평균 계산
aug_sept_2024 = weather_2024[weather_2024['시점'].str.contains('08|09')]
rainfall_2024_avg = aug_sept_2024['합계강수량(mm)'].mean()

# 그래프 그리기
years = list(range(2014, 2025))  # 2014년부터 2024년까지의 연도 (2024년 추가)
rainfall_values = list(rainfall_2014_2023_avg) + [rainfall_2024_avg]  # 2014~2023년도 평균 + 2024년도 평균

# Streamlit으로 앱 구현
st.title("Rainfall Comparison per year")

# 그래프 생성
fig, ax = plt.subplots()
# 2014년부터 2023년까지의 데이터 막대 그래프
ax.bar(years[:-1], rainfall_2014_2023_avg, color='blue', label='2014-2023 Average Total Rainfall', width=0.4)
# 2024년 데이터 막대 그래프
ax.bar(years[-1], rainfall_2024_avg, color='red', label='2024 Average Total Rainfall', width=0.4)
ax.set_xlabel('Year')
ax.set_ylabel('Average Rainfall (mm)')
ax.set_title('Average Rainfall Comparison (August and September)')
ax.set_ylim(0, max(rainfall_values) + 50)  # Y축 범위 설정
ax.set_xticks(years)  # X축에 표시될 연도 설정
# 범례 추가 (라벨 크기 조정)
ax.legend(fontsize='8')  # small, medium, large 등 사용 가능. 또는 숫자(예: 10)로 크기 조절

# Streamlit으로 그래프 출력
st.pyplot(fig)

# 데이터 로드
weather_2014_2023 = pd.read_csv('weather_2014_2023.csv', encoding='utf-8')  # 2014~2023 기상 데이터
weather_2024 = pd.read_csv('weather_2024.csv', encoding='euc-kr')  # 2024 기상 데이터

# '시점' 컬럼에서 연도를 추출하여 'year' 컬럼을 생성
weather_2014_2023['year'] = weather_2014_2023['시점'].astype(str).str[:4].astype(int)
weather_2024['year'] = weather_2024['시점'].astype(str).str[:4].astype(int)

# 8월과 9월 데이터를 필터링
aug_sept_2014_2023 = weather_2014_2023[weather_2014_2023['시점'].astype(str).str.contains('08|09')]
aug_sept_2024 = weather_2024[weather_2024['시점'].astype(str).str.contains('08|09')]

# 2014년부터 2023년까지의 전지역 합계일조시간 평균
sunlight_2014_2023_avg = aug_sept_2014_2023.groupby('year')['합계일조시간(hr)'].mean()

# 2024년의 전지역 합계일조시간 평균
sunlight_2024 = aug_sept_2024['합계일조시간(hr)'].mean()

# 스트림릿 앱
st.title("Sunlight Hours Comparison per Year")

# 2014~2023년의 평균 일조시간과 2024년 일조시간을 시각화하는 막대그래프
fig, ax = plt.subplots()

# 2014~2023년 일조시간 막대 그래프
years = list(sunlight_2014_2023_avg.index)
sunlight_values = list(sunlight_2014_2023_avg) + [sunlight_2024]

# 그래프가 제대로 그려지지 않는 문제 해결을 위해 x와 y 데이터를 명확하게 나눕니다.
ax.bar(years, sunlight_values[:-1], color='blue', label='2014-2023 Average Total Sunlight Hours', width=0.4, align='center')
ax.bar([2024], [sunlight_values[-1]], color='red', label='2024 Average Total Sunlight Hours', width=0.4, align='center')

# 그래프의 제목과 축 라벨 추가
ax.set_title('Average Sunlight Hours per Year')
ax.set_xlabel('Year')
ax.set_ylabel('Total Sunlight Hours (hr)')

# Y축 범위 설정 (예시: 200 ~ 400 시간)
ax.set_ylim(100, 250)

# X축 간격 설정
ax.set_xticks(years + [2024])

# X축 라벨 설정
ax.set_xticklabels(years + [2024])

# 범례 추가
ax.legend(fontsize='8')

# 그래프를 스트림릿 앱에 출력
st.pyplot(fig)


