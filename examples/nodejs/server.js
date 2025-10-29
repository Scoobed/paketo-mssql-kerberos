const express = require('express');
const sql = require('mssql');

const app = express();
const port = process.env.PORT || 8080;

const config = {
    server: process.env.MSSQL_SERVER || 'localhost',
    database: process.env.MSSQL_DATABASE || 'master',
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

app.get('/', (req, res) => {
    res.send('MSSQL Kerberos Example App (Node.js)');
});

app.get('/test-connection', async (req, res) => {
    try {
        await sql.connect(config);
        const result = await sql.query('SELECT @@VERSION AS version');
        
        res.json({
            status: 'success',
            message: 'Connected successfully',
            sql_version: result.recordset[0].version
        });
    } catch (err) {
        res.status(500).json({
            status: 'error',
            message: err.message
        });
    }
});

app.listen(port, () => {
    console.log(`Server running on port ${port}`);
});
