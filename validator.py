import pandas as pd
import json
from sqlalchemy import create_engine
from collections import namedtuple
import os


def load_schema_from_db(db_user,db_passw, db_host,db_port, db_name,source_table,target_table):

    # Removed Columns: IS_NULLABLE, COLUMN_TYPE
    query = """
    select COLUMN_NAME, ORDINAL_POSITION, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH
    from INFORMATION_SCHEMA.COLUMNS
    where table_name
    """

    DATABASE_URL = f"mysql+mysqlconnector://{db_user}:{db_passw}@{db_host}:{db_port}/{db_name}"
    
    try:
        engine = create_engine(DATABASE_URL)
        print("Engine created...")
        
        src_col_schema_df = pd.read_sql(f"{query} = '{source_table}';",engine)
        target_col_schema_df = pd.read_sql(f"{query} = '{target_table}';",engine)
        
        src_col_schema_df.sort_values(by="ORDINAL_POSITION")
        target_col_schema_df.sort_values(by="ORDINAL_POSITION")
        
        print(f"Schema loaded.. \n{len(src_col_schema_df['COLUMN_NAME'][:5].values)} columns found\n{len(target_col_schema_df['COLUMN_NAME'].values)} columns expected")  

        return src_col_schema_df,target_col_schema_df
    except Exception as e:
        print (f"Error: {e}")
        
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
                'data_type': {
                    'expected': expected_col_def['DATA_TYPE'],
                    'actual': row['DATA_TYPE']
                }
            }])
            issues_found_count+=1
        # Ordinal position Validation 
        if row['ORDINAL_POSITION'] != expected_col_def['ORDINAL_POSITION'].item():
            validation_result[row['COLUMN_NAME']].extend([ {
                'ordinal_position': {
                    'expected': expected_col_def['ORDINAL_POSITION'].item(),
                    'actual': row['ORDINAL_POSITION']
                }
            }])
            issues_found_count+=1
        # Length validation
        if row['CHARACTER_MAXIMUM_LENGTH']!= expected_col_def['CHARACTER_MAXIMUM_LENGTH'].item():
            validation_result[row['COLUMN_NAME']].extend([ {
                'max_length': {
                    'expected': expected_col_def['ORDINAL_POSITION'].item(),
                    'actual': row['ORDINAL_POSITION']
                }
            }])
            issues_found_count+=1
    return issues_found_count,validation_result        
    
def validate(source_table, target_table):
    
    DB_HOST = os.environ['DB_HOST']
    DB_PORT = os.environ['DB_PORT']
    DB_USER = os.environ["DB_USER"]
    DB_PASSW = os.environ['DB_PASSW']
    DB_NAME = os.environ['DB_NAME']

    src_col_schema_df, target_col_schema_df=load_schema_from_db(DB_USER,DB_PASSW,DB_HOST,DB_PORT,DB_NAME, source_table,target_table )
    
    # Find added & removed columns
    new_cols, removed_cols = find_columns_diff(src_col_schema_df,target_col_schema_df)

    # Validate columns (actual vs expected) across column data type, length, order
    # ~isin() filters out columns that are found both on the source and destination tables 
    cols_to_validate_df = src_col_schema_df[~src_col_schema_df['COLUMN_NAME'].isin(new_cols)]


    issues_found_count, col_validation_result = validate_col_details(cols_to_validate_df, target_col_schema_df)

    status = issues_found_count=="SUCCESS" if issues_found_count==0 else "FAILED"
    val_result = {
        "validation_summary":{
            "status":status,
            "total_columns_compared":len(cols_to_validate_df),
            "total_schema_issues": issues_found_count,
            "new_columns_found": len(new_cols),
            "removed_columns_found": len(removed_cols)
            
        },
        "col_diff":{
                "new_columns": list(new_cols),
                "removed_columns": list(removed_cols)    
                },
        "val_details":col_validation_result
        
    }
    # TODO: include validation summary
    """
    "validation_summary": {
    "status": "FAILED", // Based on presence of CRITICAL errors
    "total_columns_compared": 22,
    "total_schema_issues": 35,
    "new_columns_found": 5,
    "removed_columns_found": 1
}
    """
    return val_result