import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Weka seed ili data zisibadilike kila mara
np.random.seed(42)

num_claims = 500

# 1. Tarehe za ajali (Accident Dates)
start_date = pd.Timestamp('2019-01-01')
end_date = pd.Timestamp('2024-12-31')

# Tengeneza tarehe kwa kutumia pandas date range
random_timestamps = np.random.uniform(start_date.value, end_date.value, num_claims)
accident_dates = pd.to_datetime(random_timestamps)

# 2. Ucheleweshaji wa kuripoti (Reporting Delays)
reporting_delays = np.random.exponential(scale=60, size=num_claims).astype(int)
reported_dates = [acc + pd.Timedelta(days=int(delay)) for acc, delay in zip(accident_dates, reporting_delays)]

# 3. Ucheleweshaji wa malipo (Payment Delays)
payment_delays = np.random.exponential(scale=180, size=num_claims).astype(int)
payment_dates = [rep + pd.Timedelta(days=int(delay)) for rep, delay in zip(reported_dates, payment_delays)]

# 4. Kiasi cha madai (Amounts in TZS)
paid_amounts = np.random.lognormal(mean=14.5, sigma=1.0, size=num_claims).round(-3)
incurred_amounts = (paid_amounts * np.random.uniform(1.0, 1.3, size=num_claims)).round(-3)

# Tengeneza DataFrame
df = pd.DataFrame({
    'ClaimID': [f'CLM-TZ-{1000 + i}' for i in range(num_claims)],
    'PolicyID': [f'POL-MOT-{5000 + np.random.randint(1, 200)}' for _ in range(num_claims)],
    'AccidentDate': [d.strftime('%Y-%m-%d') for d in accident_dates],
    'ReportedDate': [d.strftime('%Y-%m-%d') for d in reported_dates],
    'PaymentDate': [d.strftime('%Y-%m-%d') for d in payment_dates],
    'ClaimStatus': np.random.choice(['Closed', 'Open'], size=num_claims, p=[0.75, 0.25]),
    'PaidAmount': paid_amounts,
    'IncurredAmount': incurred_amounts
})

# Hifadhi kama CSV
df.to_csv('claims_data.csv', index=False)
print("SUCCESS: File la 'claims_data.csv' limetengenezwa kikamilifu!")