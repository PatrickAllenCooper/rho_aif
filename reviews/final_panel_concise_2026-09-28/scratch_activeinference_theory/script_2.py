import pandas as pd
df = pd.read_csv('results/results_summary.csv')
print(df[df['env'].isin(['Tiger', 'Diagnosis', 'Bandit']) & df['agent'].isin(['PlanningAgent', 'EFEAgent'])][['env', 'agent', 'reward', 'success']])
