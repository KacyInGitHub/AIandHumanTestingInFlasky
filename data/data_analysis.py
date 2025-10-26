import numpy as np
import pandas as pd
from scipy.stats import shapiro, ttest_ind, wilcoxon, ranksums
from math import sqrt


# -----------------------------
# calculate Cohen's d
# -----------------------------
def cohen_d(x, y):
    nx = len(x)
    ny = len(y)
    dof = nx + ny - 2
    pooled_std = np.sqrt(((nx - 1) * np.std(x, ddof=1) ** 2 + (ny - 1) * np.std(y, ddof=1) ** 2) / dof)
    return (np.mean(x) - np.mean(y)) / pooled_std


# -----------------------------
# calculate 95% CI
# -----------------------------
def mean_ci(x, confidence=0.95):
    n = len(x)
    m = np.mean(x)
    se = np.std(x, ddof=1) / sqrt(n)
    h = 1.96 * se  # The Z value corresponding to the 95% confidence interval
    return m - h, m + h


# Each row represents a function and each column represents an indicator value.
data = {
    "line_coverage_AI": [12/28, 125/164, 32/32, 32/32],
    "line_coverage_Human": [26/28, 147/164, 32/32, 21/32],
    "branch_coverage_AI": [5/9, 5/12, 4/4, 4/4],
    "branch_coverage_Human": [7/9, 8/12, 4/4, 3/4],
    "exec_rate_AI": [2/3,11/12,4/6,4/5],
    "exec_rate_Human": [2/3,12/12,5/6,5/5],
    "mutation_score_AI": [1/5, 5/8, 4/4, 3/3],
    "mutation_score_Human": [4/5, 6/8, 4/4, 2/3],
    "fun_coverage_AI":[1,1,1,1],
    "fun_coverage_Human":[1,1,1,1]
}

df = pd.DataFrame(data)


# -----------------------------
# analyze function
# -----------------------------
def analyze_metric(group_A, group_B, metric_name):
    print(f"\n=== {metric_name} ===")

    # normality test
    stat_A, p_A = shapiro(group_A)
    stat_B, p_B = shapiro(group_B)
    normal_A = p_A > 0.05
    normal_B = p_B > 0.05
    print(f"GroupA normality p={p_A:.4f}, {'Approximately normal' if normal_A else 'non-normal'}")
    print(f"GroupB normality p={p_B:.4f}, {'Approximately normal' if normal_B else 'non-normal'}")

    # Select the inspection method
    if normal_A and normal_B:
        # independent-samples T test（Welch t-test）
        t_stat, p_val = ttest_ind(group_A, group_B, equal_var=False)
        method = "Independent samples t-test（Welch t-test）"
    else:
        # Wilcoxon rank sum test
        t_stat, p_val = ranksums(group_A, group_B)
        method = "Wilcoxon rank-sum test (Non-parametric)"

    # Calculate the effect size
    d = cohen_d(group_A, group_B)

    # 95% confidence interval
    ci_A = mean_ci(group_A)
    ci_B = mean_ci(group_B)

    # output result
    print(f"method: {method}")
    print(f"statistical magnitude t={t_stat:.4f}, p={p_val:.4f}")
    print(f"Cohen's d = {d:.4f}")
    print(f"mean value of Group A={np.mean(group_A):.4f}, 95% CI={ci_A}")
    print(f"mean value of Group B={np.mean(group_B):.4f}, 95% CI={ci_B}")


# -----------------------------
# Traverse all indicators
# -----------------------------
metrics = ["line_coverage", "mutation_score", "branch_coverage", "exec_rate", "fun_coverage"]

for metric in metrics:
    analyze_metric(df[f"{metric}_AI"], df[f"{metric}_Human"], metric_name=metric)

