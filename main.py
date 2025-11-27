import validator
from dotenv import load_dotenv
import os
import report_generator
import logging
import argparse
def setup_arg_parser():
    arg_desc ="""
    Generates a multi-sheet Excel report detailing the schema validation differences 
    between the source and target data systems. Credentials are required to establish 
    a connection to the underlying data sources.
    """
    parser = argparse.ArgumentParser(prog='dwh-gatekeeper',description=arg_desc)
    parser.add_argument(
        '--host',
        type=str,
        required=True,
        help='The hostname or IP address of the database server (e.g., localhost, x.y.amazonaws.com).'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=5432,
        help='The port number for the database connection (e.g., 5432 for Postgres, 3306 for MySQL). Default is 5432.'
    )
    
    parser.add_argument(
        '--db',
        type=str,
        required=True,
        help='The name of the database to connect to (e.g., "analytics" or "warehouse").'
    )
    
    parser.add_argument(
        '--user',
        type=str,
        required=True,
        help='The username for connecting to the database.'
    )
    
    parser.add_argument(
        '--password',
        type=str,
        required=True,
        help='The password for the specified database user.'
    )

    # --- Table Arguments (What to Validate) ---
    parser.add_argument(
        '--source_table',
        type=str,
        required=True,
        help='The fully qualified name of the SOURCE table to read the current schema from (e.g., "staging.customer_data").'
    )
    
    parser.add_argument(
        '--target_table',
        type=str,
        required=True,
        help='The fully qualified name of the TARGET (expected) table to validate against (e.g., "production.customer_data").'
    )

    return parser
def main():
    # Init DB Connection and Parameters, Load Schema
    try:
        logging.basicConfig(level=logging.INFO)
        arg_parser=setup_arg_parser()
        args = arg_parser.parse_args()
        load_dotenv()
        # Replace with cmd args
        # DB_HOST = os.environ['DB_HOST']
        # DB_PORT = os.environ['DB_PORT']
        # DB_USER = os.environ["DB_USER"]
        # DB_PASSW = os.environ['DB_PASSW']
        # DB_NAME = os.environ['DB_NAME']
        # SOURCE_TABLE = ""
        # TARGET_TABLE = ""

        val_result= validator.validate(args.source_table,args.target_table,args.user,args.password,args.host,args.port,args.db)
        print(args)
        report_generator.generate_excel_report(val_result)
        
    except Exception as e:
        print (f"Error: {e}")

if __name__ == "__main__":
    main()