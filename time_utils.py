from datetime import datetime, timedelta

now = datetime.now()

current_date = now.strftime("%Y-%m-%d")

current_year = now.year

year_start_date = f"{current_year}-01-01"

past_week_date = (now - timedelta(days=7)).strftime("%Y-%m-%d")

past_month_date = (now - timedelta(days=30)).strftime("%Y-%m-%d")

past_quarter_date = (now - timedelta(days=90)).strftime("%Y-%m-%d")

past_half_year_date = (now - timedelta(days=180)).strftime("%Y-%m-%d")

past_year_date = (now - timedelta(days=365)).strftime("%Y-%m-%d")
