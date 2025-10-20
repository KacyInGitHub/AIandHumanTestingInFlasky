import numpy as np
import pandas as pd
from scipy.stats import shapiro, ttest_ind, wilcoxon, ranksums
from math import sqrt


# -----------------------------
# 自定义函数：计算 Cohen's d
# -----------------------------
def cohen_d(x, y):
    nx = len(x)
    ny = len(y)
    dof = nx + ny - 2
    pooled_std = np.sqrt(((nx - 1) * np.std(x, ddof=1) ** 2 + (ny - 1) * np.std(y, ddof=1) ** 2) / dof)
    return (np.mean(x) - np.mean(y)) / pooled_std


# -----------------------------
# 自定义函数：计算 95% CI
# -----------------------------
def mean_ci(x, confidence=0.95):
    n = len(x)
    m = np.mean(x)
    se = np.std(x, ddof=1) / sqrt(n)
    h = 1.96 * se  # 对应95%置信区间的Z值
    return m - h, m + h


# -----------------------------
# 输入数据示例：每个指标两组
# 可以改成从 CSV 或 Excel 读取
# -----------------------------
# 每行是函数，每列是指标值
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
# 分析函数
# -----------------------------
def analyze_metric(group_A, group_B, metric_name):
    print(f"\n=== {metric_name} ===")

    # 正态性检验
    stat_A, p_A = shapiro(group_A)
    stat_B, p_B = shapiro(group_B)
    normal_A = p_A > 0.05
    normal_B = p_B > 0.05
    print(f"A组正态性 p={p_A:.4f}, {'近似正态' if normal_A else '非正态'}")
    print(f"B组正态性 p={p_B:.4f}, {'近似正态' if normal_B else '非正态'}")

    # 选择检验方法
    if normal_A and normal_B:
        # 独立样本t检验（Welch t-test）
        t_stat, p_val = ttest_ind(group_A, group_B, equal_var=False)
        method = "独立样本 t 检验（Welch t-test）"
    else:
        # Wilcoxon秩和检验
        t_stat, p_val = ranksums(group_A, group_B)
        method = "Wilcoxon rank-sum 检验（非参数）"

    # 计算效应量
    d = cohen_d(group_A, group_B)

    # 95%置信区间
    ci_A = mean_ci(group_A)
    ci_B = mean_ci(group_B)

    # 输出结果
    print(f"检验方法: {method}")
    print(f"统计量 t={t_stat:.4f}, p={p_val:.4f}")
    print(f"Cohen's d = {d:.4f}")
    print(f"A组均值={np.mean(group_A):.4f}, 95% CI={ci_A}")
    print(f"B组均值={np.mean(group_B):.4f}, 95% CI={ci_B}")


# -----------------------------
# 遍历所有指标
# -----------------------------
metrics = ["line_coverage", "mutation_score", "branch_coverage", "exec_rate", "fun_coverage"]

for metric in metrics:
    analyze_metric(df[f"{metric}_AI"], df[f"{metric}_Human"], metric_name=metric)

