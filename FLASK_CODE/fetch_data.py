import pandas as pd
from sqlalchemy import create_engine

def fetch_data_from_table(table_name):
    # SQL Server Database connection details
    username = 'INFA_REP'
    password = 'INFA_REP'
    hostname = 'localhost'
    port = '1433'
    database = 'INF_METADATA'

    # Build the SQL Server connection string
    sqlserver_connection_string = (
        f"mssql+pyodbc://{username}:{password}@{hostname}:{port}/{database}"
        f"?driver=ODBC+Driver+17+for+SQL+Server"
    )
    
    # Create engine
    engine = create_engine(sqlserver_connection_string)
    
    query = f"SELECT * FROM tgt.{table_name}"
    try:
        with engine.connect() as connection:
            df = pd.read_sql(query, con=connection)
            pd.options.display.float_format = '{:.0f}'.format
            df = df.applymap(lambda x: '{:.0f}'.format(x) if isinstance(x, (int, float)) else x)
        return df
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None
