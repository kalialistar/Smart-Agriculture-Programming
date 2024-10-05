import os

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import numpy as np
import requests
import pandas as pd

import csv
from datetime import datetime
import math

def get_data(sy, ey):  # -> api를 통해서 데이터 받아오기
    station_dic = {'Icheon':203, 'Cheonan':232, 'Sangju':137, 'Yeongcheon':281}

    for station, station_code in station_dic.items():

        print(station, station_code)
        for i in range(ey+1-sy):
            url = f'https://api.taegon.kr/stations/{station_code}/'

            params = {
                'sy' : sy+i,
                'ey' : sy+i,
                format : 'csv'
            }

            response = requests.get(url, params=params, verify=False)
            if response.status_code == 200:
                content = response.json()
                df = pd.DataFrame(content)

                if not os.path.exists(f'output/{station}'):
                    os.makedirs(f'output/{station}')

                df.to_csv(f'output/{station}/{station}_{sy+i}')
                print(f'{sy+i}년도 데이터 저장 완료.')
            else:
                print(response.status_code)

def DVR_model(): # --> DVR모델
    output_path = 'output'
    output_list = os.listdir(output_path)

    # output_list = ['naju'] # 테스트를 위한 데이터 정리
    for output_folder in output_list:
        file_list = os.listdir(os.path.join(output_path, output_folder))
        file_list.sort()
        flowering_df = pd.DataFrame()

        for file in file_list: #하나의 파일 ex.Icheon_2004
            print(file)
            if not (f'png' in file or f'DVS_{output_folder}_model.csv' in file or 'input' in file or 'cd' in file or 'flowering_date' in file or 'mDVR' in file):
                if file != f'DVS_{output_folder}_model.csv':
                    df = pd.read_csv(os.path.join(output_path, output_folder, file))

                    # DVR모델 계산
                    pear_a = 107.94
                    pear_b = 0.9

                    DVS = 0
                    for i in range(len(df)):
                        if df.iloc[i]['tavg'] >= 5:

                            DVRi = (1 / (pear_a * (pear_b ** df.iloc[i]['tavg']))) * 100
                            DVS += DVRi

                            if DVS >= 100:

                                dic = {'Station':output_folder, 'Date': df.iloc[i]['Date'], 'DVS':DVS}
                                df_save = pd.DataFrame([dic])

                                flowering_df = pd.concat([flowering_df, df_save])
                                break
                    flowering_df.to_csv(f'output/{output_folder}/DVS_{output_folder}_model.csv')

                else:
                    pass

