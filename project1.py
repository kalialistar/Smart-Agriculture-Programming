from flask import Flask, request, render_template
import pandas as pd

app = Flask(__name__)

contract_paddy1 = pd.read_csv('C:/Users/서보성/Desktop/농업정책보험금융원_농작물재해보험 논작물세부정보_20221231_part1.csv', encoding='EUC-KR', on_bad_lines='skip')
contract_paddy2 = pd.read_csv('C:/Users/서보성/Desktop/농업정책보험금융원_농작물재해보험 논작물세부정보_20221231_part2.csv', encoding='EUC-KR', on_bad_lines='skip')
contract_special = pd.read_csv('C:/Users/서보성/Desktop/농업정책보험금융원_농작물재해보험 계약된 특용작물 세부현황_20221231.csv', encoding='UTF-8-SIG', on_bad_lines='skip')
contract_fruit = pd.read_csv('C:/Users/서보성/Desktop/농업정책보험금융원_농작물재해보험 계약된 과수작물 세부현황_20221231 (1).csv', encoding='EUC-KR', on_bad_lines='skip')
contract_field = pd.read_csv('C:/Users/서보성/Desktop/농업정책보험금융원_농작물재해보험 계약된 밭작물 세부현황_20221231 (1).csv', encoding='EUC-KR', on_bad_lines='skip')


@app.route('/')
def index():
    page = 1
    total_pages = 0
    return render_template('index.html', results=[], page=page, total_pages=total_pages)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    crop_type = request.args.get('crop_type')
    std_yield = request.args.get('std_yield')
    avg_yield = request.args.get('avg_yield')
    ins_yield = request.args.get('ins_yield')
    ins_area = request.args.get('ins_area')
    page = int(request.args.get('page', 1))
    per_page = 20

    queries = [q.strip() for q in query.split(',')]

    if not query or not crop_type:
        return render_template('index.html', results=[], page=page, total_pages=0)

    def filter_data(data, area_col='보험가입면적'):
        result = data[
            (data['품목명'].str.contains(queries[0], case=False, na=False)) &
            (data['품종명'].str.contains(queries[1], case=False, na=False))
        ]
        if std_yield:
            result = result[result['표준수확량'] >= float(std_yield)]
        if avg_yield:
            result = result[result['평년수확량'] >= float(avg_yield)]
        if ins_yield:
            result = result[result['가입수확량'] >= float(ins_yield)]
        if ins_area:
            result = result[result[area_col] >= float(ins_area)]
        return result

    if crop_type == 'paddy1':
        result = filter_data(contract_paddy1)
    elif crop_type == 'paddy2':
        result = filter_data(contract_paddy2)
    elif crop_type == 'special':
        result = filter_data(contract_special, area_col='보험가입면적(m2)')
    elif crop_type == 'fruit':
        result = filter_data(contract_fruit)
    elif crop_type == 'field':
        result = filter_data(contract_field)
    else:
        return render_template('index.html', results=[], page=page, total_pages=0)

    total_rows = len(result)
    total_pages = (total_rows // per_page) + (1 if total_rows % per_page else 0)

    start_row = (page - 1) * per_page
    end_row = start_row + per_page
    paginated_result = result.iloc[start_row:end_row]

    results = paginated_result.to_dict(orient='records')

    columns = result.columns.tolist()

    return render_template('index.html', results=results, columns=columns, page=page, total_pages=total_pages)


if __name__ == '__main__':
    app.run(debug=True)
