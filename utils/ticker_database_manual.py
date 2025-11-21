"""
Manual ticker database - Dedicated to a large, consistent, user-supplied list.
This version uses NO external dependencies (requests/pandas) to avoid Python 3.13 errors.
It provides a structure for 500+ tickers based on S&P 500 components.
"""

import json
import os
from datetime import datetime
import sys
# Removed: import requests
# Removed: import pandas as pd
# Removed: from io import StringIO


# --- ORIGINAL MANUAL FUNCTION (MODIFIED TO BE THE PRIMARY FUNCTION) ---

def create_manual_ticker_database():
    """Create a comprehensive ticker database manually (500+)."""
    
    print("\n" + "="*80)
    print("CREATING LARGE MANUAL TICKER DATABASE (500+ S&P 500 COMPONENTS)")
    print("="*80)
    
    # --- USER ACTION REQUIRED: PASTE 500+ TICKERS HERE ---
    #
    # ACTION: To reach 500+ tickers, you must replace the list below
    # with a dictionary containing all the S&P 500 tickers and company names.
    # You will need to copy this list from a source like a CSV/website and format it once.
    #
    ticker_to_company = {
        # --- TOP 100+ STOCKS (Your original list, retained for structure) ---
        # FAANG + Big Tech
        'AAPL': 'Apple Inc.',
        'MSFT': 'Microsoft Corporation',
        'GOOGL': 'Alphabet Inc. (Class A)',
        'GOOG': 'Alphabet Inc. (Class C)',
        'AMZN': 'Amazon.com Inc.',
        'META': 'Meta Platforms Inc.',
        'NVDA': 'NVIDIA Corporation',
        'TSLA': 'Tesla Inc.',
        'NFLX': 'Netflix Inc.',
        
        # Financial Services
        'JPM': 'JPMorgan Chase & Co.',
        'BAC': 'Bank of America Corporation',
        'V': 'Visa Inc.',
        'MA': 'Mastercard Inc.',
        
        # Healthcare & Pharma
        'JNJ': 'Johnson & Johnson',
        'UNH': 'UnitedHealth Group Inc.',
        'PFE': 'Pfizer Inc.',
        
        # Consumer & Retail
        'WMT': 'Walmart Inc.',
        'HD': 'Home Depot Inc.',
        
        'MMM': '3M',
        'AOS': 'A. O. Smith',
        'ABT': 'Abbott Laboratories',
        'ABBV': 'AbbVie',
        'ACN': 'Accenture',
        'ADBE': 'Adobe Inc.',
        'AMD': 'Advanced Micro Devices',
        'AES': 'AES Corporation',
        'AFL': 'Aflac',
        'A': 'Agilent Technologies',
        'APD': 'Air Products',
        'ABNB': 'Airbnb',
        'AKAM': 'Akamai Technologies',
        'ALB': 'Albemarle Corporation',
        'ARE': 'Alexandria Real Estate Equities',
        'ALGN': 'Align Technology',
        'ALLE': 'Allegion',
        'LNT': 'Alliant Energy',
        'ALL': 'Allstate',
        'GOOGL': 'Alphabet Inc. (Class A)',
        'GOOG': 'Alphabet Inc. (Class C)',
        'MO': 'Altria',
        'AMZN': 'Amazon',
        'AMCR': 'Amcor',
        'AEE': 'Ameren',
        'AEP': 'American Electric Power',
        'AXP': 'American Express',
        'AIG': 'American International Group',
        'AMT': 'American Tower',
        'AWK': 'American Water Works',
        'AMP': 'Ameriprise Financial',
        'AME': 'Ametek',
        'AMGN': 'Amgen',
        'APH': 'Amphenol',
        'ADI': 'Analog Devices',
        'AON': 'Aon plc',
        'APA': 'APA Corporation',
        'APO': 'Apollo Global Management',
        'AAPL': 'Apple Inc.',
        'AMAT': 'Applied Materials',
        'APP': 'AppLovin',
        'APTV': 'Aptiv',
        'ACGL': 'Arch Capital Group',
        'ADM': 'Archer Daniels Midland',
        'ANET': 'Arista Networks',
        'AJG': 'Arthur J. Gallagher & Co.',
        'AIZ': 'Assurant',
        'T': 'AT&T',
        'ATO': 'Atmos Energy',
        'ADSK': 'Autodesk',
        'ADP': 'Automatic Data Processing',
        'AZO': 'AutoZone',
        'AVB': 'AvalonBay Communities',
        'AVY': 'Avery Dennison',
        'AXON': 'Axon Enterprise',
        'BKR': 'Baker Hughes',
        'BALL': 'Ball Corporation',
        'BAC': 'Bank of America',
        'BAX': 'Baxter International',
        'BDX': 'Becton Dickinson',
        'BRK.B': 'Berkshire Hathaway',
        'BBY': 'Best Buy',
        'TECH': 'Bio-Techne',
        'BIIB': 'Biogen',
        'BLK': 'BlackRock',
        'BX': 'Blackstone Inc.',
        'XYZ': 'Block, Inc.',
        'BK': 'BNY Mellon',
        'BA': 'Boeing',
        'BKNG': 'Booking Holdings',
        'BSX': 'Boston Scientific',
        'BMY': 'Bristol Myers Squibb',
        'AVGO': 'Broadcom',
        'BR': 'Broadridge Financial Solutions',
        'BRO': 'Brown & Brown',
        'BF.B': 'Brown–Forman',
        'BLDR': 'Builders FirstSource',
        'BG': 'Bunge Global',
        'BXP': 'BXP, Inc.',
        'CHRW': 'C.H. Robinson',
        'CDNS': 'Cadence Design Systems',
        'CPT': 'Camden Property Trust',
        'CPB': 'Campbell\'s Company (The)',
        'COF': 'Capital One',
        'CAH': 'Cardinal Health',
        'CCL': 'Carnival',
        'CARR': 'Carrier Global',
        'CAT': 'Caterpillar Inc.',
        'CBOE': 'Cboe Global Markets',
        'CBRE': 'CBRE Group',
        'CDW': 'CDW Corporation',
        'COR': 'Cencora',
        'CNC': 'Centene Corporation',
        'CNP': 'CenterPoint Energy',
        'CF': 'CF Industries',
        'CRL': 'Charles River Laboratories',
        'SCHW': 'Charles Schwab Corporation',
        'CHTR': 'Charter Communications',
        'CVX': 'Chevron Corporation',
        'CMG': 'Chipotle Mexican Grill',
        'CB': 'Chubb Limited',
        'CHD': 'Church & Dwight',
        'CI': 'Cigna',
        'CINF': 'Cincinnati Financial',
        'CTAS': 'Cintas',
        'CSCO': 'Cisco',
        'C': 'Citigroup',
        'CFG': 'Citizens Financial Group',
        'CLX': 'Clorox',
        'CME': 'CME Group',
        'CMS': 'CMS Energy',
        'KO': 'Coca-Cola Company (The)',
        'CTSH': 'Cognizant',
        'COIN': 'Coinbase',
        'CL': 'Colgate-Palmolive',
        'CMCSA': 'Comcast',
        'CAG': 'Conagra Brands',
        'COP': 'ConocoPhillips',
        'ED': 'Consolidated Edison',
        'STZ': 'Constellation Brands',
        'CEG': 'Constellation Energy',
        'COO': 'Cooper Companies (The)',
        'CPRT': 'Copart',
        'GLW': 'Corning Inc.',
        'CPAY': 'Corpay',
        'CTVA': 'Corteva',
        'CSGP': 'CoStar Group',
        'COST': 'Costco',
        'CTRA': 'Coterra',
        'CRWD': 'CrowdStrike',
        'CCI': 'Crown Castle',
        'CSX': 'CSX Corporation',
        'CMI': 'Cummins',
        'CVS': 'CVS Health',
        'DHR': 'Danaher Corporation',
        'DRI': 'Darden Restaurants',
        'DDOG': 'Datadog',
        'DVA': 'DaVita',
        'DAY': 'Dayforce',
        'DECK': 'Deckers Brands',
        'DE': 'Deere & Company',
        'DELL': 'Dell Technologies',
        'DAL': 'Delta Air Lines',
        'DVN': 'Devon Energy',
        'DXCM': 'Dexcom',
        'FANG': 'Diamondback Energy',
        'DLR': 'Digital Realty',
        'DG': 'Dollar General',
        'DLTR': 'Dollar Tree',
        'D': 'Dominion Energy',
        'DPZ': 'Domino\'s',
        'DASH': 'DoorDash',
        'DOV': 'Dover Corporation',
        'DOW': 'Dow Inc.',
        'DHI': 'D. R. Horton',
        'DTE': 'DTE Energy',
        'DUK': 'Duke Energy',
        'DD': 'DuPont',
        'ETN': 'Eaton Corporation',
        'EBAY': 'eBay Inc.',
        'ECL': 'Ecolab',
        'EIX': 'Edison International',
        'EW': 'Edwards Lifesciences',
        'EA': 'Electronic Arts',
        'ELV': 'Elevance Health',
        'EME': 'Emcor',
        'EMR': 'Emerson Electric',
        'ETR': 'Entergy',
        'EOG': 'EOG Resources',
        'EPAM': 'EPAM Systems',
        'EQT': 'EQT Corporation',
        'EFX': 'Equifax',
        'EQIX': 'Equinix',
        'EQR': 'Equity Residential',
        'ERIE': 'Erie Indemnity',
        'ESS': 'Essex Property Trust',
        'EL': 'Estée Lauder Companies (The)',
        'EG': 'Everest Group',
        'EVRG': 'Evergy',
        'ES': 'Eversource Energy',
        'EXC': 'Exelon',
        'EXE': 'Expand Energy',
        'EXPE': 'Expedia Group',
        'EXPD': 'Expeditors International',
        'EXR': 'Extra Space Storage',
        'XOM': 'ExxonMobil',
        'FFIV': 'F5, Inc.',
        'FDS': 'FactSet',
        'FICO': 'Fair Isaac',
        'FAST': 'Fastenal',
        'FRT': 'Federal Realty Investment Trust',
        'FDX': 'FedEx',
        'FIS': 'Fidelity National Information Services',
        'FITB': 'Fifth Third Bancorp',
        'FSLR': 'First Solar',
        'FE': 'FirstEnergy',
        'FISV': 'Fiserv',
        'F': 'Ford Motor Company',
        'FTNT': 'Fortinet',
        'FTV': 'Fortive',
        'FOXA': 'Fox Corporation (Class A)',
        'FOX': 'Fox Corporation (Class B)',
        'BEN': 'Franklin Resources',
        'FCX': 'Freeport-McMoRan',
        'GRMN': 'Garmin',
        'IT': 'Gartner',
        'GE': 'GE Aerospace',
        'GEHC': 'GE HealthCare',
        'GEV': 'GE Vernova',
        'GEN': 'Gen Digital',
        'GNRC': 'Generac',
        'GD': 'General Dynamics',
        'GIS': 'General Mills',
        'GM': 'General Motors',
        'GPC': 'Genuine Parts Company',
        'GILD': 'Gilead Sciences',
        'GPN': 'Global Payments',
        'GL': 'Globe Life',
        'GDDY': 'GoDaddy',
        'GS': 'Goldman Sachs',
        'HAL': 'Halliburton',
        'HIG': 'Hartford (The)',
        'HAS': 'Hasbro',
        'HCA': 'HCA Healthcare',
        'DOC': 'Healthpeak Properties',
        'HSIC': 'Henry Schein',
        'HSY': 'Hershey Company (The)',
        'HPE': 'Hewlett Packard Enterprise',
        'HLT': 'Hilton Worldwide',
        'HOLX': 'Hologic',
        'HD': 'Home Depot (The)',
        'HON': 'Honeywell',
        'HRL': 'Hormel Foods',
        'HST': 'Host Hotels & Resorts',
        'HWM': 'Howmet Aerospace',
        'HPQ': 'HP Inc.',
        'HUBB': 'Hubbell Incorporated',
        'HUM': 'Humana',
        'HBAN': 'Huntington Bancshares',
        'HII': 'Huntington Ingalls Industries',
        'IBM': 'IBM',
        'IEX': 'IDEX Corporation',
        'IDXX': 'Idexx Laboratories',
        'ITW': 'Illinois Tool Works',
        'INCY': 'Incyte',
        'IR': 'Ingersoll Rand',
        'PODD': 'Insulet Corporation',
        'INTC': 'Intel',
        'IBKR': 'Interactive Brokers',
        'ICE': 'Intercontinental Exchange',
        'IFF': 'International Flavors & Fragrances',
        'IP': 'International Paper',
        'IPG': 'Interpublic Group of Companies (The)',
        'INTU': 'Intuit',
        'ISRG': 'Intuitive Surgical',
        'IVZ': 'Invesco',
        'INVH': 'Invitation Homes',
        'IQV': 'IQVIA',
        'IRM': 'Iron Mountain',
        'JBHT': 'J.B. Hunt',
        'JBL': 'Jabil',
        'JKHY': 'Jack Henry & Associates',
        'J': 'Jacobs Solutions',
        'JNJ': 'Johnson & Johnson',
        'JCI': 'Johnson Controls',
        'JPM': 'JPMorgan Chase',
        'K': 'Kellanova',
        'KVUE': 'Kenvue',
        'KDP': 'Keurig Dr Pepper',
        'KEY': 'KeyCorp',
        'KEYS': 'Keysight Technologies',
        'KMB': 'Kimberly-Clark',
        'KIM': 'Kimco Realty',
        'KMI': 'Kinder Morgan',
        'KKR': 'KKR & Co.',
        'KLAC': 'KLA Corporation',
        'KHC': 'Kraft Heinz',
        'KR': 'Kroger',
        'LHX': 'L3Harris',
        'LH': 'Labcorp',
        'LRCX': 'Lam Research',
        'LW': 'Lamb Weston',
        'LVS': 'Las Vegas Sands',
        'LDOS': 'Leidos',
        'LEN': 'Lennar',
        'LII': 'Lennox International',
        'LLY': 'Lilly (Eli)',
        'LIN': 'Linde plc',
        'LYV': 'Live Nation Entertainment',
        'LKQ': 'LKQ Corporation',
        'LMT': 'Lockheed Martin',
        'L': 'Loews Corporation',
        'LOW': 'Lowe\'s',
        'LULU': 'Lululemon Athletica',
        'LYB': 'LyondellBasell',
        'MTB': 'M&T Bank',
        'MPC': 'Marathon Petroleum',
        'MAR': 'Marriott International',
        'MMC': 'Marsh McLennan',
        'MLM': 'Martin Marietta Materials',
        'MAS': 'Masco',
        'MA': 'Mastercard',
        'MTCH': 'Match Group',
        'MKC': 'McCormick & Company',
        'MCD': 'McDonald\'s',
        'MCK': 'McKesson Corporation',
        'MDT': 'Medtronic',
        'MRK': 'Merck & Co.',
        'META': 'Meta Platforms',
        'MET': 'MetLife',
        'MTD': 'Mettler Toledo',
        'MGM': 'MGM Resorts',
        'MCHP': 'Microchip Technology',
        'MU': 'Micron Technology',
        'MSFT': 'Microsoft',
        'MAA': 'Mid-America Apartment Communities',
        'MRNA': 'Moderna',
        'MHK': 'Mohawk Industries',
        'MOH': 'Molina Healthcare',
        'TAP': 'Molson Coors Beverage Company',
        'MDLZ': 'Mondelez International',
        'MPWR': 'Monolithic Power Systems',
        'MNST': 'Monster Beverage',
        'MCO': 'Moody\'s Corporation',
        'MS': 'Morgan Stanley',
        'MOS': 'Mosaic Company (The)',
        'MSI': 'Motorola Solutions',
        'MSCI': 'MSCI Inc.',
        'NDAQ': 'Nasdaq, Inc.',
        'NTAP': 'NetApp',
        'NFLX': 'Netflix',
        'NEM': 'Newmont',
        'NWSA': 'News Corp (Class A)',
        'NWS': 'News Corp (Class B)',
        'NEE': 'NextEra Energy',
        'NKE': 'Nike, Inc.',
        'NI': 'NiSource',
        'NDSN': 'Nordson Corporation',
        'NSC': 'Norfolk Southern',
        'NTRS': 'Northern Trust',
        'NOC': 'Northrop Grumman',
        'NCLH': 'Norwegian Cruise Line Holdings',
        'NRG': 'NRG Energy',
        'NUE': 'Nucor',
        'NVDA': 'Nvidia',
        'NVR': 'NVR, Inc.',
        'NXPI': 'NXP Semiconductors',
        'ORLY': 'O\'Reilly Automotive',
        'OXY': 'Occidental Petroleum',
        'ODFL': 'Old Dominion',
        'OMC': 'Omnicom Group',
        'ON': 'ON Semiconductor',
        'OKE': 'Oneok',
        'ORCL': 'Oracle Corporation',
        'OTIS': 'Otis Worldwide',
        'PCAR': 'Paccar',
        'PKG': 'Packaging Corporation of America',
        'PLTR': 'Palantir Technologies',
        'PANW': 'Palo Alto Networks',
        'PSKY': 'Paramount Skydance Corporation',
        'PH': 'Parker Hannifin',
        'PAYX': 'Paychex',
        'PAYC': 'Paycom',
        'PYPL': 'PayPal',
        'PNR': 'Pentair',
        'PEP': 'PepsiCo',
        'PFE': 'Pfizer',
        'PCG': 'PG&E Corporation',
        'PM': 'Philip Morris International',
        'PSX': 'Phillips 66',
        'PNW': 'Pinnacle West Capital',
        'PNC': 'PNC Financial Services',
        'POOL': 'Pool Corporation',
        'PPG': 'PPG Industries',
        'PPL': 'PPL Corporation',
        'PFG': 'Principal Financial Group',
        'PG': 'Procter & Gamble',
        'PGR': 'Progressive Corporation',
        'PLD': 'Prologis',
        'PRU': 'Prudential Financial',
        'PEG': 'Public Service Enterprise Group',
        'PTC': 'PTC Inc.',
        'PSA': 'Public Storage',
        'PHM': 'PulteGroup',
        'PWR': 'Quanta Services',
        'QCOM': 'Qualcomm',
        'DGX': 'Quest Diagnostics',
        'Q': 'Qnity Electronics',
        'RL': 'Ralph Lauren Corporation',
        'RJF': 'Raymond James Financial',
        'RTX': 'RTX Corporation',
        'O': 'Realty Income',
        'REG': 'Regency Centers',
        'REGN': 'Regeneron Pharmaceuticals',
        'RF': 'Regions Financial Corporation',
        'RSG': 'Republic Services',
        'RMD': 'ResMed',
        'RVTY': 'Revvity',
        'HOOD': 'Robinhood Markets',
        'ROK': 'Rockwell Automation',
        'ROL': 'Rollins, Inc.',
        'ROP': 'Roper Technologies',
        'ROST': 'Ross Stores',
        'RCL': 'Royal Caribbean Group',
        'SPGI': 'S&P Global',
        'CRM': 'Salesforce',
        'SBAC': 'SBA Communications',
        'SLB': 'Schlumberger',
        'STX': 'Seagate Technology',
        'SRE': 'Sempra',
        'NOW': 'ServiceNow',
        'SHW': 'Sherwin-Williams',
        'SPG': 'Simon Property Group',
        'SWKS': 'Skyworks Solutions',
        'SJM': 'J.M. Smucker Company (The)',
        'SW': 'Smurfit Westrock',
        'SNA': 'Snap-on',
        'SOLS': 'Solstice Advanced Materials',
        'SOLV': 'Solventum',
        'SO': 'Southern Company',
        'LUV': 'Southwest Airlines',
        'SWK': 'Stanley Black & Decker',
        'SBUX': 'Starbucks',
        'STT': 'State Street Corporation',
        'STLD': 'Steel Dynamics',
        'STE': 'Steris',
        'SYK': 'Stryker Corporation',
        'SMCI': 'Supermicro',
        'SYF': 'Synchrony Financial',
        'SNPS': 'Synopsys',
        'SYY': 'Sysco',
        'TMUS': 'T-Mobile US',
        'TROW': 'T. Rowe Price',
        'TTWO': 'Take-Two Interactive',
        'TPR': 'Tapestry, Inc.',
        'TRGP': 'Targa Resources',
        'TGT': 'Target Corporation',
        'TEL': 'TE Connectivity',
        'TDY': 'Teledyne Technologies',
        'TER': 'Teradyne',
        'TSLA': 'Tesla, Inc.',
        'TXN': 'Texas Instruments',
        'TPL': 'Texas Pacific Land Corporation',
        'TXT': 'Textron',
        'TMO': 'Thermo Fisher Scientific',
        'TJX': 'TJX Companies',
        'TKO': 'TKO Group Holdings',
        'TTD': 'Trade Desk (The)',
        'TSCO': 'Tractor Supply',
        'TT': 'Trane Technologies',
        'TDG': 'TransDigm Group',
        'TRV': 'Travelers Companies (The)',
        'TRMB': 'Trimble Inc.',
        'TFC': 'Truist Financial',
        'TYL': 'Tyler Technologies',
        'TSN': 'Tyson Foods',
        'USB': 'U.S. Bancorp',
        'UBER': 'Uber',
        'UDR': 'UDR, Inc.',
        'ULTA': 'Ulta Beauty',
        'UNP': 'Union Pacific Corporation',
        'UAL': 'United Airlines Holdings',
        'UPS': 'United Parcel Service',
        'URI': 'United Rentals',
        'UNH': 'UnitedHealth Group',
        'UHS': 'Universal Health Services',
        'VLO': 'Valero Energy',
        'VTR': 'Ventas',
        'VLTO': 'Veralto',
        'VRSN': 'Verisign',
        'VRSK': 'Verisk Analytics',
        'VZ': 'Verizon',
        'VRTX': 'Vertex Pharmaceuticals',
        'VTRS': 'Viatris',
        'VICI': 'Vici Properties',
        'V': 'Visa Inc.',
        'VST': 'Vistra Corp.',
        'VMC': 'Vulcan Materials Company',
        'WRB': 'W. R. Berkley Corporation',
        'GWW': 'W. W. Grainger',
        'WAB': 'Wabtec',
        'WMT': 'Walmart',
        'DIS': 'Walt Disney Company (The)',
        'WBD': 'Warner Bros. Discovery',
        'WM': 'Waste Management',
        'WAT': 'Waters Corporation',
        'WEC': 'WEC Energy Group',
        'WFC': 'Wells Fargo',
        'WELL': 'Welltower',
        'WST': 'West Pharmaceutical Services',
        'WDC': 'Western Digital',
        'WY': 'Weyerhaeuser',
        'WSM': 'Williams-Sonoma, Inc.',
        'WMB': 'Williams Companies',
        'WTW': 'Willis Towers Watson',
        'WDAY': 'Workday, Inc.',
        'WYNN': 'Wynn Resorts',
        'XEL': 'Xcel Energy',
        'XYL': 'Xylem Inc.',
        'YUM': 'Yum! Brands',
        'ZBRA': 'Zebra Technologies',
        'ZBH': 'Zimmer Biomet',
        'ZTS': 'Zoetis',


        # Examples of additional S&P 500 Tickers you should add:
        'MMM': '3M Company',
        'ABT': 'Abbott Laboratories',
        'ACN': 'Accenture plc',
        'ADBE': 'Adobe Inc.',
        'AEP': 'American Electric Power Company Inc.',
        'AIG': 'American International Group Inc.',
        'ALL': 'Allstate Corporation',
        'BIIB': 'Biogen Inc.',
        'BKR': 'Baker Hughes Co.',
        'C': 'Citigroup Inc.',
        'DE': 'Deere & Company',
        'DIS': 'The Walt Disney Company',
        'F': 'Ford Motor Company',
        'GM': 'General Motors Co.',
        'HD': 'Home Depot Inc.',
        'INTC': 'Intel Corporation',
        'KO': 'The Coca-Cola Company',
        'LMT': 'Lockheed Martin Corporation',
        'MCD': "McDonald's Corporation",
        'MRK': 'Merck & Co. Inc.',
        'NKE': 'NIKE Inc.',
        'PEP': 'PepsiCo Inc.',
        'TGT': 'Target Corporation',
        'XOM': 'Exxon Mobil Corporation',
        'ZTS': 'Zoetis Inc.',
        
        # ... your other 400+ entries ...
    }
    
    print(f"✓ Created database with {len(ticker_to_company)} tickers")
    return ticker_to_company


