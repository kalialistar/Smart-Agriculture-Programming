from flask import Flask, request, render_template
import pandas as pd

app = Flask("농작물재해보험 계약 현황 검색 서비스")

# CSV 파일 로드
contract_paddy1 = pd.read_csv('C:/Users/서보성/Desktop/농업정책보험금융원_농작물재해보험 논작물세부정보_20221231_part1.csv', encoding='EUC-KR', on_bad_lines='skip')
contract_paddy2 = pd.read_csv('C:/Users/서보성/Desktop/농업정책보험금융원_농작물재해보험 논작물세부정보_20221231_part2.csv', encoding='EUC-KR', on_bad_lines='skip')
contract_special = pd.read_csv('C:/Users/서보성/Desktop/농업정책보험금융원_농작물재해보험 계약된 특용작물 세부현황_20221231.csv', encoding='UTF-8-SIG', on_bad_lines='skip')
contract_fruit = pd.read_csv('C:/Users/서보성/Desktop/농업정책보험금융원_농작물재해보험 계약된 과수작물 세부현황_20221231 (1).csv', encoding='EUC-KR', on_bad_lines='skip')
contract_field = pd.read_csv('C:/Users/서보성/Desktop/농업정책보험금융원_농작물재해보험 계약된 밭작물 세부현황_20221231 (1).csv', encoding='EUC-KR', on_bad_lines='skip')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    crop_type = request.args.get('crop_type')
    std_yield = request.args.get('std_yield')
    avg_yield = request.args.get('avg_yield')
    ins_yield = request.args.get('ins_yield')
    ins_area = request.args.get('ins_area')

    queries = [q.strip() for q in query.split(',')]

    if not query or not crop_type:
        return render_template('index.html', results=[])

    print(f"Received query: {query}, crop_type: {crop_type}, std_yield: {std_yield}, avg_yield: {avg_yield}, ins_yield: {ins_yield}, ins_area: {ins_area}")

    # 검색 조건 필터링 함수
    def filter_data(data):
        result = data[
            (data['품목명'].str.contains(queries[0], case=False, na=False)) &
            (data['품종명'].str.contains(queries[1], case=False, na=False))
        ]
        print(f"Initial filtered data: {len(result)} rows found")
        if std_yield:
            result = result[result['표준수확량'] >= float(std_yield)]
            print(f"After std_yield filtering: {len(result)} rows remaining")
        if avg_yield:
            result = result[result['평년수확량'] >= float(avg_yield)]
            print(f"After avg_yield filtering: {len(result)} rows remaining")
        if ins_yield:
            result = result[result['가입수확량'] >= float(ins_yield)]
            print(f"After ins_yield filtering: {len(result)} rows remaining")
        if ins_area:
            result = result[result['보험가입면적'] >= float(ins_area)]
            print(f"After ins_area filtering: {len(result)} rows remaining")
        return result

    # 각 작물 유형에 따라 데이터 필터링
    if crop_type == 'paddy1':
        result = filter_data(contract_paddy1)
        result = result.rename(columns={
            '표준수확량': '표준수확량(kg)',
            '평년수확량': '평년수확량(kg)',
            '가입수확량': '가입수확량(kg)',
            '보험가입면적': '보험가입면적(㎡)'
        })

    elif crop_type == 'paddy2':
        result = filter_data(contract_paddy2)
        result = result.rename(columns={
            '표준수확량': '표준수확량(kg)',
            '평년수확량': '평년수확량(kg)',
            '가입수확량': '가입수확량(kg)',
            '보험가입면적': '보험가입면적(㎡)'
        })

    elif crop_type == 'special':
        result = filter_data(contract_special)
        result = result.rename(columns={
            '재배칸수': '재배칸수(칸)',
            '단변식재수': '단변식재수(그루)',
            '장변식재수': '장변식재수(그루)',
            '지주목간격거리': '지주목간격거리(cm)',
            '두둑너비': '두둑너비(cm)',
            '고랑너비': '고랑너비(cm)',
            '두둑높이': '두둑높이(cm)',
            '보험가입면적(m2)': '보험가입면적(㎡)'
        })

    elif crop_type == 'fruit':
        result = filter_data(contract_fruit)
        result = result.rename(columns={
            '수령': '수령(살)',
            '주수': '주수(그루)',
            '가입가격': '가입가격(만원)',
            '표준수확량': '표준수확량(kg)',
            '평년수확량': '평년수확량(kg)',
            '가입수확량': '가입수확량(kg)',
            '평년과실수': '평년과실수(개)',
            '가입과실수': '가입과실수(개)',
            '과중': '과중(g)'
        })

    elif crop_type == 'field':
        result = filter_data(contract_field)
        result = result.rename(columns={
            '주간거리': '주간거리(m)',
            '재식간격': '재식간격(cm)',
            '이랑너비': '이랑너비(m)',
            '이랑수': '이랑수(줄)',
            '총재식주수': '총재식주수(그루)',
            '표준수확량': '표준수확량(kg)',
            '평년수확량': '평년수확량(kg)',
            '가입수확량': '가입수확량(kg)',
            '보험가입면적': '보험가입면적(㎡)'
        })

    else:
        return render_template('index.html', results=[])


    results = result.head(100).to_dict(orient='records')
    print(f"Final result to display: {len(results)} rows")
    return render_template('index.html', results=results)


if __name__ == '__main__':
    app.run(debug=True)

