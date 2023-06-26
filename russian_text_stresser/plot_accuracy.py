import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv('correctness_tests/benchmark_results.tsv', sep="\t")
sns.barplot(data=df, x="System", y="Percentage correct words")
# Rotate x-axis labels
plt.xticks(rotation=45)
plt.tight_layout()

plt.savefig('correctness_tests/accuracy.png')