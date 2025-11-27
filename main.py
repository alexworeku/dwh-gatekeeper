import validator
from dotenv import load_dotenv
import os
import report_generator
import logging
def main():
    # Init DB Connection and Parameters, Load Schema
    try:
        logging.basicConfig(level=logging.INFO)
        load_dotenv()
        # Replace with cmd args
        DB_HOST = os.environ['DB_HOST']
        DB_PORT = os.environ['DB_PORT']
        DB_USER = os.environ["DB_USER"]
        DB_PASSW = os.environ['DB_PASSW']
        DB_NAME = os.environ['DB_NAME']
        
        val_result= validator.validate('transactions_source','transactions_dw',DB_USER,DB_PASSW,DB_HOST,DB_PORT,DB_NAME)
        
        report_generator.generate_excel_report(val_result)
        
    except Exception as e:
        print (f"Error: {e}")

if __name__ == "__main__":
    main()