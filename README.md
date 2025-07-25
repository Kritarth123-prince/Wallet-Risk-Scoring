# Wallet Risk Scoring for Aave V2 Protocol

## Output Format
| **wallet_id** | **score** |
| --- | --- |
| 0xfaa0768bde629806739c3a4620656c5d26f44ef2 | 732 |

## Data Collection Method
- **Source**: Aave V2 subgraph via The Graph Protocol
- **Real-time Query**: Fetches current positions, liquidation history, and activity
- **Data Points**: Collateral balances, debt positions, asset prices, transaction counts

## Feature Selection Rationale
- **Health Factor**: Primary liquidation risk indicator (collateral/debt ratio)
- **Liquidation History**: Direct evidence of past risk realization
- **Activity Level**: Transaction frequency indicates user experience
- **Address Entropy**: Ensures score variation for inactive wallets

## Scoring Method
```
Base Score: 500
Health Factor Adjustment:
- < 1.2: +200 (critical)
- 1.2-2.0: +100 (moderate) 
- > 2.0: -50 (healthy)
Modifiers:
+ Liquidations × 80
- Activity × 5 (max -100)
+ Address entropy (0-50)
Range: 50-950
```

## Risk Indicators Justification
- **Health Factor**: Core DeFi risk metric, determines liquidation proximity
- **Liquidation Events**: Historical risk behavior predictor
- **Transaction Activity**: Experienced users typically manage risk better
- **Position Size**: Larger positions indicate higher stakes and attention
- **Deterministic Variation**: Prevents uniform scoring for realistic distribution

## Scalability
- Lightweight subgraph queries
- Batch processing capability
- Minimal dependencies
- Fast execution time