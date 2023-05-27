import baostock as bs
import stock_x


bs.login()

stock_x.download_stocks_yield_data("H30094")

bs.logout()