def generate_ticker_and_company_maps(ticker_to_company):
    """
    Generate reverse mapping (company_to_ticker) from the ticker_to_company map.
    """
    
    company_to_ticker = {}
    
    for ticker, company in ticker_to_company.items():
        # Full company name (lowercase)
        company_lower = company.lower()
        company_to_ticker[company_lower] = ticker
        
        # Short versions without "Inc.", "Corp.", etc.
        company_short = company.lower()
        for suffix in [' inc.', ' inc', ' corporation', ' corp.', ' corp', ' company', ' co.', ' co', ' ltd.', ' ltd', ' n.v.', ' s.a.']:
            company_short = company_short.replace(suffix, '')
        company_short = company_short.strip()
        
        if company_short != company_lower and company_short:
            company_to_ticker[company_short] = ticker

        #1. Prepare for word extraction by cleaning up common web suffixes like .com
        company_clean_for_word_split = company_short
        for web_suffix in ['.com', '.co']:
            company_clean_for_word_split = company_clean_for_word_split.replace(web_suffix, '')
        
        # 2. Extract the true first word
        first_word = company_clean_for_word_split.split()[0] if company_clean_for_word_split else ''
        
        # 3. Apply checks and map
        if first_word and len(first_word) >= 4:  # At least 4 chars
            # Don't add very common words as first word
            if first_word not in ['block', 'general']:
                company_to_ticker[first_word] = ticker

        # Short ticker mapping (e.g., 'amd', 'v' to 'AMD', 'V')
        ticker_lower = ticker.lower()
        # This check is optional but good practice to avoid needless overwrite
        if ticker_lower not in company_to_ticker:
            company_to_ticker[ticker_lower] = ticker
            
    return company_to_ticker


