import numpy as np
import pandas as pd

datafiles = [
    '../../../../Experiments/data/dots/all_apps_wide_2018-08-14.csv',
    '../../../../Experiments/data/dots/all_apps_wide_2018-08-28.csv',
]


def make_dataframe(file):
    df = pd.DataFrame(file)

    # take only the relevant columns in data sheet
    df = df[[
            'session.code', 'session.config.selection_method',
            'participant.mturk_worker_id', 'session.config.true_number_of_dots',
            'session.config.views', 'participant.id_in_session',
            'dots.1.player.decision_order', 'dots.1.player.confirm',
            'dots.1.player.decision_history', 'dots.1.player.guess',
            'dots.1.player.sec_spent', 'dots.1.player.payoff', 'participant.payoff'
            ]]

    # rename columns
    df.columns = [
        'session', 'method', 'mturker', 'dots',
        'views', 'id', 'order', 'confirm', 'hist',
        'guess', 'time', 'bonus', 'pay'
    ]

    # drop all rows with nan's, sort and index
    df = df.dropna()

    # save a new csv-file for each session
    sessions = df.session.unique()
    for session in sessions:
        df_s = df[df['session'] == session]

        # now we sort the df with "order", and then reset the index and
        # drop the order column, because the index now is our new time line.
        df_s = df_s.sort_values('order')
        df_s = df_s.reset_index(drop=True)
        df_s = df_s.drop('order', 1)
        df_s.to_csv('../../../../Experiments/data/dots/' + str(session) + '.csv')
    return sessions, df


sessions = []
df_all = pd.DataFrame()
for datafile in datafiles:
    s, df = make_dataframe(pd.read_csv(datafile))
    sessions.append(s)
    df_all = df_all.append(df)

# sort properly and save
df_all = df_all.sort_values(['method', 'views', 'session', 'order'])
np.savetxt("../../../../Experiments/data/dots/sessions.csv", sessions, fmt='%s',
           delimiter="")
df_all.to_csv('../../../../Experiments/data/dots/all_data_dots.csv')
