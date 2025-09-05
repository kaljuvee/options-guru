"""
Stock data utilities with S&P 500 stock list
"""

# Popular S&P 500 stocks for the calculator
SP500_STOCKS = {
    'AAPL': 'Apple Inc.',
    'MSFT': 'Microsoft Corporation',
    'GOOGL': 'Alphabet Inc. Class A',
    'AMZN': 'Amazon.com Inc.',
    'NVDA': 'NVIDIA Corporation',
    'TSLA': 'Tesla Inc.',
    'META': 'Meta Platforms Inc.',
    'BRK.B': 'Berkshire Hathaway Inc. Class B',
    'UNH': 'UnitedHealth Group Incorporated',
    'JNJ': 'Johnson & Johnson',
    'JPM': 'JPMorgan Chase & Co.',
    'V': 'Visa Inc.',
    'PG': 'Procter & Gamble Company',
    'MA': 'Mastercard Incorporated',
    'HD': 'Home Depot Inc.',
    'CVX': 'Chevron Corporation',
    'LLY': 'Eli Lilly and Company',
    'ABBV': 'AbbVie Inc.',
    'PFE': 'Pfizer Inc.',
    'KO': 'Coca-Cola Company',
    'AVGO': 'Broadcom Inc.',
    'PEP': 'PepsiCo Inc.',
    'TMO': 'Thermo Fisher Scientific Inc.',
    'COST': 'Costco Wholesale Corporation',
    'MRK': 'Merck & Co. Inc.',
    'WMT': 'Walmart Inc.',
    'BAC': 'Bank of America Corporation',
    'NFLX': 'Netflix Inc.',
    'XOM': 'Exxon Mobil Corporation',
    'DIS': 'Walt Disney Company',
    'ABT': 'Abbott Laboratories',
    'CRM': 'Salesforce Inc.',
    'VZ': 'Verizon Communications Inc.',
    'ADBE': 'Adobe Inc.',
    'NKE': 'Nike Inc.',
    'WFC': 'Wells Fargo & Company',
    'T': 'AT&T Inc.',
    'PM': 'Philip Morris International Inc.',
    'INTC': 'Intel Corporation',
    'UPS': 'United Parcel Service Inc.',
    'IBM': 'International Business Machines Corporation',
    'GS': 'Goldman Sachs Group Inc.',
    'MS': 'Morgan Stanley',
    'CAT': 'Caterpillar Inc.',
    'GE': 'General Electric Company',
    'AMD': 'Advanced Micro Devices Inc.',
    'QCOM': 'QUALCOMM Incorporated',
    'INTU': 'Intuit Inc.',
    'ISRG': 'Intuitive Surgical Inc.',
    'BKNG': 'Booking Holdings Inc.',
    'TXN': 'Texas Instruments Incorporated',
    'AMGN': 'Amgen Inc.',
    'HON': 'Honeywell International Inc.',
    'SPGI': 'S&P Global Inc.',
    'LOW': 'Lowe\'s Companies Inc.',
    'AXP': 'American Express Company',
    'BLK': 'BlackRock Inc.',
    'BA': 'Boeing Company',
    'DE': 'Deere & Company',
    'MDT': 'Medtronic plc',
    'C': 'Citigroup Inc.',
    'GILD': 'Gilead Sciences Inc.',
    'TJX': 'TJX Companies Inc.',
    'SCHW': 'Charles Schwab Corporation',
    'LMT': 'Lockheed Martin Corporation',
    'ADP': 'Automatic Data Processing Inc.',
    'SYK': 'Stryker Corporation',
    'TMUS': 'T-Mobile US Inc.',
    'CVS': 'CVS Health Corporation',
    'MO': 'Altria Group Inc.',
    'ZTS': 'Zoetis Inc.',
    'FIS': 'Fidelity National Information Services Inc.',
    'REGN': 'Regeneron Pharmaceuticals Inc.',
    'PLD': 'Prologis Inc.',
    'MMM': '3M Company',
    'NOW': 'ServiceNow Inc.',
    'PYPL': 'PayPal Holdings Inc.',
    'SO': 'Southern Company',
    'DUK': 'Duke Energy Corporation',
    'CL': 'Colgate-Palmolive Company',
    'ITW': 'Illinois Tool Works Inc.',
    'BSX': 'Boston Scientific Corporation',
    'EOG': 'EOG Resources Inc.',
    'ICE': 'Intercontinental Exchange Inc.',
    'FCX': 'Freeport-McMoRan Inc.',
    'NSC': 'Norfolk Southern Corporation',
    'SHW': 'Sherwin-Williams Company',
    'USB': 'U.S. Bancorp',
    'AON': 'Aon plc',
    'PNC': 'PNC Financial Services Group Inc.',
    'CME': 'CME Group Inc.',
    'GD': 'General Dynamics Corporation',
    'TGT': 'Target Corporation',
    'F': 'Ford Motor Company',
    'EMR': 'Emerson Electric Co.',
    'COF': 'Capital One Financial Corporation',
    'FISV': 'Fiserv Inc.',
    'CSX': 'CSX Corporation',
    'GM': 'General Motors Company',
    'WM': 'Waste Management Inc.',
    'TFC': 'Truist Financial Corporation',
    'BDX': 'Becton Dickinson and Company',
    'NOC': 'Northrop Grumman Corporation',
    'SPY': 'SPDR S&P 500 ETF Trust',
    'QQQ': 'Invesco QQQ Trust',
    'IWM': 'iShares Russell 2000 ETF',
    'VTI': 'Vanguard Total Stock Market ETF',
    'VOO': 'Vanguard S&P 500 ETF'
}

def get_stock_list():
    """Get list of available stocks"""
    return list(SP500_STOCKS.keys())

def get_stock_name(symbol):
    """Get company name for a stock symbol"""
    return SP500_STOCKS.get(symbol.upper(), symbol.upper())

def get_popular_stocks():
    """Get list of most popular stocks for quick selection"""
    return ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META', 'SPY', 'QQQ']

def search_stocks(query):
    """Search for stocks by symbol or name"""
    query = query.upper()
    matches = []
    
    for symbol, name in SP500_STOCKS.items():
        if query in symbol or query in name.upper():
            matches.append(symbol)
    
    return matches[:10]  # Return top 10 matches

