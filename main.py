import os
import requests
import pandas as pd
from dotenv import load_dotenv
import time

load_dotenv()

def get_wallet_metrics(address):
    api_key = os.getenv('ETHERSCAN_API_KEY')
    base_url = 'https://api.etherscan.io/api'
    
    tx_response = requests.get(f'{base_url}?module=proxy&action=eth_getTransactionCount&address={address}&apikey={api_key}')
    tx_count = int(tx_response.json()['result'], 16)
    
    balance_response = requests.get(f'{base_url}?module=account&action=balance&address={address}&apikey={api_key}')
    eth_balance = int(balance_response.json()['result']) / 1e18
    
    history_response = requests.get(f'{base_url}?module=account&action=txlist&address={address}&startblock=0&endblock=99999999&page=1&offset=1&sort=asc&apikey={api_key}')
    history = history_response.json()['result']
    
    wallet_age = 0
    if history and len(history) > 0:
        first_tx_time = int(history[0]['timeStamp'])
        current_time = int(time.time())
        wallet_age = (current_time - first_tx_time) / (24 * 3600)
    
    return tx_count, eth_balance, wallet_age

def calculate_risk_score(tx_count, balance, age_days):
    risk_score = 400
    
    # Transaction frequency risk
    if tx_count > 2000:
        risk_score += 200
    elif tx_count > 1000:
        risk_score += 120
    elif tx_count > 500:
        risk_score += 80
    elif tx_count > 100:
        risk_score += 40
    
    # Balance-based risk
    if balance < 0.01:
        risk_score += 150
    elif balance > 500:
        risk_score += 100
    elif balance > 100:
        risk_score += 50
    
    # Age-based risk
    if age_days < 7:
        risk_score += 180
    elif age_days < 30:
        risk_score += 120
    elif age_days < 90:
        risk_score += 80
    elif age_days < 365:
        risk_score += 40
    
    return min(max(risk_score, 100), 950)

def process_wallets():
    wallet_df = pd.read_csv('wallet id.csv')
    scored_wallets = []
    
    for index, wallet_address in enumerate(wallet_df['wallet_id']):
        try:
            tx_count, balance, age = get_wallet_metrics(wallet_address)
            score = calculate_risk_score(tx_count, balance, age)
            
            scored_wallets.append({
                'wallet_id': wallet_address,
                'score': score
            })
            
            print(f"Processed {index + 1}/{len(wallet_df)} wallets")
            time.sleep(0.25)
            
        except Exception as e:
            print(f"Error processing {wallet_address}: {str(e)}")
            scored_wallets.append({
                'wallet_id': wallet_address,
                'score': 500
            })
    
    results_df = pd.DataFrame(scored_wallets)
    results_df.to_csv('wallet_risk_scores.csv', index=False)
    print("Risk scoring completed.")

if __name__ == "__main__":
    process_wallets()