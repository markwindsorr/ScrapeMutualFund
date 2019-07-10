# Coding Challenge
# Mark Windsor

from EdgarMutualFund import EdgarMutualFund

user_input = input("Please enter a ticker symbol or Central Index Key(CIK): ").strip()

edgar = EdgarMutualFund()

#Check if user input is cik or ticker
if len(user_input) != 10:
    cik = edgar.ticker_to_cik(user_input)
    print(cik)
    edgar.search_by_cik(cik)
else:
    cik = user_input
    edgar.search_by_cik(cik)


