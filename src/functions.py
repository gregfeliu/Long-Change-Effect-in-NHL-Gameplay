from config import *
import mysql.connector
import seaborn as sns
import pandas as pd


######## SQL Table Creation Functions ########
def get_col_info(df):
    """
    Collects information about columns in a dataframe for use in "create table" statements. 
    It returns the maximum number of characters needed for VARCHAR and fills in nan values.
    -
    Input: 
    df: a pandas dataframe.
    -
    Output:
    col_names: a list of all of the column names for that dataframe.
    sql_col_types: a list, of equal length to the col_names list, that has all of the SQL equivalent datatypes.
    """
    # initializing the replacement dictionary and the column names
    replacement_dict = {"int64": "INT", "float64": "FLOAT", "bool":'BIT', "object":'VARCHAR'}
    col_names = list(df.columns)
    # replacing the pandas datatypes to SQL datatypes
    col_types = [x for x in df.dtypes]
    sql_col_types = [replacement_dict[str(x)] for x in col_types]
    # handling case where datatype is VARCHAR since it needs to know how many characters need to be stored
    for idx, x in enumerate(sql_col_types):
        if x == 'VARCHAR':
            if df[col_names[idx]].isnull().values.any() == True:
                df = df.fillna("")
            max_col_len = len(max(df[col_names[idx]], key=len))
            sql_col_types[idx] = x + "(" + str(max_col_len) + ")"
    return col_names, sql_col_types

def all_create_table_statements(df_names, df_files):
    """
    Creates "create table" statements for every dataframe. 
    They are stored in a list and copy and pasted into Google Cloud Platform in order to store the SQL table.
    -
    Input: 
    df_names: a list of names for the dataframes.
    df_diles: the file locations for all of the dataframes.
    -
    Output:
    create_table_statement_list: a list with full "create table" statements for each one of the tables.
    """
    create_table_statement_list = []
    for idx, df in enumerate(df_files):
        # initializing the values used with that specific table
        df_name = df_names[idx]
        print(f"Table name is {df_name}")
        df_dataframe = pd.read_csv(df)
        df_columns, df_dtypes = get_col_info(df_dataframe)
        # building the statement
        column_section = f"CREATE TABLE {df_name} ("
        for idx1, x in enumerate(df_columns):
            col_row = str(x) + " " + df_dtypes[idx1] + ", "
            column_section += col_row
        final_column_section = column_section[:-2] + ");"
        create_table_statement_list.append(final_column_section)
    return create_table_statement_list

######## SQL Query Functions ########
def run_query(sql_query):
    """
    Makes a connection to the Google Cloud Platform, and executes the query.
    -
    Input: 
    sql_query: a string with the sql query 
    -
    Output:
    variable: a list of lists containing the results of the query
    """
    # add try except for connection
    connection = mysql.connector.connect(**config)
    # main part of function
    cursor = connection.cursor()
    cursor.execute(sql_query)
    variable = cursor.fetchall()
    return variable

def get_total_period_sum(event_type):
    """
    Gets the sum of an event type by period from the entire dataset. 
    The "events" are hits, takeaways, goals, etc.
    -
    Input:
    event_type: a string that is in title case and is one of the possible event types
    -
    Output:
    variable_by_period_query_result: a list of lists containing the results of the query
    """
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

def get_raw_data(event_type):
    """
    Makes a query that sums the event for a period and game_id. 
    This allows us to get median values and view the distribution for an event type for a given game.
    Returns a dataframe for that event type
    -
    Input:
    event_type: a string that is in title case and is one of the possible event types
    -
    Output:
    df: a pandas dataframe
    """
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
    """
    Gets the shift length for each player and shift from regulation time shifts. 
    The data is organized by position and game_id
    -
    Input:
    position: a string that is in title case 
    -
    Output:
    variable: a list of lists containing the results of the query
    """
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

######## Analyzing Functions ########
def make_barplot_of_variable_by_period(query_result):
    """
    Makes a barplot of the query that has a sum of the event grouped by period
    -
    Input:
    query_result: The result of a query, a list of lists
    -
    Output:
    barplot: a seaborn barplot
    """
    barplot = sns.barplot(x = [i[0] for i in query_result],
                          y = [i[1] for i in query_result], 
                          ci=None)
    return barplot

def get_category_and_period_avg(category):
    """
    Finds a dataframe for a specific stat category and gets the average of that category by period
    -
    Input:
    category: a string that is in title case and is one stats I have collected in a dataframe already
    -
    Output:
    category_period_avg: a pandas series that averaged the category values by period
    """
    lower_category = category.lower()
    file_location = f"../data/{lower_category}s.csv"
    category_df = pd.read_csv(file_location, index_col=0)
    category_period_avg = category_df.groupby(["period"])[f'{category}'].mean()
    return category_period_avg

def generate_three_proposals(category_avg_df):
    """
    Gets the sum of the category under 3 diff proposals: no change, double long change, triple long change.
    The third period of each category is multiplied by the ratio between the third and first period for that stat category.
    This is done so that it mimics the change in game strategy, independent of the short/long change effect.
    -
    Input:
    category_avg_df: a pandas series that is the result of get_category_and_period_avg(category)
    -
    Output:
    all_proposals: a dictionary with the results of the current data and the three proposals.
    """
    # 
    ratio_3_1 = category_avg_df.iloc[2] / category_avg_df.iloc[0]
    sum_no_change = round(sum(category_avg_df.values), 2)
    sum_double_long = round(category_avg_df.iloc[1] + category_avg_df.iloc[0] + (category_avg_df.iloc[1] * ratio_3_1), 2)
    sum_triple_change = round((category_avg_df.iloc[1] * 2) + (category_avg_df.iloc[1] * ratio_3_1), 2)
    all_proposals = {"No_Change": sum_no_change, 
                     "Two_Long_Changes": sum_double_long,
                     "Three_Long_Changes": sum_triple_change}
    return all_proposals

def proposals_to_df(proposal_dict, type_of_proposal):
    """
    Turns the proposal dictionary into a dataframe. 
    This is done to make combining the proposal values for each category into a single dataframe.
    -
    Input:
    proposal_dict: a dictionary of the three proposal values. Result of generate_three_proposals(category_avg_df)
    type_of_proposal: a title case string of the category of interest.
    -
    Output:
    proposal_df: a dataframe of the three proposals for a specific category
    """
    proposal_df = pd.DataFrame.from_dict(proposal_dict, orient='index', columns=[type_of_proposal])
    return proposal_df