"""
The **algorithm** module provides various algorithms for generating personality and compatability profiles.
"""

from math import exp, floor
import sys, ast

# TODO: cache calls to Finnhub
def generate_profile(portfolio, finnhub_client):
    """
    Generates personality profile from portfolio.

    #### Parameters
    - **portfolio : (str, int) dict** - Dictionary of stock symbol and number held pairs.
    - **finnhub_client : finnhub.Client** - Finnhub API client for financial data.

    #### Return Value
    **(str, int) dict** - Dictionary of personality factors and values. 
    """

    """
    Dependent Var MB, SIZE regression values
    EXPEXT 0.026 ; 854
    IMPDIS 0.027 ; -1004
    SENTIM -0.074 ; 17
    ATTDEP 0.000 ; -1010
    Interc 1.892 ; 12785
    Method of converting: OLS snip?
    """
    
    person = {'EXPEXT': 0.0,
        'IMPDIS': 0.0,
        'ATTDEP': 0.0,
        'SENTIM': 0.0,
        'INVEST': 0.0,      # float: total dollar value of portfolio 
        'HOBBIE': ""        # str: favorite hobby based on most popular sector by num of shares
    }
    totalNumShares = 0
    totalValueShares = 0
    intermediates = []
    sectors = {}
    #TODO: implement OLS snipping

    for sym, num in portfolio.items():
        totalNumShares = totalNumShares + int(num)
        financials = finnhub_client.company_basic_financials(sym, 'all')['metric']
        price = (float(financials['52WeekHigh']) + float(financials['52WeekLow']))/2.0
        
        MB = price / float(financials['bookValuePerShareAnnual'])
        Size = float(financials['marketCapitalization'])

        # Size is in units: $ million
        if Size > 14e3: # cap the market cap
            Size = 14e3
        
        E = 19.23*(MB - 1.7364) + 0.0006*(Size + 4124.38)
        I = 18.518*(MB - 1.80656) + 0.0005*(12679.64 - Size)
        S = 13.514*(2.37625 - MB)
        A = 0.001*(14271.26 - Size)

        intermediates.append({'EXPEXT': E,
            'IMPDIS': I,
            'ATTDEP': A,
            'SENTIM': S,
            'NUM': int(num)
        })

        totalValueShares = totalValueShares + (price * int(num))

        # Assign sector weight based on number of shares owned in sector
        companyProfile = finnhub_client.company_profile2(symbol=sym)
        sector = companyProfile['finnhubIndustry']
        if sector in sectors:
            sectors[sector] = sectors[sector] + num
        else:
            sectors[sector] = num

    E = I = S = A = 0.0
    for inter in intermediates:
        E = E + (inter['NUM']/totalNumShares)*inter['EXPEXT']
        I = I + (inter['NUM']/totalNumShares)*inter['IMPDIS']
        S = S + (inter['NUM']/totalNumShares)*inter['SENTIM']
        A = A + (inter['NUM']/totalNumShares)*inter['ATTDEP']
    # 472, 442, 14, 110
    person['EXPEXT'] = floor(100/(1+exp(-E/120))) # Old: 118
    person['IMPDIS'] = floor(100/(1+exp(-I/115))) # Old: 111
    person['SENTIM'] = floor(100/(1+exp(-S/30))) # Old: 4
    person['ATTDEP'] = floor(100/(1+exp(-A/30))) # Old: 28

    # Assign investment rank
    # based on U.S. Census Bureau 2021 report of median household wealth quintiles
    if totalValueShares < 4715:                # bottom 20%
        person['INVEST'] = 0
    elif 4715 <= totalValueShares < 34940:
        person['INVEST'] = 1
    elif 34940 <= totalValueShares < 80120:    # middle 20%
        person['INVEST'] = 2
    elif 80120 <= totalValueShares < 188300:
        person['INVEST'] = 3
    elif 188300 <= totalValueShares < 554700:
        person['INVEST'] = 4
    else:                                       # top 20%
        person['INVEST'] = 5

    # Find most popular sector
    # If there is a tie, only chooses the first sector found
    if sectors:
        person['HOBBIE'] = max(sectors, key=sectors.get)

    return person

def compare_profiles(person1, person2):
    """
    Generates compatability profile from two personality profiles.

    #### Parameters
    - **person1 : (str, int) dict** - Personality profile for Person 1.
    - **person2 : (str, int) dict** - Personality profile for Person 2.
    - **finnhub_client : finnhub.Client** - Finnhub API client for financial data.

    #### Return Value
    **(str, int) dict** - Dictionary of compatability factors and values.
    """

    # Compatibility Profile
    compatProfile = {'EXPEXT': 0.0,
        'IMPDIS': 0.0,
        'ATTDEP': 0.0,
        'SENTIM': 0.0,
        'INVDIF': 0,        # int: difference in investment quintile
        'HOBCHK': "",       # str: name of most popular sector if matched, "" otherwise
        'COMPAT': 0.0       # float: compatibility percentage
    }

    # Check keys exist in profiles
    if not all (k in person1 for k in ('EXPEXT','IMPDIS','ATTDEP','SENTIM','INVEST','HOBBIE')):
        print("Person1 profile is missing keys", file=sys.stderr)
        return compatProfile
    elif not all (k in person2 for k in ('EXPEXT','IMPDIS','ATTDEP','SENTIM','INVEST','HOBBIE')):
        print("Person2 profile is missing keys", file=sys.stderr)
        return compatProfile
    
    # closeness(a1, a2) = aMax - |a1 - a2|
    #       aMax = max(range of a)
    #       range of a = range of a1 = range of a2 = 0->100
    compatProfile['EXPEXT'] = 100 - floor(abs(person1['EXPEXT'] - person2['EXPEXT']))
    compatProfile['IMPDIS'] = 100 - floor(abs(person1['IMPDIS'] - person2['IMPDIS']))
    compatProfile['ATTDEP'] = 100 - floor(abs(person1['ATTDEP'] - person2['ATTDEP']))
    compatProfile['SENTIM'] = 100 - floor(abs(person1['SENTIM'] - person2['SENTIM']))

    # Simple average of personality category closeness
    compatibility = (compatProfile['EXPEXT'] + compatProfile['IMPDIS'] + 
                    compatProfile['ATTDEP'] + compatProfile['SENTIM']) / 4

    # Investment (amount of money invested in market) Factor: +/-15% based on wealth bracket
    compatProfile['INVDIF'] = abs(person1['INVEST'] - person2['INVEST'])
    compatibility += (compatProfile['INVDIF'] - 2.5) * -6

    # Interests/Hobbies Factor : +10% compatibility on most popular sector match
    if (person1['HOBBIE'] == person2['HOBBIE']):
        compatibility += 10
        compatProfile['HOBCHK'] = person1['HOBBIE']

    compatProfile['COMPAT'] = round(max(0, min(compatibility, 100)), 1)     # clamp in range 0-100

    return compatProfile