# 지역별로 실제 만개일 정리
def get_flowering_date():
    input_file = 'obs_date.txt'
    output_file = 'flowering_date.csv'

    # txt 파일에서 데이터를 읽어와 csv로 변환
    with open(input_file, 'r', encoding='utf-8') as txt_file, open(output_file, 'w', newline='',
                                                                   encoding='utf-8') as csv_file:

        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['생육일조사지역', '만개기'])

        # 각 줄을 읽어 필요한 부분만 추출
        for line in txt_file:
            columns = line.strip().split()  # 공백으로 분리
            if len(columns) >= 3 and columns[0] != '생육일조사지역':  # 유효한 데이터인 경우만 처리
                # 생육일조사지역과 만개기 추출
                region = columns[0]
                flowering_date = columns[2]
                csv_writer.writerow([region, flowering_date])

    df = pd.read_csv('flowering_date.csv')

    df_naju = pd.DataFrame()
    df_icheon = pd.DataFrame()
    df_cheonan = pd.DataFrame()
    df_sangju = pd.DataFrame()
    df_yoengcheon = pd.DataFrame()
    df_wanju = pd.DataFrame()
    df_ulju = pd.DataFrame()
    df_sacheon = pd.DataFrame()

    for i in range(len(df)):
        print(df.iloc[i])
        if df.iloc[i]['생육일조사지역'] == '나주':
            dic_naju = {'station':'naju', 'year':df.iloc[i]['만개기'].split('-')[0], 'Date':df.iloc[i]['만개기']}
            df_dic = pd.DataFrame([dic_naju])
            df_naju = pd.concat([df_naju, df_dic])

        elif df.iloc[i]['생육일조사지역'] == '이천':
            dic_icheon = {'station':'icheon', 'year':df.iloc[i]['만개기'].split('-')[0], 'Date':df.iloc[i]['만개기']}
            df_dic = pd.DataFrame([dic_icheon])
            df_icheon = pd.concat([df_icheon, df_dic])

        elif df.iloc[i]['생육일조사지역'] == '천안':
            dic_cheonan = {'station':'cheonan', 'year':df.iloc[i]['만개기'].split('-')[0], 'Date':df.iloc[i]['만개기']}
            df_dic = pd.DataFrame([dic_cheonan])
            df_cheonan = pd.concat([df_cheonan, df_dic])

        elif df.iloc[i]['생육일조사지역'] == '상주':
            dic_sangju = {'station':'sangju', 'year':df.iloc[i]['만개기'].split('-')[0], 'Date':df.iloc[i]['만개기']}
            df_dic = pd.DataFrame([dic_sangju])
            df_sangju = pd.concat([df_sangju, df_dic])

        elif df.iloc[i]['생육일조사지역'] == '영천':
            dic_yoengcheon = {'station':'yoengcheon', 'year':df.iloc[i]['만개기'].split('-')[0], 'Date':df.iloc[i]['만개기']}
            df_dic = pd.DataFrame([dic_yoengcheon])
            df_yoengcheon = pd.concat([df_yoengcheon, df_dic])

        elif df.iloc[i]['생육일조사지역'] == '완주':
            dic_wanju = {'station':'wanju', 'year':df.iloc[i]['만개기'].split('-')[0], 'Date':df.iloc[i]['만개기']}
            df_dic = pd.DataFrame([dic_wanju])
            df_wanju = pd.concat([df_wanju, df_dic])

        elif df.iloc[i]['생육일조사지역'] == '울산':
            dic_ulju = {'station':'ulju', 'year':df.iloc[i]['만개기'].split('-')[0], 'Date':df.iloc[i]['만개기']}
            df_dic = pd.DataFrame([dic_ulju])
            df_ulju = pd.concat([df_ulju, df_dic])

        elif df.iloc[i]['생육일조사지역'] == '사천':
            dic_sacheon = {'station':'sacheon', 'year':df.iloc[i]['만개기'].split('-')[0], 'Date':df.iloc[i]['만개기']}
            df_dic = pd.DataFrame([dic_sacheon])
            df_sacheon = pd.concat([df_sacheon, df_dic])

    df_naju.to_csv('output/naju/flowering_date_naju.csv')
    df_icheon.to_csv('output/Icheon/flowering_date_Icheon.csv')
    df_cheonan.to_csv('output/Cheonan/flowering_date_Cheonan.csv')
    df_sangju.to_csv('output/Sangju/flowering_date_Sangju.csv')
    df_yoengcheon.to_csv('output/Yeongcheon/flowering_date_Yeongcheon.csv')
    df_wanju.to_csv('output/wanju/flowering_date_wanju.csv')
    df_ulju.to_csv('output/ulju/flowering_date_ulju.csv')
    df_sacheon.to_csv('output/sacheon/flowering_date_sacheon.csv')

# 2004 - 2024년까지 실제 만개일 ( 없으면 NaN으로 )
def sort_flowering_date():  # 2004 - 2024년까지 실제 만개일
    # 파일 로드 --> 8개 지역
    output_path = 'output'
    output_list = os.listdir(output_path)
    for output_folder in output_list:
        print(output_folder)

        file_path = os.path.join(output_path, output_folder, f'flowering_date_{output_folder}.csv')
        flowering_date_df = pd.read_csv(file_path)
        flowering_date_df = pd.DataFrame(flowering_date_df)

        years = list(range(2004, 2025))
        years.sort(reverse=True)

        df_full = pd.DataFrame({
            "year": years,
            "station": output_folder,
            "Date": np.nan
        })

        result = flowering_date_df.combine_first(df_full)
        # result = result.drop(columns=['Unnamed: 0'])

        result = result[['station', 'year', 'Date']]
        # print(result)
        result.to_csv(f'output/{output_folder}/flowering_date_{output_folder}.csv', index=False, encoding='utf-8-sig')

def get_other_region_data():
    output_path = 'output'
    output_folder = ['naju', 'wanju', 'ulju', 'sacheon']
    # output_folder = ['naju']


    for station in output_folder:
        input_list = os.path.join(output_path, station, 'input')
        input_file = os.listdir(input_list)

        for file in input_file:
            file_path = os.path.join(input_list, file)

            df = pd.read_csv(file_path, encoding='euc-kr')
            df['년도'] = df['일시'].astype(str).str.split('-').str[0]
            grouped = df.groupby('년도')

            for year, group in grouped:
                group = group.rename(columns={'평균기온(°C)': 'tavg', '최고기온(°C)': 'tmax', '최저기온(°C)': 'tmin',
                                              '일시':'Date', '년도':'year', '지점명':'station'})
                print(group)
                group.to_csv(f'output/{station}/{station}_{year}.csv', index=False, encoding='utf-8-sig')

