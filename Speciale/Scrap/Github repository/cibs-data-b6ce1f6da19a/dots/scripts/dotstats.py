import numpy as np
import pandas as pd
from scipy.stats import ttest_ind
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
from matplotlib import style
# import seaborn as sns
style.use('ggplot')

"""
This python script analyzes the data from the WoT
experiments on Amazon Mechanical Turk.
"""

data_file = pd.read_csv('../../../../Experiments/data/dots/all_data_dots.csv')


def hist(df, treat, views):
    bin_values = np.arange(start=0, stop=10000, step=100)
    df['guess'].hist(bins=bin_values, figsize=[14, 6])
    plt.title(str(treat)+str(views))


def basic_stats(df1):
    sessions = df1['session'].unique()

    for session in sessions:
        df = df1[df1['session'] == session]
        print('\n\nSession:', df['session'].unique())
        print('dots:', df['dots'].unique())
        print('Method', df['method'].unique())
        print('Views:', df['views'].unique())
        print('Number of guesses (unfiltered):', len(df['guess'].values))
        # df = df[df['confirm'] == 1]
        print('Number of guesses (confirmed):', len(df['guess'].values))
        if df['method'].unique().item() == 'history':
            # remove guesses more than an order of magnitude away from true number
            df = df[(df['guess'] > df['dots'].unique().item()/10) & (df['guess'] < df['dots'].unique().item()*100)]
        print('Number of guesses (confirmed & filtered):', len(df['guess'].values))
        print('Mean = ', df['guess'].mean(), (df['guess'].mean() - df['dots'].unique().item())/df['dots'].unique().item())
        print('Median = ', df['guess'].median(), (df['guess'].median() - df['dots'].unique().item())/df['dots'].unique().item())
        print('Mode = ', df['guess'].mode())
        print('Variance = ', df['guess'].var(ddof=0))
        print('Variance = ', df['guess'].var(ddof=1))
        print('Std (div N) = ', df['guess'].std(ddof=0), df['guess'].std(ddof=0)/df['dots'].unique().item())
        print('Std (div N-1) = ', df['guess'].std(ddof=1))
        print('Mean (average) absolute deviation = ', df['guess'].mad(), df['guess'].mad()/df['dots'].unique().item())
        print('MSE = ', np.sqrt(((df['guess'].values - 1233) ** 2).mean()))
        print('Skewness = ', df['guess'].skew())
        print('Kurtosis = ', df['guess'].kurt())
        print('25th percentile = ', df['guess'].quantile(0.25))
        print('50th percentile = ', df['guess'].quantile(0.5))
        print('75th percentile = ', df['guess'].quantile(0.75))
        print('10th percentile = ', df['guess'].quantile(0.1))
        print('90th percentile = ', df['guess'].quantile(0.9))
        # print(df['guess'].describe())
        print('Number of bonuses: ', df['bonus'].sum(), df['bonus'].sum()/len(df['guess'].values))
        print('payoff:', df['pay'].sum(), df['pay'].sum()/len(df['guess'].values))


def basic_stats_all(df_all):
    for image, true_number in [('dots1', 55), ('dots2', 148), ('dots3', 403),
                               ('dots4', 1097)]:
        for views in [0, 1, 3, 9]:
            for selection_method in ['history', 'min', 'max']:
                if views > 0 or selection_method == 'history':
                    df = df_all[(df_all['dots'] == true_number) &
                                (df_all['views'] == views) &
                                (df_all['method'] == selection_method)]
                    basic_stats(df)


