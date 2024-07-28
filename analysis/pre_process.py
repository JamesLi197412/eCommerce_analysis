import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


def order_data(df):
    """to adjust order date column in orders datasets"""
    df['order_delivered_customer_date'] = pd.to_datetime(df['order_delivered_customer_date'], errors='coerce')
    df['order_delivered_carrier_date'] = pd.to_datetime(df['order_delivered_carrier_date'], errors='coerce')
    df['order_approved_at'] = pd.to_datetime(df['order_approved_at'], errors='coerce')
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'], errors='coerce')
    df['order_estimated_delivery_date'] = pd.to_datetime(df['order_estimated_delivery_date'], errors='coerce')
    return df


def distribution_plt(dataframe, column_name, title, xlabel, ylabel, path):
    sns.distplot(dataframe[column_name], color='red')
    plt.title(title, fontsize=30)
    plt.xlabel(xlabel, fontsize=15)
    plt.ylabel(ylabel)
    plt.axvline(np.median(dataframe[column_name]), 0, linestyle='--', linewidth=1.5, color='b')
    plt.savefig(path)


def pie_chart(dataframe, col, target, color, title, path):
    plt.figure(figsize=(10, 5), dpi=100)
    target_df = dataframe.groupby([col])[target].agg(['count']).reset_index()

    plt.pie(target_df['count'], labels=target_df[col],
            autopct='%1.2f%%', startangle=45, colors=sns.color_palette(color),
            labeldistance=0.75, pctdistance=0.4)
    plt.title(title, fontsize=20)
    plt.axis('off')
    plt.legend()
    plt.savefig(path)


def hist_plot(df, xlabel, ylabel, title, path):
    plt.hist(df[xlabel], color='blue', edgecolor='black',
             bins=int(180 / 5))

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)

    plt.show()
    plt.savefig(path)
