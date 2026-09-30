import pandas as pd

df = pd.read_csv('results/results_sarsop_baseline.csv')
print("SARSOP Baseline")
print(df[['env', 'agent', 'reward', 'reward_se', 'usage', 'usage_se', 'success']])

