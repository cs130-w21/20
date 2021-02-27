from math import exp, floor

# TODO: cache calls to Finnhub
def generate_profile(portfolio, finnhub_client):
    """
    Generates personality profile from portfolio

    Parameters
    ----------
    portfolio : (str, int) dict
        Dictionary of stock symbol and number held
        pairs.
    finnhub_client : finnhub.Client
        Finnhub API client for financial data

    Returns
    -------
    (str, int) dict
        Dictionary of personality factors and
        values.
    
    Notes
    -------
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
    }
    total = 0
    intermediates = []
    #TODO: implement OLS snipping
    
    for symbol, num in portfolio.items():
        total = total + int(num)
        financials = finnhub_client.company_basic_financials(symbol, 'all')['metric']
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
    E = I = S = A = 0.0
    for inter in intermediates:
        E = E + (inter['NUM']/total)*inter['EXPEXT']
        I = I + (inter['NUM']/total)*inter['IMPDIS']
        S = S + (inter['NUM']/total)*inter['SENTIM']
        A = A + (inter['NUM']/total)*inter['ATTDEP']
    # 472, 442, 14, 110
    person['EXPEXT'] = floor(100/(1+exp(-E/118)))
    person['IMPDIS'] = floor(100/(1+exp(-I/111)))
    person['SENTIM'] = floor(100/(1+exp(-S/4)))
    person['ATTDEP'] = floor(100/(1+exp(-A/28)))
    return person

def compare_profiles(person1, person2):
    """
    Generates personality profile from portfolio

    Parameters
    ----------
    person1 : (str, int) dict
        Dictionary of personality profile for Person 1.
    person2 : (str, int) dict
        Dictionary of personality profile for Person 2.

    Returns
    -------
    (str, int) dict
        Dictionary of personality factors and values 
        for compatibility between Person 1 and 2.
    """

    # closeness of categories
    closeness = {'EXPEXT': 0.0,
        'IMPDIS': 0.0,
        'ATTDEP': 0.0,
        'SENTIM': 0.0,
    }
    
    # closeness(a1, a2) = aMax - (aMax * (|a1 - a2| / aMax)
    #       aMax = max(range of a)
    #       range of a = range of a1 = range of a2 = 0->100
    closeness['EXPEXT'] = 100 - floor(100 * (abs(person1['EXPEXT'] - person2['EXPEXT']) / 100))
    closeness['IMPDIS'] = 100 - floor(100 * (abs(person1['IMPDIS'] - person2['IMPDIS']) / 100))
    closeness['ATTDEP'] = 100 - floor(100 * (abs(person1['ATTDEP'] - person2['ATTDEP']) / 100))
    closeness['SENTIM'] = 100 - floor(100 * (abs(person1['SENTIM'] - person2['SENTIM']) / 100))

    # Simple average
    compatibility = (closeness['EXPEXT'] + closeness['EXPEXT'] + 
                    closeness['EXPEXT'] + closeness['EXPEXT']) / 4

    return compatibility
