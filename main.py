import validator
import report_generator
import logging
import argparse
def setup_arg_parser():
    arg_desc ="""
    Generates a multi-sheet Excel report detailing the schema validation differences 
    between the source and target data systems. 
    """
    parser = argparse.ArgumentParser(prog='dwh-gatekeeper',description=arg_desc)
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

        val_result= validator.validate(args.source_table,args.target_table)

        report_generator.generate_excel_report(val_result)
        
    except Exception as e:
        print (f"Error: {e}")

if __name__ == "__main__":
    main()