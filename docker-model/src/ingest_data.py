#!/usr/bin/env python
# coding: utf-8

import click
import pandas as pd
from tqdm.auto import tqdm
from sqlalchemy import create_engine  


# Read a sample of the data
prefix = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/'
dtype = {
    "VendorID": "Int64",
    "passenger_count": "Int64",
    "trip_distance": "float64",
    "RatecodeID": "Int64",
    "store_and_fwd_flag": "string",
    "PULocationID": "Int64",
    "DOLocationID": "Int64",
    "payment_type": "Int64",
    "fare_amount": "float64",
    "extra": "float64",
    "mta_tax": "float64",
    "tip_amount": "float64",
    "tolls_amount": "float64",
    "improvement_surcharge": "float64",
    "total_amount": "float64",
    "congestion_surcharge": "float64"
}

parse_dates = [
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime"
]


@click.command()
@click.option("--year", type=int, default=2021, show_default=True)
@click.option("--month", type=click.IntRange(1, 12), default=1, show_default=True)
@click.option("--target-table", default="yellow_taxi_data", show_default=True)
@click.option("--pg-user", default="root", show_default=True)
@click.option("--pg-pass", default="root")
@click.option("--pg-port", type=click.IntRange(1, 65535), default=5432, show_default=True)
@click.option("--pg-db", default="ny_taxi", show_default=True)
@click.option("--pg-host", default="localhost", show_default=True)
@click.option("--chunksize", type=click.IntRange(min=1), default=10000, show_default=True)
def main(year, month, target_table, pg_user, pg_pass, pg_host, pg_port, pg_db, chunksize):
    url = prefix + f'yellow_tripdata_{year}-{month:02d}.csv.gz'
    url_zones = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv'

    df_iter = pd.read_csv(
        url,
        dtype=dtype,
        parse_dates=parse_dates,
        iterator=True,
        chunksize=chunksize,
    )


    engine = create_engine(f'postgresql+psycopg://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}')

    df_zones = pd.read_csv(url_zones)
    df_zones.to_sql(name='zones', con=engine, if_exists='replace')

    first = True

    #Yellow taxi trips
    for df_chunk in tqdm(df_iter):
        if first:
            df_chunk.head(n=0).to_sql(
                name=target_table,
                con=engine,
                if_exists='replace'
            )
            first = False
            print('Table created')

        df_chunk.to_sql(
            name=target_table,
            con=engine, 
            if_exists='append'
        )


if __name__ == "__main__":
    main()