def get_dvr_graph():
    output_path = 'output'
    output_list = os.listdir(output_path)

    # output_list = ['naju'] # 테스트를 위한 데이터 정리
    for station in output_list:
        print(station)

        obj_date = pd.read_csv(f'output/{station}/flowering_date_{station}.csv')
        obj_date = obj_date[['station', 'year', 'Date']]
        obj_date = obj_date.sort_values(by='year', ascending=True, ignore_index=True)
        obj_date = obj_date.rename(columns={'Date':'obj_date'})
        obj_date['station'] = station

        dvs_date = pd.read_csv(f'output/{station}/DVS_{station}_model.csv')
        dvs_date['year'] = dvs_date['Date'].str.split('-').str[0].astype(int)
        dvs_date = dvs_date[['Station', 'year', 'Date']]
        dvs_date = dvs_date.rename(columns={'Date':'dvs_date', 'Station':'station'})

        mdvr_date = pd.read_csv(f'output/{station}/mDVR/{station}_mDVR_date.csv')
        print(mdvr_date)
        mdvr_date = mdvr_date.rename(columns={'Date':'mdvr_date'})


        cd_date = pd.read_csv(f'output/{station}/cd_{station}_date.csv')
        cd_date = cd_date.rename(columns={'예상 만개일':'cd_date'})

        df = pd.merge(obj_date, dvs_date, on=['station','year'], how='outer')
        df = pd.merge(df, mdvr_date, on=['station','year'], how='outer')
        df = pd.merge(df, cd_date, on=['station','year'], how='outer')

        df = df.sort_values(by='year', ignore_index=True)
        print(df)
        df['obj_date'] = df['obj_date'].apply(lambda x: x.split('-')[1] + '-' + x.split('-')[2] if pd.notna(x) else x)
        df['dvs_date'] = df['dvs_date'].apply(lambda x: x.split('-')[1] + '-' + x.split('-')[2] if pd.notna(x) else x)
        df['mdvr_date'] = df['mdvr_date'].apply(lambda x: x.split('-')[1] + '-' + x.split('-')[2] if pd.notna(x) else x)
        df['cd_date'] = df['cd_date'].apply(lambda x: x.split('-')[1] + '-' + x.split('-')[2] if pd.notna(x) else x)


        df['obj_date'] = pd.to_datetime(df['obj_date'], format='%m-%d')
        df['dvs_date'] = pd.to_datetime(df['dvs_date'], format='%m-%d')
        df['mdvr_date'] = pd.to_datetime(df['mdvr_date'], format='%m-%d')
        df['cd_date'] = pd.to_datetime(df['cd_date'], format='%m-%d')


        # # 그래프 그리기
        fig, ax = plt.subplots(figsize=(10, 6))

        ax.yaxis.set_major_locator(mdates.DayLocator(interval=3))
        ax.yaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))

        # 첫 번째 y축: DVS_date
        plt.plot(df['year'], df['dvs_date'], label='dvs', color='b', marker='o')
        ax.set_xlabel('Year', fontweight = 'bold')


        # 두 번째 y축: obj_date
        plt.plot(df['year'], df['obj_date'], label='obj', color='r', marker='x')

        plt.plot(df['year'], df['mdvr_date'], label='mDVR', color='g', marker='^')
        plt.plot(df['year'], df['cd_date'], label='cd', color='brown', marker='<')


        # 그래프 제목과 축 레이블 설정
        plt.suptitle(f'{station}', fontsize=20, position=(0.5, 0.87))
        plt.ylabel('Full bloom dates', fontweight = 'bold')
        plt.grid(True, alpha=0.5, color='gray')

        ax.set_ylim([mdates.date2num(datetime(1900, 3, 15)), mdates.date2num(datetime(1900, 5, 20))])

        plt.xticks(dvs_date['year'])

        # 그래프 제목 및 레이아웃 설정
        fig.tight_layout()
        plt.legend()
        # plt.show()
        plt.savefig(f'output/{station}/dvs_{station}_graph.png')


