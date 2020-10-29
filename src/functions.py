from config import *
import mysql.connector
import seaborn as sns
import pandas as pd



def run_query(sql_query):
    # add try except for connection
    connection = mysql.connector.connect(**config)
    # main part of function
    cursor = connection.cursor()
    cursor.execute(sql_query)
    variable = cursor.fetchall()
    return variable

def get_total_period_sum(event_type):
    assert type(event_type) == str
    variable_by_period = f"""
            SELECT period, COUNT(event)
            FROM game_plays
            WHERE event = '{event_type}' AND 
            period < 4
            GROUP BY period
"""
    variable_by_period_query_result = run_query(variable_by_period)
    return variable_by_period_query_result

def make_barplot_of_variable_by_period(query_result):
    barplot = sns.barplot(x = [i[0] for i in query_result],
                          y = [i[1] for i in query_result], 
                          ci=None)
    return barplot

def get_raw_data(event_type):
    assert type(event_type) == str
    variable_by_period = f"""
            SELECT period, COUNT(event), game_id
            FROM game_plays
            WHERE event = '{event_type}' AND 
            0 < period AND 
            period < 4
            GROUP BY period, game_id
"""
    variable_by_period_query_result = run_query(variable_by_period)
    df = pd.DataFrame(data = variable_by_period_query_result, columns = ['period', event_type, 'game_id'])
    return df

def get_shift_len_by_position(position):
    query = f"""
            SELECT period, shift_end - shift_start, player_info.primaryPosition, game_id
            FROM game_shifts
            INNER JOIN player_info
            ON game_shifts.player_id = player_info.player_id
            WHERE period < 4 
            AND period > 0
            AND player_info.primaryPosition = '{position}'
    """
    query_result = run_query(query)
    return query_result

def get_category_and_period_avg(category):
    lower_category = category.lower()
    file_location = f"../data/{lower_category}s.csv"
    category_df = pd.read_csv(file_location, index_col=0)
    category_period_avg = category_df.groupby(["period"])[f'{category}'].mean()
    return category_period_avg

def generate_three_proposals(category_avg_df):
    # get the sum of the category under 3 diff proposals: no change, double long change, triple long change
    sum_no_change = round(sum(category_avg_df.values), 2)
    sum_double_long = round(category_avg_df.iloc[0] + (category_avg_df.iloc[1] * 2), 2)
    sum_triple_change = round(category_avg_df.iloc[1] * 3, 2)
    all_proposals = {"No_Change": sum_no_change, 
                     "Two_Long_Changes": sum_double_long,
                     "Three_Long_Changes": sum_triple_change}
    return all_proposals

def proposals_to_df(proposal_dict, type_of_proposal):
    proposal_df = pd.DataFrame.from_dict(proposal_dict, orient='index', columns=[type_of_proposal])
    return proposal_df
