from flask import Flask, request, render_template
import pandas as pd

app = Flask("APFS")

# 데이터 로드
contract_paddy1 = pd.read_csv('농업정책보험금융원_농작물재해보험 논작물세부정보_20221231_part1.csv', encoding='EUC-KR', on_bad_lines='skip')
contract_paddy2 = pd.read_csv('농업정책보험금융원_농작물재해보험 논작물세부정보_20221231_part2.csv', encoding='EUC-KR', on_bad_lines='skip')
contract_special = pd.read_csv('농업정책보험금융원_농작물재해보험 계약된 특용작물 세부현황_20221231.csv', encoding='UTF-8-SIG', on_bad_lines='skip')
contract_fruit = pd.read_csv('농업정책보험금융원_농작물재해보험 계약된 과수작물 세부현황_20221231.csv', encoding='EUC-KR', on_bad_lines='skip')
contract_field = pd.read_csv('농업정책보험금융원_농작물재해보험 계약된 밭작물 세부현황_20221231.csv', encoding='EUC-KR', on_bad_lines='skip')

# 데이터 통합(ChatGPT 도움)
contract_paddy = pd.concat([contract_paddy1, contract_paddy2], ignore_index=True)

@app.route('/')
def index():
    return render_template('result1.html')

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    crop_type = request.args.get('crop_type', '')
    std_yield = request.args.get('std_yield', '')
    avg_yield = request.args.get('avg_yield', '')
    ins_yield = request.args.get('ins_yield', '')
    ins_area = request.args.get('ins_area', '')
    page = int(request.args.get('page', 1))
    per_page = 20

    if ',' in query:
        queries = [q.strip() for q in query.split(',')]
    else:
        queries = [query.strip(), '']

    if not crop_type:
        return render_template('result1.html')

    # 근사값(ChatGPT 도움)
    def filter_data(data, name, value):
        if value:
            data['approx'] = (data[name] - float(value)).abs()
            return data.nsmallest(50, 'approx').drop(columns=['approx'])
        return data

    # 필터링
    if crop_type == 'paddy':
        result = contract_paddy[
            (contract_paddy['품목명'].str.contains(queries[0], case=False, na=False) | (queries[0] == '')) &
            (contract_paddy['품종명'].str.contains(queries[1], case=False, na=False) | (queries[1] == ''))
        ]
    elif crop_type == 'special':
        result = contract_special[
            (contract_special['품목명'].str.contains(queries[0], case=False, na=False) | (queries[0] == '')) &
            (contract_special['품종명'].str.contains(queries[1], case=False, na=False) | (queries[1] == ''))
        ]
    elif crop_type == 'fruit':
        result = contract_fruit[
            (contract_fruit['품목명'].str.contains(queries[0], case=False, na=False) | (queries[0] == '')) &
            (contract_fruit['품종명'].str.contains(queries[1], case=False, na=False) | (queries[1] == ''))
        ]
    elif crop_type == 'field':
        result = contract_field[
            (contract_field['품목명'].str.contains(queries[0], case=False, na=False) | (queries[0] == '')) &
            (contract_field['품종명'].str.contains(queries[1], case=False, na=False) | (queries[1] == ''))
        ]
    else:
        return render_template('result1.html')

    result = filter_data(result, '표준수확량', std_yield)
    result = filter_data(result, '평년수확량', avg_yield)
    result = filter_data(result, '가입수확량', ins_yield)
    result = filter_data(result, '보험가입면적', ins_area)

    # 페이지네이션(ChatGPT 도움)
    total_rows = len(result)
    total_pages = (total_rows // per_page) + (1 if total_rows % per_page else 0)

    start_row = (page - 1) * per_page
    end_row = start_row + per_page
    paginated_result = result.iloc[start_row:end_row]

    results = paginated_result.to_dict(orient='records')
    columns = result.columns.tolist()

    # 렌더링
    return render_template('result2.html', results=results, columns=columns, page=page, total_pages=total_pages,
                           query=query, crop_type=crop_type, std_yield=std_yield, avg_yield=avg_yield, ins_yield=ins_yield, ins_area=ins_area)

if __name__ == '__main__':
    app.run(debug=True)
