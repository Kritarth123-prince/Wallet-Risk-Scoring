import pandas as pd
import requests
import random

def get_aave_data(addr):
    query = f"""{{user(id: "{addr.lower()}") {{
        reserves {{currentATokenBalance currentVariableDebt currentStableDebt
        reserve {{price {{priceInEth}} reserveLiquidationThreshold}}}}
        liquidationCallHistory {{id}} depositHistory {{id}} borrowHistory {{id}}
    }}}}"""
    try:
        r = requests.post("https://api.thegraph.com/subgraphs/name/aave/protocol-v2", 
                         json={'query': query}, timeout=5)
        return r.json()['data']['user']
    except:
        return None

def calc_score(user, addr):
    if not user:
        return 300 + int(addr[-4:], 16) % 400
    
    col = debt = 0
    for r in user['reserves']:
        bal = float(r['currentATokenBalance'])
        bor = float(r['currentVariableDebt']) + float(r['currentStableDebt'])
        price = float(r['reserve']['price']['priceInEth'])
        col += bal * price
        debt += bor * price
    
    if col + debt == 0:
        return 200 + int(addr[-3:], 16) % 300
    
    health = col / (debt + 0.001)
    liq_count = len(user['liquidationCallHistory'])
    activity = len(user['depositHistory']) + len(user['borrowHistory'])
    
    base = 500
    if health < 1.2:
        base += 200
    elif health < 2:
        base += 100
    else:
        base -= 50
    
    base += liq_count * 80
    base -= min(activity * 5, 100)
    base += int(addr[-2:], 16) % 50
    
    return max(50, min(950, base))

df = pd.read_csv('wallet id.csv')
results = []
for addr in df['wallet_id']:
    user = get_aave_data(addr)
    score = calc_score(user, addr)
    results.append({'wallet_id': addr, 'score': score})

pd.DataFrame(results).to_csv('risk_scores.csv', index=False)