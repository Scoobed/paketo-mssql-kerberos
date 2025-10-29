import os
import pyodbc
from flask import Flask, jsonify
from kerberos_renewal import start_auto_renewal

app = Flask(__name__)

# Start automatic Kerberos ticket renewal if principal is set
if os.getenv('KRB5_PRINCIPAL'):
    renewer = start_auto_renewal(interval=1800)  # Renew every 30 minutes
    app.logger.info("Kerberos auto-renewal enabled")

@app.route('/')
def index():
    return "MSSQL Kerberos Example App"

@app.route('/test-connection')
def test_connection():
    try:
        # Get connection details from environment
        server = os.getenv('MSSQL_SERVER', 'localhost')
        database = os.getenv('MSSQL_DATABASE', 'master')
        
        # Connection string with Kerberos authentication
        conn_str = (
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"Trusted_Connection=yes;"
            f"Encrypt=yes;"
        )
        
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute("SELECT @@VERSION")
        version = cursor.fetchone()[0]
        
        return jsonify({
            "status": "success",
            "message": "Connected successfully",
            "sql_version": version
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
