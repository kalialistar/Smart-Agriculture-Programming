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
    file_type = request.args.get('file_type')
    queries = [q.strip() for q in query.split(',')]

    if not query or not file_type:
        return render_template('index.html', results=[])

    # paddy1 검색
    if file_type == 'paddy1':
        result = contract_paddy1[
            contract_paddy1['품목명'].str.contains(queries[0], case=False, na=False) &
            contract_paddy1['품종명'].str.contains(queries[1], case=False, na=False)
        ]
        result = result.rename(columns={
            '표준수확량': '표준수확량(kg)',
            '평년수확량': '평년수확량(kg)',
            '가입수확량': '가입수확량(kg)',
            '보험가입면적': '보험가입면적(㎡)'
        })
        results = result.to_dict(orient='records')

    # paddy2 검색
    elif file_type == 'paddy2':
        result = contract_paddy2[
            contract_paddy2['품목명'].str.contains(queries[0], case=False, na=False) &
            contract_paddy2['품종명'].str.contains(queries[1], case=False, na=False)
        ]
        result = result.rename(columns={
            '표준수확량': '표준수확량(kg)',
            '평년수확량': '평년수확량(kg)',
            '가입수확량': '가입수확량(kg)',
            '보험가입면적': '보험가입면적(㎡)'
        })
        results = result.to_dict(orient='records')

    # special 검색
    elif file_type == 'special':
        result = contract_special[
            contract_special['품목명'].str.contains(queries[0], case=False, na=False) &
            contract_special['품종명'].str.contains(queries[1], case=False, na=False)
        ]
        result = result.rename(columns={'보험가입면적': '보험가입면적(㎡)'})
        results = result.to_dict(orient='records')

    # fruit 검색
    elif file_type == 'fruit':
        result = contract_fruit[
            contract_fruit['품목명'].str.contains(queries[0], case=False, na=False) &
            contract_fruit['품종명'].str.contains(queries[1], case=False, na=False)
        ]
        result = result.rename(columns={
            '표준수확량': '표준수확량(kg)',
            '평년수확량': '평년수확량(kg)',
            '가입수확량': '가입수확량(kg)',
            '평년과실수': '평년과실수(개)',
            '가입과실수': '가입과실수(개)'
        })
        results = result.to_dict(orient='records')

    # field 검색
    elif file_type == 'field':
        result = contract_field[
            contract_field['품목명'].str.contains(queries[0], case=False, na=False) &
            contract_field['품종명'].str.contains(queries[1], case=False, na=False)
        ]
        result = result.rename(columns={
            '표준수확량': '표준수확량(kg)',
            '평년수확량': '평년수확량(kg)',
            '가입수확량': '가입수확량(kg)',
            '보험가입면적': '보험가입면적(㎡)'
        })
        results = result.to_dict(orient='records')

    else:
        return render_template('index.html', results=[])

    return render_template('index.html', results=results)


if __name__ == '__main__':
    app.run(debug=True)






