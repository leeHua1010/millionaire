import requests
import os
import baostock as bs
import pandas as pd
import time_utils as tu

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299'
}

def get_stock_codes_from_index(index_code):
    url = f"https://csi-web-dev.oss-cn-shanghai-finance-1-pub.aliyuncs.com/static/html/csindex/public/uploads/file/autofile/cons/{index_code}cons.xls"

    file_path = f"{index_code}cons.xls"
    res = requests.get(url,headers=headers)

    open(file_path, "wb").write(res.content)

    stocks_data = pd.read_excel(file_path, converters={4: str})

    codes = []
    for index, row in stocks_data.iterrows():
        code = row[4]
        exchange = row[7]
        full_code = ""

        if exchange == "上海证券交易所":
            full_code = f"sh.{code}"
        else:
            full_code = f"sz.{code}"

        codes.append(full_code)

    if os.path.exists(file_path):
        os.remove(file_path)

    return codes


def get_stock_year_roe(code, year):
    dupont_data = bs.query_dupont_data(code, year, quarter=4)

    year_roe = ""
    while (dupont_data.error_code == "0") & dupont_data.next():
        year_roe = dupont_data.get_row_data()[3]

    return year_roe


def get_stock_name(code):
    stock_info = bs.query_stock_basic(code)

    code_name = ""
    while (stock_info.error_code == "0") & stock_info.next():
        code_name = stock_info.get_row_data()[1]

    return code_name


def get_stock_yield(code, start_date=tu.past_year_date, end_date=tu.current_date):
    info = bs.query_history_k_data_plus(
        code,
        "date,close",
        start_date=start_date,
        end_date=end_date,
        frequency="d",
        adjustflag="3",
    )

    data_list = []
    while (info.error_code == "0") & info.next():
        data_list.append(info.get_row_data())

    df = pd.DataFrame(data_list, columns=info.fields)

    price_list = df["close"].tolist()

    start_price = float(price_list[0])
    end_price = float(price_list[-1])
    change_rate = (end_price - start_price) / start_price

    return f"{change_rate:.2%}"


def get_stocks_roe_data(codes, start_year=2013, end_year=tu.current_year, roe_flag=12):
    data_list = []
    columns = ["code", "name", f"gt_{roe_flag}%_counts"]
    year_list = list(range(start_year, end_year))[::-1]

    for year in year_list:
        columns.append(f"{year}_roe")

    for code in codes:
        row = [code]

        name = get_stock_name(code)
        row.append(name)

        for year in year_list:
            year_roe = get_stock_year_roe(code, year)

            row.append(f"{float(year_roe):.2%}" if year_roe else "")

        cleaned_list = [x for x in row if "%" in x]
        count = len([x for x in cleaned_list if float(x.strip("%")) > roe_flag])
        row.insert(2, count)

        data_list.append(row)

    sorted_list = sorted(data_list, key=lambda x: int(x[2]), reverse=True)

    return {"data_list": sorted_list, "columns": columns}


def download_stocks_roe_data(index_code, save_dir="./roe_data"):
    codes = get_stock_codes_from_index(index_code)

    data = get_stocks_roe_data(codes)
    roe_df = pd.DataFrame(data["data_list"], columns=data["columns"])

    if not os.path.exists(save_dir):
        os.mkdir(save_dir)

    roe_df.to_csv(f"{save_dir}/{index_code}_roe_data.csv")


def get_stocks_yield_data(codes):
    data_list = []

    columns = [
        "code",
        "name",
        "this_year_yield",
        "past_week_yield",
        "past_month_yield",
        "past_quarter_yield",
        "past_half_year_yield",
        "past_year_yield",
    ]

    for code in codes:
        row = [code]

        name = get_stock_name(code)
        row.append(name)

        this_year_yield = get_stock_yield(code, tu.year_start_date)
        row.append(this_year_yield)

        past_week_yield = get_stock_yield(code, tu.past_week_date)
        row.append(past_week_yield)

        past_month_yield = get_stock_yield(code, tu.past_month_date)
        row.append(past_month_yield)

        past_quarter_yield = get_stock_yield(code, tu.past_quarter_date)
        row.append(past_quarter_yield)

        past_half_year_yield = get_stock_yield(code, tu.past_half_year_date)
        row.append(past_half_year_yield)

        past_year_yield = get_stock_yield(code, tu.past_year_date)
        row.append(past_year_yield)

        data_list.append(row)

    data_list.sort(key=lambda x: float(x[5].strip("%")))

    return {"data_list": data_list, "columns": columns}


def download_stocks_yield_data(index_code, save_dir="./yield_data"):
    codes = get_stock_codes_from_index(index_code)

    data = get_stocks_yield_data(codes)
    yield_df = pd.DataFrame(data["data_list"], columns=data["columns"])

    if not os.path.exists(save_dir):
        os.mkdir(save_dir)

    yield_df.to_csv(f"{save_dir}/{index_code}_yield_data.csv")


def record_fear_data(save_dir='./fear_data',filename='fear_data.csv'):
    res = requests.get('https://api.jiucaishuo.com/v2/kjtl/getbasedata',headers=headers).json();
    data = res['data']

    if not os.path.exists(save_dir):
        os.mkdir(save_dir)

    file_path = os.path.join(save_dir, filename)
    columns = ['date','num','status_str']
    if(os.path.isfile(file_path)):
        fear_df = pd.read_csv(file_path)
        fear_df.loc[len(fear_df)]=[tu.current_date,data['num'],data['status_str']]
        fear_df.to_csv(file_path,index=False)
    else:
        data_list = []
        data_list.append([tu.current_date,data['num'],data['status_str']])
        fear_df = pd.DataFrame(data_list,columns=columns)
        fear_df.to_csv(file_path,index=False)