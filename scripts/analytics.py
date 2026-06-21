import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

plt.ion()

def count_per_loc(df, name):
    print(f"Propiedades por ubicación ({name}):\n", df['Location'].value_counts())
    
def mean_by_location(df, col):
    df_gr = df.groupby('Location')[col].agg(['mean','count']).assign(mean=lambda x: x['mean'].round(1)).sort_values('mean')
    print(df_gr)
    return df_gr.index

def print_numeric_columns_value_counts(df):
    numeric_cols = df.select_dtypes(include=np.number).columns
    for col in numeric_cols:
        print(df[col].value_counts(dropna=False).sort_index())
        print('\n')
        
def plot_price_vs_size(df, title, price_col, size_col):
    plt.figure(figsize=(10, 6))
    plt.scatter(df[size_col], df[price_col], alpha=0.7, edgecolor='k')
    plt.title(title)
    plt.xlabel(size_col)
    plt.ylabel(price_col)
    plt.grid(True)
    plt.show()
    
def plot_histogram(df, t, c):
    plt.figure(figsize=(10, 6))
    sns.histplot(df[c], kde=True, bins=30)
    plt.title('Histogram '+t)
    plt.xlabel(c)
    plt.ylabel('Frequency')
    plt.show()

def plot_correlation_heatmap(df, cols, title):
    plt.figure(figsize=(8, 6))
    correlation_matrix = df[cols].corr()
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f', cbar=True)
    plt.title(title + ' - Corr b/ Var', fontsize=16)
    plt.show()

def plot_boxplot(df, x_col, y_col, locations, group_num=None, char=10):
    df_filtered = df[df[x_col].isin(locations)]
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=df_filtered, x=x_col, y=y_col)
    title = f'{y_col} by {x_col} (group {group_num})'
    plt.title(title)
    plt.xlabel(x_col)
    plt.ylabel(y_col)
    labels = [label.get_text()[:char] for label in plt.gca().get_xticklabels()]
    plt.gca().set_xticklabels(labels)
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.show()

def boxplot_location_groups(df, y_col='Price/SqM', n_groups=4):
    if 'Location' not in df.columns:
        print("La columna 'Location' no existe en este dataset.")
        return
        
    locations = df['Location'].unique()
    group_size = len(locations) // n_groups
    if group_size == 0:
        group_size = 1
        
    location_groups = [locations[i*group_size:(i+1)*group_size] for i in range(n_groups)]
    if len(locations) % n_groups != 0 and n_groups > 0:
        location_groups[-1] = np.append(location_groups[-1], locations[n_groups*group_size:])
        
    for i, group in enumerate(location_groups, 1):
        if len(group) > 0:
            plot_boxplot(df, 'Location', y_col, group, group_num=i, char=10)
    plt.ioff()
    plt.show()
