import pandas as pd
import numpy as np

# 1. Load claims data
df = pd.read_csv('claims_data.csv')

# 2. Convert date strings to datetime objects
df['AccidentDate'] = pd.to_datetime(df['AccidentDate'])
df['PaymentDate'] = pd.to_datetime(df['PaymentDate'])

# 3. Extract Accident Year (AY) and Payment Year (PY)
df['AccidentYear'] = df['AccidentDate'].dt.year
df['PaymentYear'] = df['PaymentDate'].dt.year

# 4. Calculate Development Year (DevYear = PaymentYear - AccidentYear)
df['DevYear'] = df['PaymentYear'] - df['AccidentYear']

# Filter out invalid records where payment precedes accident date
df = df[df['DevYear'] >= 0]

# 5. Build Incremental Loss Triangle (Sum of Paid Amounts)
incremental_triangle = df.pivot_table(
    index='AccidentYear',
    columns='DevYear',
    values='PaidAmount',
    aggfunc='sum'
).fillna(0)

# 6. Accumulate across development years (Cumulative Loss Triangle)
cumulative_triangle = incremental_triangle.cumsum(axis=1)

print("\n========================================================")
print("     CUMULATIVE PAID LOSS TRIANGLE (TZS)                ")
print("========================================================\n")
print(cumulative_triangle.round(0))
print("\n========================================================\n")