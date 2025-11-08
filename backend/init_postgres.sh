#!/bin/bash
# Script to initialize PostgreSQL for CivicLens

# Install PostgreSQL and PostGIS
sudo apt-get update
sudo apt-get install -y postgresql postgresql-contrib postgis

# Start PostgreSQL service
sudo service postgresql start

# Create database and user
sudo -u postgres psql << EOF
CREATE DATABASE civiclens;
CREATE USER postgres WITH PASSWORD 'postgres';
GRANT ALL PRIVILEGES ON DATABASE civiclens TO postgres;
\c civiclens
CREATE EXTENSION IF NOT EXISTS postgis;
EOF

echo "PostgreSQL and PostGIS setup complete!"