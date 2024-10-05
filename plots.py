import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def plot_cloud_coverage(df):
    """Plot cloud coverage over time."""
    plt.figure(figsize=(10, 6))
    sns.lineplot(x="Date", y="CloudCoverage", data=df, marker="o")
    plt.title("Cloud Coverage Over Time")
    plt.xlabel("Date")
    plt.ylabel("Cloud Coverage (%)")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plt.show()