def mDVR_hourly_temp():
    # 데이터 불러오기
    output_path = 'output'
    output_list = os.listdir(output_path)
    # output_list = ['naju'] # 테스트를 위한 데이터 정리
    for output_folder in output_list:
        file_path = os.listdir(os.path.join(output_path, output_folder))
        # file_path = ['naju_2004.csv']

        df_mdvr_date = pd.DataFrame()
        df_mdvr_date['station'] = [output_folder] * 21
        df_mdvr_date['year'] = [i for i in range(2004, 2025)]

        for station_file in file_path:
            print(station_file)

            # 현재 데이터 없어서 처리 -> 데이터 생기면 삭제 (보성)
            # if not ('wanju' in station_file or 'ulju' in station_file or 'sacheon' in station_file):

            if not ('input' in station_file or 'cd' in station_file or 'graph' in station_file or 'flowering_date' in station_file or 'DVS' in station_file or 'mDVR' in station_file): # --> 여기까지 : 모든 파일에 대해 기상데이터만 남기기
                try:
                    year = station_file.split('_')[1]
                    index = df_mdvr_date[df_mdvr_date['year'] == int(year)].index[0]

                except:
                    year = station_file.split('_')[1].split('.')[0]
                    index = df_mdvr_date[df_mdvr_date['year'] == int(year)].index[0]

                file_path = os.path.join(output_path, output_folder, station_file)
                df = pd.read_csv(file_path)
                df_hourly_temp = pd.DataFrame()

                dvr1_sum = 0
                dvr2_sum = 0
                save_date = None
                mDVR_date = None

                for idx, row in df.iterrows():
                    if idx != 0 and idx != len(df)-1:

                        hy = df.iloc[idx-1]['tmax']
                        mt = df.iloc[idx+1]['tmin']
                        h = row['tmax']
                        m = row['tmin']

                        temp_list = []
                        df_daily = pd.DataFrame()
                        df_daily['Date'] = [row['Date']] * 24
                        df_daily['hour'] = [i for i in range(24)]
                        df_daily['station'] = [output_folder] * 24
                        for i in range(24):
                            hour = i

                            if 0 <= hour <= 3:
                                temp = (hy - m) * math.sin((4 - hour) * 3.14 / 30) ** 2 + m
                            elif 4 <= hour <= 13:
                                temp = (h - m) * math.sin((hour - 4) * 3.14 / 18) ** 2 + m
                            elif 14 <= hour <= 23:
                                temp = (h - mt) * math.sin((28 - hour) * 3.14 / 30) ** 2 + mt

                            temp_list.append(temp)

                            if 0 <= temp <= 6:
                                DVR_1 = 1.333 * 10**-3
                            elif 6 < temp <= 9:
                                DVR_1 = 2.276 * 10**-3 - 1.571 * 10**-4 * temp
                            elif 9 < temp <= 12:
                                DVR_1 = 3.448 * 10**-3 - 2.874 * 10**-4 * temp

                            try:
                                dvr1_sum += DVR_1
                            except:
                                pass

                            if dvr1_sum >= 2:
                                if not save_date:
                                    save_date = row['Date']
                                else:
                                    if temp <= 20:
                                        DVR_2 = math.exp(35.27 - 12094 * ((temp + 273) ** -1))
                                    elif 20 <= temp:
                                        DVR_2 = math.exp(5.82 - 3474 * ((temp + 273) ** -1))

                                    dvr2_sum += DVR_2

                                    if dvr2_sum >= 0.9593:
                                        if not mDVR_date:
                                            mDVR_date = row['Date']
                                            df_mdvr_date.loc[index, 'Date'] = mDVR_date

                        df_daily['temp'] = temp_list
                        df_hourly_temp = pd.concat([df_hourly_temp, df_daily])

            if not os.path.exists(f'output/{output_folder}/mDVR'):
                os.makedirs(f'output/{output_folder}/mDVR')

                # df_hourly_temp.to_csv(f'output/{output_folder}/mDVR/{output_folder}_{year}_hourly_temp.csv', index=False, encoding='utf-8-sig')
        df_mdvr_date.to_csv(f'output/{output_folder}/mDVR/{output_folder}_mDVR_date.csv', index=False, encoding='utf-8-sig')

                    # # 함수 작동 부분
    # df = pd.DataFrame()
    # df['시간'] = [i for i in range(24)]
    #
    # for i in range(len(df)):
    #     hy = 전날 tmax
    #     mt = 다음날 tmin
    #     h = tmax
    #     m = tmin

    #
    # print(df)
    # df.to_csv(f'output/{output_path}/mDVR/{station}_{year}_hourly_temp.csv', index=False, encoding='utf-8-sig'}
    #

