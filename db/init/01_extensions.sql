-- db/init/01_extensions.sql
-- Role: enable required Postgres extensions on database creation
-- Description: runs once when the data volume is first initialized.

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;