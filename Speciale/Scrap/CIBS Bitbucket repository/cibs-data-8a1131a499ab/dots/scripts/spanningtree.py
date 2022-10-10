import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
from matplotlib import style
# figure(figsize=(10, 18))
style.use('ggplot')

"""
This python script plots a spanning tree / hamilton tree from a WoT session
"""

file = pd.read_csv('../hhb0if6e.csv')


# function for finding nearest guess
def find_nearest(array, value):
    array = np.asarray(array)

    # because argmin() always returns the first number in the case of multiple
    # minimum values, we are good with the code as is:
    idx = (np.abs(array - value)).argmin()

    return (idx, array[idx])


def simple_moving_average(guess_list, window_size):
    return sum(guess_list[-window_size:]) / window_size


def calculate_spanning_tree(df):
    spanning_tree = {}

    ids = df['id'].values

    # retrieve the history matrix of what people saw:
    hist = df['hist'].values

    # hist is now a numpy array of strings. Needs to be converted.
    # I use pd.eval()
    hist2d = [pd.eval(h) for h in hist]

    for id in ids:
        own_order = df[df['id'] == id].index.item()
        own_guess = df[df['id'] == id]['guess'].item()

        seen_ids = hist2d[own_order]

        if len(seen_ids) == 0:
            continue

        seen_guesses = [df[df['id'] == g]['guess'].item() for g in seen_ids]

        nearest = find_nearest(seen_guesses, own_guess)

        # set new order and idol vars
        followed_player_order = df[df['id'] == seen_ids[nearest[0]]].index.item()
        spanning_tree[own_order] = (followed_player_order, nearest[1])

    return spanning_tree


def spanning_tree_path(id, df, spanning_tree):
    own_order = df[df['id'] == id].index.item()

    path = []
    # add the current guess to the path of this guess
    path.append((own_order, df[df['id'] == id]['guess'].item()))

    followed_player = spanning_tree.get(own_order)

    while followed_player is not None:
        path.append(followed_player)
        followed_player = spanning_tree.get(followed_player[0])

    return path


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

    # add the preceeding nearest guesses until hitting time = 1
    while order > 1:
        guess = df[df['id'] == idol]['guess'].item()
        seen_ids = hist2d[order]
        # if order == 11:
        #     print(seen_ids)

        # make a list of guesses seen, and find the nearest
        seen_guesses = [df[df['id'] == g]['guess'].item() for g in seen_ids]

        nearest = find_nearest(seen_guesses, guess)

        # set new order and idol vars
        order = df[df['id'] == seen_ids[nearest[0]]].index.item()
        idol = seen_ids[nearest[0]]

        # save into hamiltonian path vector
        path.append((order, nearest[1]))
        # printx(order)

    return path


def plotting_tree(df, views, method):
    spanning_tree = calculate_spanning_tree(df)

    session = df['session'].unique().item()
    guesses = df['guess'].values
    true_number_of_dots = df['dots'].unique().item()
    xsize = 4
    ysize = 0.1*len(guesses)
    print(xsize, ysize)
    plt.figure(figsize=(xsize, ysize))

    # retrieve and plot the hamiltonian path for person id:
    ids = df['id'].values
    ids = ids[-len(ids) + 1:]  # removing the first id (has empty history)
    for id in ids:
        # x, y = zip(*hamiltonian_path(id, df, spanning_tree))
        x, y = zip(*spanning_tree_path(id, df, spanning_tree))
        plt.plot(y, x, linewidth=5.0)

    # add the actual guesses to the plot as large black dots
    plt.plot(guesses, [i for i in range(len(guesses))], 'o', c='black',
             alpha=0.7)

    # add the moving average and the moving median to the plot. But first
    # filter out really bad guesses:
    filtered_guesses = [g for g in guesses if g < true_number_of_dots*100]
    ma = []
    me = []
    for g in range(1, len(filtered_guesses)+1):
        guess_list = filtered_guesses[:g]
        ma.append(simple_moving_average(guess_list, g))
        me.append(np.median(guess_list))

    plt.plot(ma, [i for i in range(len(filtered_guesses))], c='blue', alpha=0.3)
    plt.plot(me, [i for i in range(len(filtered_guesses))], c='green', alpha=0.3)

    # plotting paraphernalia
    # plt.xlim(0, np.amax(guesses) + 100)
    plt.xlim(true_number_of_dots/10, true_number_of_dots*2)
    plt.xlabel('guess')
    plt.ylabel('order')
    plt.title(str(true_number_of_dots)+'dots_'+str(views)+str(method)+'_'+str(session))
    plt.tight_layout()
    plt.savefig('../analysis/'+str(true_number_of_dots)+'dots_'+str(views)+str(method)+'_'+str(session)+'.png', dpi=300)
    plt.show()


# main code
df = pd.DataFrame(file)
# print(df.tail())
# df['guess'].plot()
# plt.show()
with pd.option_context('display.max_rows', None,'display.max_columns', None):
    print(df)
# print(df['views'].unique().item(), df['method'].unique().item())
plotting_tree(df, df['views'].unique().item(), df['method'].unique().item())
# print(df.tail())