def chill_days(tmax, tmin, tavg):
    tc = 5.4

    if 0 <= tc <= tmin <= tmax:
        cd = 0
    elif 0 <= tmin <= tc < tmax:
        cd = -((tavg - tmin) - (tmax - tc) ** 2 / (2 * (tmax - tmin)))
    elif 0 <= tmin <= tmax <= tc:
        cd = -(tavg - tmin)
    elif tmin < 0 <= tmax <= tc:
        cd = -(tmax ** 2 / (2 * (tmax - tmin)))
    elif tmin < 0 < tc < tmax:
        cd = -(tmax ** 2 / (2 * (tmax - tmin))) - ((tmax - tc) ** 2 / (2 * (tmax - tmin)))
    else:
        cd = 0
    return cd

def anti_chill_days(tmax, tmin, tavg):
    tc = 5.4

    if 0 <= tc <= tmin <= tmax:
        hr = tavg - tc
    elif 0 <= tmin <= tc < tmax:
        hr = (tmax - tc) ** 2 / (2 * (tmax - tmin))
    elif 0 <= tmin <= tmax <= tc:
        hr = 0
    elif tmin < 0 <= tmax <= tc:
        hr = 0
    elif tmin < 0 < tc < tmax:
        hr = (tmax - tc) ** 2 / (2 * (tmax - tmin))
    else:
        hr = 0
    return hr

def cd_model():
    cr = -86.4
    Hr = 272

    # 데이터 불러오기
    output_path = 'output'
    output_list = os.listdir(output_path)
    for output_folder in output_list:
        file_path = os.listdir(os.path.join(output_path, output_folder))
        df_cd_date = pd.DataFrame()
        df_cd_date['year'] = [i for i in range(2004, 2025)]
        df_cd_date['station'] = [output_folder] * 21
        for station_file in file_path:

            if not ('input' in station_file or
                    'cd' in station_file or 'flowering_date' in station_file or 'DVS' in station_file or 'mDVR' in station_file or 'graph' in station_file):  # 기상데이터만 남기기
                try:
                    year = station_file.split('_')[1]
                    index = df_cd_date[df_cd_date['year'] == int(year)].index[0]
                except:
                    year = station_file.split('_')[1].split('.')[0]
                    index = df_cd_date[df_cd_date['year'] == int(year)].index[0]

                df = pd.read_csv(os.path.join(output_path, output_folder, station_file))
                # tavg 계산 추가
                df['tavg'] = (df['tmax'] + df['tmin']) / 2
                df['cd'] = 0  # 냉각량 초기화
                df['hr'] = 0  # 가온량 초기화

                cumulative_cd = 0
                cumulative_hr = 0
                dormancy_released = False
                flowering_date = None

                for idx, row in df.iterrows():
                    tmax = row['tmax']
                    tmin = row['tmin']
                    tavg = row['tavg']

                    # 냉각량 계산
                    cd_value = chill_days(tmax, tmin, tavg)
                    df.at[idx, 'cd'] = cd_value
                    cumulative_cd += cd_value

                    # 저온 요구량에 도달했을 때 내생휴면 해제
                    if not dormancy_released and cumulative_cd <= cr:
                        dormancy_released = True
                        release_date = row['Date']
                        df_cd_date.loc[index, '내생휴면 해제일'] = release_date

                    # 내생휴면 해재 후 가온량 계산
                    if dormancy_released:
                        hr_value = anti_chill_days(tmax, tmin, tavg)
                        df.at[idx, 'hr'] = hr_value
                        cumulative_hr += hr_value

                        # 누적 가온량이 고온 요구량에 도달했을 때 만개일 예측
                        if cumulative_hr >= Hr and flowering_date is None:
                            flowering_date = row['Date']
                            df_cd_date.loc[index, '예상 만개일'] = flowering_date

        df_cd_date.to_csv(f'output/{output_folder}/cd_{output_folder}_date.csv', index=False, encoding='utf-8-sig')

def main():
    if not os.path.exists('output'):
        os.makedirs('output')

    # # DVR모델을 위한 데이터 수집
    # get_data(2004, 2024)
    # get_other_region_data()
    # get_flowering_date()
    DVR_model()
    # get_dvr_graph()

    # mDVR모델
    mDVR_hourly_temp()

    # cd모델
    cd_model()



if __name__ == '__main__':
    main()
