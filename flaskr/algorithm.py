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
        
        E = 30.78*(MB - 1.7364) + 0.00024*(Size + 4124.38)
        I = 29.63*(MB - 1.80656) + 0.0002*(12679.64 - Size)
        S = 10.814*(2.37625 - MB) + 0.0118*(Size - 4895.96)
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
    person['EXPEXT'] = E
    person['IMPDIS'] = I
    person['SENTIM'] = S
    person['ATTDEP'] = A
    return person

def compare_profiles(p1, p2, finnhub_client):
    pass
