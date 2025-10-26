import requests
import pandas as pd
from io import StringIO
import os


def get_seasons(url) -> list | None:
    """
    Gets all the tables from the provided url
    Uses the requests module to mask the script preventing a 403 error from Wikipedia.
    :param url: The url to grab the tables from.
    :return: A list of the tables from the provided url.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        tables = pd.read_html(StringIO(response.text))
        # Process tables as needed
        print(f"Successfully retrieved {len(tables)} tables.")
        return tables
    except requests.exceptions.HTTPError as err:
        print(f"HTTP Error: {err}")
    except Exception as e:
        print(f"An error occurred: {e}")



def real_seasons(all_tables) -> list:
    """
    Returns a list of dataframes that include real seasons
    It separates these columns beside on the overall number column.
    :param all_tables: A list of dataframes
    :return: A list of dataframes that include real seasons
    """
    real_seasons_list = []
    for i in range(0, len(all_tables)):
        if 'No. overall' in all_tables[i].columns:
            real_seasons_list.append(all_tables[i])
    return real_seasons_list


def add_season_nums(real_seasons_list):
    """
    Add the season numbers to a dataframe
    :param real_seasons_list: A list of dataframes to iterate through
    """
    for i in range(0, len(f_seasons)):
        f_seasons[i]['Season'] = i + 1


def create_season_df(real_seasons_list, drop_columns) -> pd.DataFrame:
    """
    Creates a dataframe from the list of real seasons and drops the included columns.
    Removes rows that are entirely null (excluding the season column).
    :param real_seasons_list: A list of real season dataframes
    :param drop_columns: A list of columns to drop
    :return: A pandas dataframe containing only the real seasons and the necessary columns
    """
    seasons_combined = pd.concat(real_seasons_list, ignore_index=True)
    seasons_combined.drop(columns=drop_columns, inplace=True)
    seasons_combined.dropna(thresh=5, inplace=True, ignore_index=True)
    return seasons_combined


def add_date_column(f_episodes) -> pd.DataFrame:
    """
    Creates the Release Date column.
    Splits the original release date column into the release month, day, and year columns.
    Cleans the year column.
    Combines the year, month and day columns and creates a new column date column called Release Date.
    Drops the unnecessary columns original release date, year, month, and day.
    :param f_episodes: The original episode dataframe
    :return: Returns a new episode dataframe with the date column
    """
    # Spit the Original release data column in tho month, day, and year values.
    # Remove original comma from day values
    f_episodes[['Release_Month', 'Release_Day', 'Release_Year']] = \
        f_episodes['Original release date'].str.split('\xa0', expand=True)
    f_episodes['Release_Day'] = f_episodes['Release_Day'].str.replace(',', '')

    # Get the first four characters in the Release_Year column.
    f_episodes['Release_Year'] = f_episodes['Release_Year'].str[:4]

    try:
        # Create a date type column and drop unnecessary columns
        f_episodes['Date_String'] = f_episodes['Release_Year'].astype(str) + '-' + \
                                    f_episodes['Release_Month'] + '-' + \
                                    f_episodes['Release_Day'].astype(str)

        f_episodes['Release_Date'] = pd.to_datetime(f_episodes['Date_String'], format='%Y-%B-%d')

        drop_columns = ['Date_String', 'Release_Year', 'Release_Month', 'Release_Day', 'Original release date']
        f_episodes.drop(columns=drop_columns, inplace=True)
    except:
        print("Failed to convert release_date to datetime format.")

    return f_episodes

def clean_episodes(f_episodes) -> pd.DataFrame:
    """
    Cleans the U.S. viewers, Production code, Overall number, Number in season, Title, and Written by columns
    Spits the Written by column into separate writers and keeps the first two columns.
        (Columns 3 and 4 have more than 65% null values.)
    Drops the Written by column.
    :param f_episodes: The DataFrame containing all episodes
    :return: A cleaned DataFrame
    """
    # Remove info brackets from the viewers column and change type to float.
    f_episodes['U.S. viewers (millions)'] = f_episodes['U.S. viewers (millions)'].str.split('[', expand=True)[0]
    f_episodes['U.S. viewers (millions)'] = f_episodes['U.S. viewers (millions)'].astype(float)

    # Change Prod. code to int
    f_episodes['Prod. code'] = f_episodes['Prod. code'].astype(int)

    # Change No. overall to int
    f_episodes['No. overall'] = f_episodes['No. overall'].astype(int)

    # Change No. in season to int
    f_episodes['No. in season'] = f_episodes['No. in season'].astype(int)

    # Remove info brackets from the title column
    f_episodes['Title'] = f_episodes['Title'].str.replace(r'\[.*?\]', '', regex=True)

    # Splits the Written by column and only keeps the first two rows. (Columns 3 & 4 include over 75% nulls)
    # Keeps only Writers
    f_episodes['Written by'] = f_episodes['Written by'].str.replace('Story by\u200a: ', '')
    f_episodes['Written by'] = f_episodes['Written by'].str.split('Teleplay by\u200a:', expand=True)[0]
    f_episodes[['Writer_1', 'Writer_2']] = f_episodes['Written by'].str.split('& ', expand=True).iloc[:, :2]
    f_episodes['Writer_1'] = f_episodes['Writer_1'].str.strip()
    f_episodes['Writer_2'] = f_episodes['Writer_2'].str.strip()
    f_episodes.drop(columns=['Written by'], inplace=True)

    return f_episodes

def export(dataframe,file, file_path):
    """
    Exports the dataframe to a csv file.
    :param dataframe: The dataframe to export.
    :param file: The file name.
    :param file_path: The file path.
    """
    full_file_path = os.path.join(file_path, file)
    dataframe.to_csv(full_file_path, index=False)

def split_row(row_index, dataframe) -> pd.DataFrame:
    """
    Splits the data in the Overall number, Number in season, and Production code columns.
    Creates a new dataframe with the new rows and removes the indexed row.
    :param row_index: The row index needed to be split and removed.
    :param dataframe: The dataframe that contains the identified row.
    :return: A new dataframe with the new rows and removed indexed row.
    """
    # Get the combined values from the row
    overall_1 = dataframe.iloc[row_index]['No. overall'].astype(str)[0:2]
    overall_2 = dataframe.iloc[row_index]['No. overall'].astype(str)[2:4]
    season_num_1 = dataframe.iloc[row_index]['No. in season'].astype(str)[0:2]
    season_num_2 = dataframe.iloc[row_index]['No. in season'].astype(str)[2:4]
    prod_code_1 = dataframe.iloc[row_index]['Prod. code'].astype(str)[0:6]
    prod_code_2 = dataframe.iloc[row_index]['Prod. code'].astype(str)[6:12]

    # Create row dictionaries
    new_rows = [{'No. overall': int(overall_1), 'No. in season': int(season_num_1),
                 'Title': dataframe.iloc[row_index]['Title'],
                 'Directed by': dataframe.iloc[row_index]['Directed by'],
                 'Prod. code': int(prod_code_1),
                 'U.S. viewers (millions)': dataframe.iloc[row_index]['U.S. viewers (millions)'],
                 'Season': dataframe.iloc[row_index]['Season'],
                 'Release_Date': dataframe.iloc[row_index]['Release_Date'],
                 'Writer_1': dataframe.iloc[row_index]['Writer_1'],
                 'Writer_2': dataframe.iloc[row_index]['Writer_2'],},
                {'No. overall': int(overall_2), 'No. in season': int(season_num_2),
                 'Title': dataframe.iloc[row_index]['Title'], 'Directed by': dataframe.iloc[row_index]['Directed by'],
                 'Prod. code': int(prod_code_2),
                 'U.S. viewers (millions)': dataframe.iloc[row_index]['U.S. viewers (millions)'],
                 'Season': dataframe.iloc[row_index]['Season'],
                 'Release_Date': dataframe.iloc[row_index]['Release_Date'],
                 'Writer_1': dataframe.iloc[row_index]['Writer_1'],
                 'Writer_2': dataframe.iloc[row_index]['Writer_2'],}]

    # Create a new dataframe with the row values
    df = pd.DataFrame(new_rows)

    # Combine the two dataframes
    dataframe = pd.concat([dataframe, df], ignore_index=True)

    # Removes the split row from the dataframe
    dataframe = pd.concat([dataframe.iloc[:row_index], dataframe.iloc[row_index + 1 :]], ignore_index=True)

    # Sorts the dataframe by the overall number
    dataframe.sort_values(by=['No. overall'], inplace=True, ignore_index=True)

    return dataframe


if __name__ == '__main__':
    # Get all tables from the friends episode Wikipedia page
    friends_url = "https://en.wikipedia.org/wiki/List_of_Friends_episodes"
    f_tables = get_seasons(friends_url)

    # Separate real seasons from extra tables
    f_seasons = real_seasons(f_tables)

    # Add season nums to tables
    add_season_nums(f_seasons)

    # Creates a combined Dataframe with all seasons and legit episodes
    f_episode = create_season_df(f_seasons,drop_columns = ['Rating (18–49)', 'Rating/share (18–49)'])

    # Creates the date column
    f_episode = add_date_column(f_episode)

    # Cleans multiple dataframe columns
    f_episode_clean = clean_episodes(f_episode)

    # Splits the 16th and 17th episodes into their individual rows
    friends_df = split_row(15, f_episode_clean)

    # Assigns the output direcotry and the file name
    output_directory = "C:/Users/Matth/Python_projects/PyCharm_Projects/Friends"
    file_name = "friends_episodes.csv"

    # Exports the dataframe to a CSV file
    export(friends_df, file_name, output_directory)











