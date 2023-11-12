import re
from pathlib import Path
import sys
import argparse
import pandas as pd

def load_dataset():
    script_dir = Path(__file__).parent
    data_path = script_dir / "data" / "eu_life_expectancy_raw.tsv"
    df = pd.read_csv(data_path, sep='\t')
    return df

def clean_data(df, country_arg = 'PT'):

    df.columns.values[0] = 'unit,sex,age,geo_time'

    df[['unit', 'sex', 'age', 'geo_time']] = df['unit,sex,age,geo_time'].str.split(',', expand=True)

    df.drop('unit,sex,age,geo_time', axis=1, inplace=True)

    df = pd.melt(df, id_vars=['unit', 'sex', 'age', 'geo_time'],
                 var_name='year', value_name='value')

    df.columns.values[3] = 'region'

    df['year'] = df['year'].astype(int)

    df['value'] = df['value'].apply(clean)

    df['value'] = df['value'].replace('', pd.NA)
    df = df.dropna(subset=['value'])

    df['region'] = df['region'].str.extract(r'([A-Z]{2})', expand=False)

    df['value'] = df['value'].astype(float)
    df = df[df['region'] == country_arg]

    return df

def save_data(dataframe):
    script_dir = Path(__file__).parent
    csv_path = script_dir / "data" / "pt_life_expectancy.csv"
    dataframe.to_csv(csv_path, index=False)

def clean (value):
    cleaned_value = re.sub(r'[^0-9.]', '', value)
    return cleaned_value

if __name__ == "__main__": # pragma: no cover
    parser = argparse.ArgumentParser(prog='cleaning.py', description="Script to clean a dataset")
    parser.add_argument('--country', type=str, nargs='*', help= 'Country to filter the dataframe')
    args = parser.parse_args()

    original_df = load_dataset()

    if len(sys.argv) > 1:
        df_cleaned = clean_data(original_df, args.country[0])
    else:
        df_cleaned = clean_data(original_df)

    save_data(df_cleaned)