def plot_stats(df_all, dots):
    fig, (ax0, ax1, ax2) = plt.subplots(nrows=3, gridspec_kw = {'height_ratios':[4, 5, 4]}, sharex=True)
    # Set the font size via a keyword argument
    ax0.set_title(str(dots)+": Guess the Number of Dots", fontsize='large')
    ax0.set_yticklabels(['']*4) # removing axis numbers by making an empty list
    ax1.set_yticklabels(['']*2)
    ax2.set_yticklabels(['']*3)
    plt.xlabel('guess')

    control = []
    treatments = ['history', 'max', 'min']
    for treat in treatments:
        if treat == 'history':
            views = [0, 1, 3, 9]
        else:
            views = [1, 3, 9]
        for pos, view in enumerate(views):
            if view == 0:
                df = df_all[(df_all['views'] == view) & (df_all['method'] == treat)]
                cl = '#34495e'
                control = df['guess'].values
            elif view == 1:
                df = df_all[(df_all['views'] == view) & (df_all['method'] == treat)]
                cl = '#e74c3c'
                print(dots, treat, view, len(control), len(df['guess'].values))
                print(ttest_ind(control, df['guess'].values, equal_var=False))
            elif view == 3:
                df = df_all[(df_all['views'] == view) & (df_all['method'] == treat)]
                cl = '#2ecc71'
                print(dots, treat, view, len(control), len(df['guess'].values))
                print(ttest_ind(control, df['guess'].values, equal_var=False))
            else:
                df = df_all[(df_all['views'] == view) & (df_all['method'] == treat)]
                cl = '#3498db'
                print(dots, treat, view, len(control), len(df['guess'].values))
                print(ttest_ind(control, df['guess'].values, equal_var=False))

            # remove guesses more than an order of magnitude away from true number
            if treat == 'history':
                df = df[(df['guess'] > dots/10) & (df['guess'] < dots*100)]

            # calculate quartiles and deciles
            quan_min = df['guess'].quantile(0.25)
            quan_max = df['guess'].quantile(0.75)
            dec_min = df['guess'].quantile(0.1)
            dec_max = df['guess'].quantile(0.9)
            if treat == 'history':
                ax1.plot(df['guess'].median(), [pos],  'o', markersize=8, c=cl)
                ax1.plot(df['guess'].mean(), [pos],  'o', c=cl)
                ax1.hlines(y=pos, xmin=quan_min, xmax=quan_max, linewidth=3, color=cl)
                ax1.hlines(y=pos, xmin=dec_min, xmax=dec_max, linewidth=1, color=cl)
                ax1.axvline(x=dots, linewidth=.2, color='black')
                ax1.set_yticks([-0.5,0,1,2,3,3.5])
                ax1.tick_params(axis="y", length=0) # removing the small ticks
                ax1r = ax1.twinx()
                ax1r.set_ylabel('history', fontsize='large')
                plt.yticks([])
            elif treat == 'max':
                ax0.plot(df['guess'].median(), [pos],  'o', markersize=8, c=cl)
                ax0.plot(df['guess'].mean(), [pos],  'o', c=cl)
                ax0.hlines(y=pos, xmin=quan_min, xmax=quan_max, linewidth=3, color=cl)
                ax0.hlines(y=pos, xmin=dec_min, xmax=dec_max, linewidth=1, color=cl)
                ax0.axvline(x=dots, linewidth=.2, color='black')
                ax0.set_yticks([-0.5,0,1,2,2.5])
                # ax1.axis('off')
                ax0.tick_params(axis="y", length=0) # removing the small ticks
                ax0r = ax0.twinx()
                ax0r.set_ylabel('max', fontsize='large')
                plt.yticks([])
            else:
                ax2.plot(df['guess'].median(), [pos],  'o', markersize=8, c=cl)
                ax2.plot(df['guess'].mean(), [pos],  'o', c=cl)
                ax2.hlines(y=pos, xmin=quan_min, xmax=quan_max, linewidth=3, color=cl)
                ax2.hlines(y=pos, xmin=dec_min, xmax=dec_max, linewidth=1, color=cl)
                ax2.axvline(x=dots, linewidth=.2, color='black')
                ax2.set_yticks([-0.5,0,1,2,2.5])
                ax2.tick_params(axis="y", length=0) # removing the small ticks
                ax2r = ax2.twinx()
                ax2r.set_ylabel('min', fontsize='large')
                plt.yticks([])

    # plotting paraphernalia
    ax0.set_xlim([0, dots*3])
    # plt.xticks()
    # plt.xlabel('guess')

    # set ylabels vertically matching the lines
    ax1.set_ylabel('9 views\n\n3 views\n\n1 view\n\n0 views', rotation=0, labelpad=30, va='center') # ha='right')
    # ax1.set_ylabel('9 views\n\n3 views\n\n1 view\n\n0 views, N='+str(len(df)), rotation=0, labelpad=30, va='center')
    ax0.set_ylabel('9 views\n\n3 views\n\n1 view', rotation=0, labelpad=30, va='center')
    ax2.set_ylabel('9 views\n\n3 views\n\n1 view', rotation=0, labelpad=30, va='center')
    plt.tight_layout()
    # plt.savefig('../analysis/OXstats.png', dpi=300)
    plt.show()


# main code
df_all = pd.DataFrame(data_file)

# check for duplicates:
# print(len(df_all['mturker'].unique()), len(df_all))
# print(df_all[df_all['mturker'].duplicated(keep=False)])

for image, true_number in [('dots1', 55), ('dots2', 148), ('dots3', 403),
                           ('dots4', 1097)]:
    plot_stats(df_all[df_all['dots'] == true_number], true_number)

basic_stats_all(df_all)
# basic_stats(df_all)
# cdf(df_all)
# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
#     print(df)
