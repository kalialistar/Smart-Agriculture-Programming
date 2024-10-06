import streamlit as st
import pandas as pd
from datetime import date, timedelta

# 로컬 경로에 있는 CSV 파일을 불러옵니다.
file_path = 'data_file.csv'  # 프로젝트 폴더 내 CSV 파일 경로

# 파일을 읽어서 세션에 저장
if 'data' not in st.session_state:
    st.session_state['data'] = pd.read_csv(file_path, encoding='euc-kr')
data = st.session_state['data']

    # Streamlit 애플리케이션
    st.title('경기도 농기계 임대 시스템')

    # 농기계 목록 및 수량을 먼저 보여줌
    st.write('현재 농기계 보유 현황')
    st.dataframe(data[['시군명', '이앙기수(대)', '트랙터수(대)', '콤바인수(대)', '파종기수(대)', '관리기수(대)']])

    # 농기계 선택을 먼저 하도록 함
    machine_type = st.selectbox('임대할 농기계를 선택하세요', ['이앙기', '트랙터', '콤바인', '파종기', '관리기'])

    # 사용자가 선택할 시 선택 (시군명에서 '시'만 선택)
    location = st.selectbox('임대할 시를 선택하세요', data['시군명'].unique())

    # 사용지 주소 입력 (경기도 + 선택한 시 고정)
    st.subheader('사용지 주소')
    st.text(f'경기도 {location}')
    address_detail = st.text_input('상세 주소를 입력하세요')

    # 임대 정보 입력
    st.subheader('임대 정보 입력')
    name = st.text_input('성함 (개인/업체명)')
    use_start_date = st.date_input('사용 시작 날짜', min_value=date.today())

    # 종료 날짜는 사용자가 시작 날짜를 선택한 후에만 표시되도록 처리
    if use_start_date:
        use_end_date = st.date_input('사용 종료 날짜', min_value=use_start_date + timedelta(days=1), value=use_start_date + timedelta(days=1))

    crop_type = st.text_input('사용 작물 품목')

    # 전화번호 입력 (11자리 강제) - 초기 경고 메시지 제거
    phone_number = st.text_input('전화번호 (11자리)', max_chars=11)
    phone_warning_shown = False  # 경고 메시지를 처음에 보이지 않도록
    if phone_number and len(phone_number) != 11:
        st.error('전화번호는 11자리여야 합니다.')
        phone_warning_shown = True

    # 임대 버튼
    if st.button('농기계 임대하기'):
        if len(phone_number) == 11 and use_start_date <= use_end_date:
            # 선택된 시에 해당하는 데이터 필터링
            selected_row = data[data['시군명'] == location].index[0]

            # 선택한 농기계의 보유 수량 확인
            if machine_type == '이앙기':
                current_count = data.loc[selected_row, '이앙기수(대)']
            elif machine_type == '트랙터':
                current_count = data.loc[selected_row, '트랙터수(대)']
            elif machine_type == '콤바인':
                current_count = data.loc[selected_row, '콤바인수(대)']
            elif machine_type == '파종기':
                current_count = data.loc[selected_row, '파종기수(대)']
            else:
                current_count = data.loc[selected_row, '관리기수(대)']

            # 농기계 수가 0개 이상이면 임대 가능
            if current_count > 0:
                # 농기계 수 줄이기
                st.session_state['data'].loc[selected_row, f'{machine_type}수(대)'] = current_count - 1
                st.success(f'{name}님, {machine_type} 임대 신청이 접수되었습니다. 남은 수량: {current_count - 1}대.')

                # 사용자가 입력한 임대 정보 표시
                st.write('임대 정보:')
                st.write(f'성함 (개인/업체명): {name}')
                st.write(f'사용지 주소: 경기도 {location} {address_detail}')
                st.write(f'사용 기간: {use_start_date} ~ {use_end_date}')
                st.write(f'사용 작물 품목: {crop_type}')
                st.write(f'전화번호: {phone_number}')
            else:
                # 농기계가 0개일 경우, 가장 빠른 반납 날짜 계산
                earliest_return_date = use_end_date + timedelta(days=1)
                st.error(f'{machine_type}은(는) 현재 임대 가능한 수량이 없습니다. '
                         f'가장 빠른 반납일은 {earliest_return_date}일 이후입니다. '
                         f'{earliest_return_date + timedelta(days=1)}일부터 임대 가능합니다.')
        else:
            if not phone_warning_shown:  # 전화번호가 잘못 입력된 경우에만 경고
                st.error('전화번호는 반드시 11자리여야 합니다.')
            if use_start_date > use_end_date:
                st.error('사용 종료 날짜는 사용 시작 날짜 이후여야 합니다.')
else:
    st.error("CSV 파일을 업로드해 주세요.")

