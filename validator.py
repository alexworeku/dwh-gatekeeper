import os
from dotenv import load_dotenv
import pandas as pd
import logging
from sqlalchemy import create_engine
from datetime import datetime


def load_schema_from_db(source_table,target_table):

    query = """
    select COLUMN_NAME, ORDINAL_POSITION, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH
    from INFORMATION_SCHEMA.COLUMNS
    where table_name
    """

    
    try:
        
        env_variables=load_required_db_vars()
        DB_HOST = env_variables['DB_HOST']
        DB_PORT = env_variables['DB_PORT']
        DB_USER = env_variables["DB_USER"]
        DB_PASSW = env_variables['DB_PASSW']
        DB_NAME = env_variables['DB_NAME']
       
        DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSW}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        engine = create_engine(DATABASE_URL)
        
        src_col_schema_df = pd.read_sql(f"{query} = '{source_table}';",engine)
        target_col_schema_df = pd.read_sql(f"{query} = '{target_table}';",engine)
        
        src_col_schema_df.sort_values(by="ORDINAL_POSITION")
        target_col_schema_df.sort_values(by="ORDINAL_POSITION")
        
        logging.info("Successfully loaded schemas from database. Source columns: %d, Target columns: %d.",
                     len(src_col_schema_df), len(target_col_schema_df))
        return src_col_schema_df,target_col_schema_df
    except Exception as e:
        logging.error("Failed to load schema from database for tables '%s' and '%s'. Error: %s", 
                      source_table, target_table, e, exc_info=True)
        raise
        
def find_columns_diff(src_schema_df, dest_schema_df):
    
    src_columns = set(src_schema_df['COLUMN_NAME'].values)
    dest_columns = set(dest_schema_df['COLUMN_NAME'].values)

    new_columns = src_columns - dest_columns
    removed_columns = dest_columns - src_columns

    # print(f" New Columns: { new_columns }")
    # print(f" Removed Columns: {removed_columns}")

    return (new_columns, removed_columns)        

def validate_col_details(actual_col_schema_df, expected_col_schema_df):
    validation_result={}
    issues_found_count=0
    for index,row in actual_col_schema_df.iterrows():
        expected_col_def = expected_col_schema_df[expected_col_schema_df['COLUMN_NAME']==row['COLUMN_NAME']].iloc[0]
        validation_result[row['COLUMN_NAME']]=[]

        # Data Type Validation
        if row['DATA_TYPE'] != expected_col_def['DATA_TYPE']:
            validation_result[row['COLUMN_NAME']].extend([{
                'data_type_mismatch': {
                    'expected': expected_col_def['DATA_TYPE'],
                    'actual': row['DATA_TYPE']
                }
            }])
            issues_found_count+=1
        # Ordinal position Validation 
        if row['ORDINAL_POSITION'] != expected_col_def['ORDINAL_POSITION'].item():
            validation_result[row['COLUMN_NAME']].extend([ {
                'ordinal_position_drift': {
                    'expected': expected_col_def['ORDINAL_POSITION'].item(),
                    'actual': row['ORDINAL_POSITION']
                }
            }])
            issues_found_count+=1
        # Length validation
        if row['CHARACTER_MAXIMUM_LENGTH']!= expected_col_def['CHARACTER_MAXIMUM_LENGTH'].item():
            validation_result[row['COLUMN_NAME']].extend([ {
                'max_length_mismatch': {
                    'expected': expected_col_def['ORDINAL_POSITION'].item(),
                    'actual': row['ORDINAL_POSITION']
                }
            }])
            issues_found_count+=1
    return issues_found_count,validation_result        
    
def validate(source_table, target_table):

    logging.info("Starting schema validation for Source: '%s' against Target: '%s'.", source_table, target_table)

    src_col_schema_df, target_col_schema_df=load_schema_from_db(source_table,target_table )
    
    # Find added & removed columns
    new_cols, removed_cols = find_columns_diff(src_col_schema_df,target_col_schema_df)

    # Validate columns (actual vs expected) across column data type, length, order
    # ~isin() filters out columns that are found both on the source and destination tables 
    cols_to_validate_df = src_col_schema_df[~src_col_schema_df['COLUMN_NAME'].isin(new_cols)]


    col_schema_issues_count, col_validation_result = validate_col_details(cols_to_validate_df, target_col_schema_df)

    status = "SUCCESS" if col_schema_issues_count==0 else "FAILED"
    
    new_cols_count = len(new_cols)
    removed_cols_count= len(removed_cols)
    total_issues_count = col_schema_issues_count+new_cols_count+removed_cols_count
    logging.info("Column reconciliation complete. New columns found: %d, Removed columns found: %d.", 
                 new_cols_count, removed_cols_count)
    logging.info("%d columns prepared for detailed attribute validation.", len(cols_to_validate_df))
    val_result = {
        "validation_summary":{
            "status":status,
            "execution_time": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "source_schema":source_table,
            "target_schema":target_table,
            "total_columns_compared":len(cols_to_validate_df),
            "total_schema_issues": total_issues_count,
            "new_columns_found": new_cols_count,
            "removed_columns_found": removed_cols_count
        },
        "col_diff":{
            "new_columns": list(new_cols),
            "removed_columns": list(removed_cols)    
        },
        "val_details":col_validation_result
        
    }
    if status == "SUCCESS":
        logging.info("Schema validation finished: SUCCESS. No schema drift detected.")
    else:
        logging.warning("Schema validation finished: FAILED. Total issues detected: %d.", total_issues_count)
    return val_result

def load_required_db_vars():

    # Load the .env file first (handles missing file by returning False)
    if not load_dotenv(".env"):
        logging.warning("'.env' file not found. Checking system environment variables.")

    try:
        DB_HOST = os.environ['DB_HOST']
        DB_PORT = os.environ['DB_PORT']
        DB_USER = os.environ["DB_USER"]
        DB_PASSW = os.environ['DB_PASSW']
        DB_NAME = os.environ['DB_NAME']
        
        return {
            'DB_HOST': DB_HOST,
            'DB_PORT': DB_PORT,
            'DB_USER': DB_USER,
            'DB_PASSW': DB_PASSW,
            'DB_NAME': DB_NAME,
        }

    except KeyError as e:
        missing_var = str(e).strip("'")
        logging.error(f"""\nCRITICAL ERROR: Required variable '{missing_var}' is missing. 
                      Please ensure your .env file or environment defines all 5 mandatory variables: DB_HOST, DB_PORT, DB_USER, DB_PASSW, DB_NAME
                      """)
        exit(1)