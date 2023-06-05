import baostock as bs
import stock_x
import os

index_codes = ['H30094','931468','931056']

bs.login()

for index_code in index_codes: 
  if not os.path.exists(f'./roe_data/{index_code}.csv'):
    stock_x.download_stocks_roe_data(index_code)

  stock_x.download_stocks_yield_data(index_code)

bs.logout()
