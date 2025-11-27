# 📊 Schema Validation Reporter (MySQL Focused)

A Python command-line utility designed to perform schema validation checks between two **MySQL** database tables (Source vs. Target) and generate a detailed, professional, multi-sheet Excel report for data engineering triage.

## ⚠️ Current Scope

**This version of the tool is designed exclusively for MySQL databases.** Support for other providers (PostgreSQL, SQL Server, Snowflake, etc.) is planned for future releases.

## ✨ Features

* **Comprehensive Validation:** Checks for schema drift, data type mismatches, max length discrepancies, and ordinal position changes.

* **Secure Connectivity:** Reads sensitive connection details (host, user, password, port, database name) exclusively from **Environment Variables** (or a `.env` file) for better security.

* **Professional Output:** Generates a single Excel workbook (`data_quality_report.xlsx`) with separate, actionable sheets.

* **Severity Triage:** Automatically categorizes issues into **CRITICAL**, **MEDIUM**, and **LOW** severity for focused remediation.

## 📦 Report Structure

The generated Excel file contains four essential worksheets:

1. **Dashboard Summary:** A high-level overview of the validation status, total columns, and issue counts. (For managers and quick checks.)

2. **Master Issues List:** A complete, unfiltered table of every single validation failure.

3. **CRITICAL Issues:** Filtered list of issues (e.g., Missing Columns, Data Type Mismatches) requiring immediate intervention to prevent ETL job failure or data loss.

4. **MEDIUM/LOW Issues:** Filtered list of less urgent issues (e.g., Max Length discrepancies, Positional Drift).

## 🛠️ Installation and Setup

### Prerequisites

* Python 3.8+

* The script requires the following libraries:

  * `pandas` (for data processing)
  * `sqlalchemy` (For connecting to the database engine and ORM features)
  * `argparse` (for handling command-line arguments)
  * `xlsxwriter` or `openpyxl` (Pandas Excel engine for report generation)
  * `mysql-connector-python` (The specific connector for MySQL)
  * `python-dotenv` (For securely loading credentials from a `.env` file)

```bash
# Install required Python packages for MySQL support
pip install pandas sqlalchemy mysql-connector-python python-dotenv xlsxwriter
```

## 🔒 Configuration & Security (Mandatory)

**This tool requires all database credentials to be supplied via environment variables.** The script uses `python-dotenv` to automatically load these variables from a local `.env` file if one exists.

### Required Environment Variables

You must set the following environment variables in your shell or use a `.env` file:

| Variable Name | Example Value | Description |
| :--- | :--- | :--- |
| `DB_HOST` | `mysql-cluster-01.internal` | **Required.** The hostname or IP address of the MySQL server. |
| `DB_PORT` | `3306` | **Required.** The port number for the MySQL connection. |
| `DB_NAME` | `user_data` | **Required.** The name of the MySQL database to connect to. |
| `DB_USER` | `replicator` | **Required.** The username for connecting to the database. |
| `DB_PASSWORD` | `mysql_pw_secret` | **Required.** The password for the specified database user. |

### Using a `.env` file (Recommended)

Create a file named `.env` in the root directory of your project:

```bash
# .env file content
DB_HOST="mysql-cluster-01.internal"
DB_PORT="3306"
DB_NAME="user_data"
DB_USER="replicator"
DB_PASSWORD="mysql_pw_secret"
```
## 🚀 Usage

The command line is used to specify the tables being compared and generated the report.

### Command Structure

```bash
python main.py \
    --source_table <SCHEMA.SOURCE_TABLE> \
    --target_table <SCHEMA.TARGET_TABLE>
```

## Example (Assuming credentials are set in the environment)
### To validate the user_profiles table:

```bash
python main.py \
    --source_table raw.user_profiles \
    --target_table aggregated.user_profiles
```
### Argument Reference (Command Line Only)

| Argument | Type | Required | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `--source_table` | `str` | Yes | N/A | The fully qualified name of the **SOURCE** table (e.g., `staging.customer_data`). |
| `--target_table` | `str` | Yes | N/A | The fully qualified name of the **TARGET** (expected) table (e.g., `production.customer_data`). |

## 🤝 Contribution & Future Plans

Contributions are welcome!

I plan to expand support to other major data platforms by implementing dialect-specific schema extraction logic. The next platforms targeted for integration are PostgreSQL and Snowflake.