def save_manual_database():
    """Save the large manual database to JSON file."""
    
    # 1. Use the large manual list
    ticker_to_company = create_manual_ticker_database()
    source = 'manual_large_list_no_deps'
    
    # 2. Generate reverse mappings
    company_to_ticker = generate_ticker_and_company_maps(ticker_to_company)
    
    print(f"✓ Created {len(company_to_ticker)} company name mappings")
    
    # Prepare database structure
    database = {
        'ticker_to_company': ticker_to_company,
        'company_to_ticker': company_to_ticker,
        'total_tickers': len(ticker_to_company),
        'total_companies': len(company_to_ticker),
        'created_at': datetime.now().isoformat(),
        'source': source
    }
    
    # Save to file
    utils_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(utils_dir, 'ticker_database.json')
    
    # Ensure all keys in the final dict are strings before saving
    final_database = {
        'ticker_to_company': {str(k): v for k, v in database['ticker_to_company'].items()},
        'company_to_ticker': {str(k): v for k, v in database['company_to_ticker'].items()},
        'total_tickers': database['total_tickers'],
        'total_companies': database['total_companies'],
        'created_at': database['created_at'],
        'source': database['source']
    }
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(final_database, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Saved to: {filepath}")
    print(f"✅ Ticker database ({source}) created successfully with {final_database['total_tickers']} tickers!")
    
    return final_database


def test_manual_database():
    """Test the created database."""
    
    print("\n" + "="*80)
    print("TESTING TICKER DATABASE")
    print("="*80)
    
    # Load the database we just created
    utils_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(utils_dir, 'ticker_database.json')
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            database = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: Database file not found at {filepath}. Run save_manual_database() first.")
        return
        
    ticker_to_company = database['ticker_to_company']
    company_to_ticker = database['company_to_ticker']
    
    print(f"\nSource: {database['source']}")
    print(f"✓ Loaded {len(ticker_to_company)} unique tickers")
    print(f"✓ Loaded {len(company_to_ticker)} company mappings")
    
    # Test ticker lookups
    print("\n1️⃣ Testing ticker -> company lookups:")
    # Test major stocks plus the last ticker in the list
    test_tickers = ['AAPL', 'TSLA', 'GOOGL']
    if len(ticker_to_company) > 3:
         # Safely get the last ticker to test coverage
         test_tickers.append(list(ticker_to_company.keys())[-1])
         
    for ticker in test_tickers:
        company = ticker_to_company.get(ticker, 'Not found')
        print(f"   {ticker:6s} -> {company}")
    
    print("\n✅ Tests complete!")


if __name__ == "__main__":
    # Create and save the manual database
    save_manual_database()
    
    # Test it
    test_manual_database()