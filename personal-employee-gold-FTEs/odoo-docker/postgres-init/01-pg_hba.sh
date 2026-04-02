#!/bin/bash
# PostgreSQL init script to configure pg_hba.conf for trust authentication

set -e

# Create pg_hba.conf with trust authentication
cat > /var/lib/postgresql/data/pg_hba.conf <<EOF
# PostgreSQL Client Authentication Configuration File
# TYPE  DATABASE        USER            ADDRESS                 METHOD

# Local connections
local   all             all                                     trust

# IPv4 local connections
host    all             all             127.0.0.1/32            trust
host    all             all             0.0.0.0/0               trust

# IPv6 local connections
host    all             all             ::1/128                 trust

# Allow all connections from Docker networks
host    all             all             172.16.0.0/12           trust
host    all             all             10.0.0.0/8              trust
host    all             all             192.168.0.0/16          trust
EOF

echo "pg_hba.conf configured for trust authentication"
