# Paketo MSSQL Kerberos Buildpack

A custom [Paketo Buildpack](https://paketo.io/) that installs the Microsoft ODBC Driver for SQL Server with Kerberos support during the build process.

## Features

- Installs Microsoft ODBC Driver 18 for SQL Server
- Includes Kerberos libraries for authenticated connections
- Vendors all dependencies for runtime availability
- Supports Ubuntu Bionic (18.04) and Jammy (22.04) stacks
- Automatic detection based on application dependencies

## Usage

### Automatic Detection

The buildpack automatically detects if your application needs the MSSQL ODBC driver by checking for:

- **Python**: `pyodbc` in `requirements.txt`
- **Node.js**: `mssql` or `tedious` in `package.json`
- **Go**: `github.com/denisenkom/go-mssqldb` in `go.mod`

### Manual Enablement

Force the buildpack to run by setting an environment variable:

```bash
pack build myapp --env BP_ENABLE_MSSQL_ODBC=true
```

### Using with Paketo Builders

#### Option 1: Add to Builder

Create a custom builder that includes this buildpack:

```toml
# builder.toml
[[buildpacks]]
  uri = "/path/to/paketo-mssql-kerberos"

[[buildpacks]]
  uri = "docker://gcr.io/paketo-buildpacks/python"

[[order]]
  [[order.group]]
    id = "scoobed/mssql-kerberos"
    version = "0.1.0"
  
  [[order.group]]
    id = "paketo-buildpacks/python"
    version = "*"
```

Build the custom builder:

```bash
pack builder create my-builder:latest --config builder.toml
```

#### Option 2: Use with pack build

```bash
pack build myapp \
  --buildpack /path/to/paketo-mssql-kerberos \
  --buildpack gcr.io/paketo-buildpacks/python \
  --builder paketobuildpacks/builder-jammy-base
```

## Runtime Configuration

### Environment Variables

The buildpack automatically sets these environment variables at runtime:

- `LD_LIBRARY_PATH`: Includes ODBC and Kerberos libraries
- `ODBCSYSINI`: Points to ODBC configuration directory
- `MSSQL_ODBC_DRIVER`: Set to "ODBC Driver 18 for SQL Server"
- `KRB5_CONFIG`: Kerberos configuration file location

### Kerberos Configuration

Create a `krb5.conf` file in your application or set `KRB5_CONFIG` to point to your configuration:

```ini
[libdefaults]
    default_realm = YOUR.DOMAIN.COM
    dns_lookup_realm = false
    dns_lookup_kdc = true
    ticket_lifetime = 24h
    renew_lifetime = 7d
    forwardable = true

[realms]
    YOUR.DOMAIN.COM = {
        kdc = kdc.your.domain.com
        admin_server = kdc.your.domain.com
    }

[domain_realm]
    .your.domain.com = YOUR.DOMAIN.COM
    your.domain.com = YOUR.DOMAIN.COM
```

### Connection String Examples

#### Python (pyodbc)

```python
import pyodbc

# With Kerberos (Windows Authentication)
conn_str = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=yourserver.database.windows.net;"
    "DATABASE=yourdatabase;"
    "Trusted_Connection=yes;"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
)

conn = pyodbc.connect(conn_str)
```

#### Node.js (mssql)

```javascript
const sql = require('mssql');

const config = {
    server: 'yourserver.database.windows.net',
    database: 'yourdatabase',
    options: {
        encrypt: true,
        trustServerCertificate: false,
        enableArithAbort: true,
        integratedSecurity: true
    },
    authentication: {
        type: 'default'
    }
};

sql.connect(config);
```

#### Go

```go
import (
    _ "github.com/denisenkom/go-mssqldb"
    "database/sql"
)

connString := "server=yourserver.database.windows.net;database=yourdatabase;authenticator=krb5;encrypt=true"
db, err := sql.Open("sqlserver", connString)
```

## Building the Buildpack

### Package the buildpack

```bash
pack buildpack package scoobed/mssql-kerberos:0.1.0 --config package.toml
```

## Licensing

Be aware of the [Microsoft ODBC Driver licensing terms](https://docs.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server).

## Troubleshooting

### Check installed driver

```bash
odbcinst -q -d
```

### Test connection

```bash
# Using sqlcmd from mssql-tools
sqlcmd -S yourserver.database.windows.net -d yourdatabase -E
```

### Verify Kerberos ticket

```bash
klist
```

### Debug ODBC

Set environment variable for verbose ODBC logging:

```bash
export ODBCINSTINI=/workspace/mssql-odbc/etc/odbcinst.ini
export ODBCSYSINI=/workspace/mssql-odbc/etc
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.
