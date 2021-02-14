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
    EXPEXT 0.022 ; 1277
    IMPDIS 0.057 ; -749
    SENTIM -0.054 ; 63
    ATTDEP -0.017 ; -1210
    Method of converting: OLS snip?
    """
    
    personality = {}
    total = 0
    #TODO: implement OLS snipping
    for symbol, num in portfolio:
        total = total + num

    return personality

def compare_profiles(p1, p2, finnhub_client):
    pass
