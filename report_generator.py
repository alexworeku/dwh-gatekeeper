import pandas as pd
from tabulate import tabulate
from markdown import markdown
import tempfile
import webbrowser
import os
import logging

SEVERITY_MAPPING = {
    "data_type_mismatch": "CRITICAL",
    "removed_columns": "CRITICAL",
    "new_columns": "CRITICAL",
    "max_length_mismatch": "MEDIUM",
    "ordinal_position_drift": "LOW"
    }



def open_report_via_browser(markdown_report):
    html_report = markdown(markdown_report,extensions=['tables'])
    
    with tempfile.NamedTemporaryFile(mode="w",suffix=".html",encoding="utf-8",delete=False) as file:
        file.write(html_report)
        file_path = file.name
        
    report_path = "file://" + os.path.realpath(file_path)
    webbrowser.open_new_tab(report_path)


def generate_excel_report(report_json:dict):
    logging.info("Starting Excel report generation...")
    summary= []
    for k,v in report_json["validation_summary"].items():
        summary.append(
            {
                "Metric": k.replace("_"," ").title(),
                "Value":  v
            }
        )
    summary_df = pd.DataFrame(summary)
    
    logging.info("Processed %d summary metrics.", len(summary_df))
    
    master_issues = []
    for column_name,issues in report_json['val_details'].items():
        for issue in issues:
            issue_type, details = issue.popitem()
            master_issues.append(
            {
            "Severity": SEVERITY_MAPPING[issue_type],
            "Column Name": column_name,
            "Issue Type":issue_type.replace("_"," ").title(),
            "Expected Value(Target DDL)":details['expected'],
            "Actual Value(Source DDL)":details['actual'],
            })
    
    for column_name in report_json['col_diff']['new_columns']:
        master_issues.append(
            {
            "Severity": SEVERITY_MAPPING['new_columns'],
            "Column Name": column_name,
            "Issue Type":"New Column Found",
            "Expected Value(Target DDL)":'-',
            "Actual Value(Source DDL)": '-',
            })
    for column_name in report_json['col_diff']['removed_columns']:
        master_issues.append(
            {
            "Severity": SEVERITY_MAPPING['removed_columns'],
            "Column Name": column_name,
            "Issue Type":"Column Removed",
            "Expected Value(Target DDL)":'-',
            "Actual Value(Source DDL)": '-',
            })    
        
    master_issues_df = pd.DataFrame(master_issues)
    logging.info("Total issues compiled: %d", len(master_issues))
    
    critical_issues_df = master_issues_df[master_issues_df['Severity']=='CRITICAL']
    
    critical_count = len(critical_issues_df)
    if critical_count > 0:
        logging.warning("Found %d CRITICAL issues requiring immediate attention.", critical_count)
    else:
        logging.info("No CRITICAL issues found in the validation report.")
    
    low_to_medium_issues_df = master_issues_df[master_issues_df['Severity'].isin(['LOW',"MEDIUM"])]
    
    # report_date = report_json["validation_summary"]['execution_time']
    report_filename='data_quality_report.xlsx'
    try:
        with pd.ExcelWriter(report_filename,engine='xlsxwriter',datetime_format="%Y-%m-%dT%H:%M:%S") as writer:
            summary_df.to_excel(writer,sheet_name="Dashboard Summary",index=False)
            master_issues_df.to_excel(writer,sheet_name="Master Issues List",index=False)
            critical_issues_df.to_excel(writer,sheet_name="CRITICAL Issues",index=False)
            low_to_medium_issues_df.to_excel(writer, sheet_name="MEDIUM & LOW Issues",index=False)
            
            logging.info("Successfully generated Excel report: '%s'", report_filename)
    except Exception as ex:
        logging.error("Failed to write Excel file '%s'. Error: %s", report_filename, ex, exc_info=True)