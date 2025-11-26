import validator
from dotenv import load_dotenv
import json
def main():
    # Init DB Connection and Parameters, Load Schema
    try:

        load_dotenv()    
        # TODO: extract table names from the commandline instead of hardcoding them
        val_result= validator.validate('transactions_source','transactions_dw')
        print(json.dumps(val_result, indent=4)) 
    except Exception as e:
        print (f"Error: {e}")

if __name__ == "__main__":
    main()