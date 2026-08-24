import pandas as pd
import numpy as np
from triangle_builder import cumulative_triangle
from link_ratios import weighted_link_ratios, tail_factor

# 1. Kokotoa Cumulative Development Factors (CDF) kurudi nyuma kutoka Ultimate
factors_list = list(weighted_link_ratios.values()) + [tail_factor]
num_years = len(cumulative_triangle)

cdfs = []
for i in range(len(factors_list)):
    # CDF ni zao (product) la link ratios zote zilizobaki hadi tail
    cdf_val = np.prod(factors_list[i:])
    cdfs.append(cdf_val)

# 2. Pata Latest Cumulative Paid Loss kwa kila Accident Year (diagonal ya mwisho)
latest_paid = []
for i, ay in enumerate(cumulative_triangle.index):
    # Pata element ya mwisho inayopatikana kwenye diagonal
    dev_col = num_years - 1 - i
    latest_paid.append(cumulative_triangle.loc[ay, dev_col])

# 3. Tengeneza Summary DataFrame ya Reserving
summary_df = pd.DataFrame({
    'AccidentYear': cumulative_triangle.index,
    'LatestPaid_TZS': latest_paid,
    'CDF': cdfs[::-1] # Geuza mpangilio uendane na Accident Years (zamani -> mpya)
})

# 4. Kokotoa Ultimate Losses na IBNR Reserves
summary_df['UltimateLoss_TZS'] = summary_df['LatestPaid_TZS'] * summary_df['CDF']
summary_df['IBNR_Reserve_TZS'] = summary_df['UltimateLoss_TZS'] - summary_df['LatestPaid_TZS']

# 5. Kokotoa Jumla (Totals)
totals = pd.Series({
    'AccidentYear': 'TOTAL',
    'LatestPaid_TZS': summary_df['LatestPaid_TZS'].sum(),
    'CDF': np.nan,
    'UltimateLoss_TZS': summary_df['UltimateLoss_TZS'].sum(),
    'IBNR_Reserve_TZS': summary_df['IBNR_Reserve_TZS'].sum()
})

summary_df = pd.concat([summary_df, pd.DataFrame([totals])], ignore_index=True)

print("\n=======================================================================")
print("          FINAL IBNR RESERVING SUMMARY TABLE (TZS)                     ")
print("=======================================================================\n")
print(summary_df.to_string(index=False, formatters={
    'LatestPaid_TZS': '{:,.0f}'.format,
    'CDF': '{:.4f}'.format,
    'UltimateLoss_TZS': '{:,.0f}'.format,
    'IBNR_Reserve_TZS': '{:,.0f}'.format
}))
print("\n=======================================================================\n")