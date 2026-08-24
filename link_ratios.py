import pandas as pd
import numpy as np
from triangle_builder import cumulative_triangle

# 1. Calculate Age-to-Age Ratios for individual cells
link_ratios_matrix = cumulative_triangle.shift(-1, axis=1) / cumulative_triangle

# 2. Calculate Weighted Average Link Ratios (Volume-Weighted)
weighted_link_ratios = {}
num_dev_years = cumulative_triangle.shape[1]

for dev_year in range(num_dev_years - 1):
    # Select available cumulative losses for dev_year and dev_year + 1
    current_losses = cumulative_triangle.iloc[:(num_dev_years - dev_year - 1), dev_year]
    next_losses = cumulative_triangle.iloc[:(num_dev_years - dev_year - 1), dev_year + 1]
    
    # Volume-weighted average formula: sum(next) / sum(current)
    weighted_factor = next_losses.sum() / current_losses.sum()
    weighted_link_ratios[f'{dev_year}-{dev_year+1}'] = weighted_factor

# Convert to Series for clean viewing
link_ratios_series = pd.Series(weighted_link_ratios)

# 3. Assume a Tail Factor for complete development (typically 1.00 if fully developed)
tail_factor = 1.000

print("\n========================================================")
print("     DEVELOPMENT LINK RATIOS (AGE-TO-AGE FACTORS)        ")
print("========================================================\n")
print(link_ratios_series.round(4))
print(f"\nAssumed Tail Factor (Dev {num_dev_years-1}-Ultimate): {tail_factor:.4f}")
print("========================================================\n")