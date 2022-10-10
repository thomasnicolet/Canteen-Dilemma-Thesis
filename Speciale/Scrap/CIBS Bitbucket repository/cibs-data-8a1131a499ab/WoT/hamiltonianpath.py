import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
from matplotlib import style
figure(figsize=(10, 18))
style.use('ggplot')

"""
This python script analyzes the data from the WoT
experiments on Amazon Mechanical Turk.
"""

# load data file from directory
# data_file = pd.read_csv('../data/ox_2018-06-20.csv')
# data_file = pd.read_csv('../data/all_apps_wide_2018-06-19.csv')
# data_file = pd.read_csv('../data/all_apps_wide_2018-06-20.csv')
# data_file = pd.read_csv('../data/all_apps_wide_2018-07-02.csv')
# data_file = pd.read_csv('../data/all_apps_wide_2018-07-03.csv')
# data_file = pd.read_csv('../data/all_apps_wide_2018-07-04.csv')
# data_file = pd.read_csv('../data/all_apps_wide_2018-07-05.csv')
data_file = pd.read_csv('../../../Experiments/data/WoT/all_apps_wide_2018-07-05_2.csv')


# function for making the propper dataframe
def make_dataframe(datafile):
    df = pd.DataFrame(datafile)

    # take only the relevant columns in data sheet
    df = df[[
            'session.code', 'participant.mturk_worker_id',
            'ox.1.subsession.views', 'participant.id_in_session',
            'ox.1.player.decision_order',
            'ox.1.player.decision_history', 'ox.1.player.estimate_kg',
            'ox.1.player.sec_spent', 'ox.1.player.payoff', 'participant.payoff'
            ]]

    # rename columns
    df.columns = [
                  'session', 'mturker',
                  'views', 'id', 'order', 'hist',
                  'guess', 'time', 'bonus', 'pay'
                 ]

    # look at one session:
    # df = df[df['session'] == 'p6hbxcct']

    # in all_apps_wide_2018-06-20.csv
    # df = df[df['session'] == '656wmc92']  # ox3hist
    # df = df[df['session'] == '654w33sp']  # ox3max
    # df = df[df['session'] == 'lg30cqht']  # ox3min

    # in all_apps_wide_2018-07-03.csv
    # df = df[df['session'] == 'uhu19909']  # ox9hist
    # df = df[df['session'] == '96v9vsvo']  # ox9min
    # df = df[df['session'] == 'emdqn9k4'] # ox9max

    # in all_apps_wide_2018-07-04.csv
    # df = df[df['session'] == 'ka00la5x']  # ox0
    # df = df[df['session'] == 'kygak6r7']  # ox1hist

    # in all_apps_wide_2018-07-05_2.csv
    df = df[df['session'] == 'i0x2cimn']  # ox9hist

    # drop all rows with nan's, sort and index
    df = df.dropna()
    df = df.sort_values('order')
    df.set_index('order', inplace=True)

    return df


# function for finding nearest guess
def find_nearest(array, value):
    array = np.asarray(array)
    diffs = np.abs(array - value)
    print(diffs, numpy.where(diffs == diffs.min()))
    idx = (np.abs(array - value)).argmin()
    return (idx, array[idx])


def simple_moving_average(guess_list, window_size):
    return sum(guess_list[-window_size:]) / window_size


# function for calculating the whole hamiltonian tree
def hamiltonian_path(id, df):
    order = df[df['id'] == id].index.item()
    idol = id

    # retrieve the history matrix of what people saw:
    hist = df['hist'].values

    # hist is now a numpy array of strings. Needs to be converted.
    # I use pd.eval()
    hist2d = [pd.eval(h) for h in hist]

    path = []

    # add the current guess to the path of this guess
    path.append((order, df[df['id'] == id]['guess'].item()))

    # add the preceeding nearest guesses until hitting order = 1
    while order > 1:
        guess = df[df['id'] == idol]['guess'].item()
        seen_ids = hist2d[order - 1]

        # make a list of guesses seen, and find the nearest
        seen_guesses = [df[df['id'] == g]['guess'].item() for g in seen_ids]
        nearest = find_nearest(seen_guesses, guess)

        # set new order and idol vars
        order = df[df['id'] == seen_ids[nearest[0]]].index.item()
        idol = seen_ids[nearest[0]]

        # save into hamiltonian path vector
        path.append((order, nearest[1]))

    return path


def plotting_stuff(df):
    # retrieve and plot the hamiltonian path for person id:
    ids = df['id'].values
    ids = ids[-len(ids) + 1:]  # removing the first id (has empty history)
    for id in ids:
        x, y = zip(*hamiltonian_path(id, df))
        plt.plot(y, x, linewidth=5.0)

    # add the actual guesses to the plot as large black dots
    guesses = df['guess'].values
    plt.plot(guesses, [i for i in range(1, 1 + len(guesses))], 'o', c='black',
             alpha=0.7)

    # add the moving average to the plot
    ma = []
    for g in range(1, len(guesses)+1):
        guess_list = guesses[:g]
        ma.append(simple_moving_average(guess_list, g))
    plt.plot(ma, [i for i in range(1, 1 + len(guesses))], c='black', alpha=0.3)

    # plotting paraphernalia
    plt.xlim(0, 4000)
    plt.xlabel('guess')
    plt.ylabel('order')
    plt.show()


# main code
df = make_dataframe(data_file)
# print(df.tail())
# df['guess'].plot(linestyle='--')
# plt.show()
# with pd.option_context('display.max_rows', None,'display.max_columns', None):
#     print(df)
print('Session:', df['session'].unique().item(),
      'views:', df['views'].unique().item())
print('Number of guesses:', len(df['guess'].values))
print('Mean =', df['guess'].mean())
print('Median = ', df['guess'].median())

plotting_stuff(df)

# print(df)
