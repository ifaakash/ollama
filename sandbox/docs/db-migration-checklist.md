# Database Migration Checklist (PROD to DEV)

This guide outlines the process of safely taking a production database dump, sanitizing it, and importing it into the DEV environment.

## Phase 0: Pre-Migration Data Gathering (PROD)

Before starting the migration, connect to the **PROD DB** and gather baseline metrics to compare against the DEV database after the import.

**1. Log in to the PROD database:**
```bash
mariadb -h prod-<DB_NAME>-db.us-east-2.rds.amazonaws.com -P 3306 -u admin -p mydb
```

**2. Gather Table and Trigger Counts:**
```sql
-- Get total table count
SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'mydb';

-- Get total trigger count
SELECT COUNT(*) FROM information_schema.triggers WHERE trigger_schema = 'mydb';
```
*(Record these numbers somewhere safe to verify later).*

---

## Phase 1: Preparation & Backup

**1. Take the Production Database Dump**
Use the following "Safe for Production" command. 

> ⚠️ **IMPORTANT:** Run this command directly from your EC2 Linux terminal (bash prompt). **Do not** run this inside the MariaDB interactive SQL shell (`MariaDB [database]>`). If you are in the shell, type `exit;` first.

This combination of flags is the industry standard for extracting data without causing a production outage.
```bash
mysqldump -h prod-<DB_NAME>-db.us-east-2.rds.amazonaws.com \
          -u admin \
          -p \
          --single-transaction \
          --routines \
          --triggers \
          --hex-blob \
          mydb > production_dump_$(date +%F).sql
```

**2. Validate the Original Dump File**
Check the integrity of the downloaded production SQL dump before making changes.
```bash
# Verify the file completed successfully (look for standard SQL footers)
tail -n 2 production_dump_2026-06-16.sql

# Check how many tables are included
grep -c "CREATE TABLE" production_dump_2026-06-16.sql

# Check for hardcoded DEFINER permissions that might cause import errors
grep -o "DEFINER=[^ ]*" production_dump_2026-06-16.sql | sort | uniq
```

**2. Archive and Backup to S3**
Compress the original dump and securely store it in AWS S3.
```bash
gzip production_dump_$(date +%F).sql
aws s3 cp production_dump_$(date +%F).sql.gz s3://optic-db-dump-bucket/
```

---

## Phase 2: Dump File Sanitization & Optimization

**1. Download the backup from S3**
*(If you are performing this on a different EC2 instance than the one used for the dump)*
```bash
aws s3 cp s3://optic-db-dump-bucket/production_dump_$(date +%F).sql.gz .
```

**2. Unzip the working file**
```bash
gunzip production_dump_$(date +%F).sql.gz
```

**3. Sanitize and Optimize the SQL File (Linux)**
Modify the dump file to improve import speed and remove production-specific constraints.
```bash
# Wrap in a single transaction and disable foreign key checks for speed
echo "SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, AUTOCOMMIT=0; SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;" | cat - production_dump_2026-06-16.sql > temp.sql && mv temp.sql production_dump_2026-06-16.sql

# Remove DEFINER clauses to prevent permission errors during import
sed -i 's/DEFINER=[^ ]* / /g' production_dump_2026-06-16.sql

# Remove hardcoded schema/database references
sed -i 's/`mydb`\.//g' production_dump_2026-06-16.sql

# Add the commit and restore constraints at the end of the file
echo "COMMIT; SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS; SET AUTOCOMMIT=@OLD_AUTOCOMMIT;" >> production_dump_2026-06-16.sql
```

---

## Phase 3: Reset the DEV Database

**1. Backup the DEV Secrets Table**
Before dropping the DEV database, take a dump of the table containing your DEV secrets so you can restore them later.
```bash
mysqldump -h dev-<DB_NAME>-db.us-east-1.rds.amazonaws.com -u admin -p mydb secrets > dev_secrets_backup.sql
```

**2. Drop and Recreate the DEV Database**

**Option A: Via CLI Commands (Recommended)**
```bash
# Drop the existing database (WARNING: Deletes all DEV data)
mariadb -h dev-<DB_NAME>-db.us-east-1.rds.amazonaws.com -u admin -p -e "DROP DATABASE IF EXISTS mydb;"

# Create a fresh, empty database
mariadb -h dev-<DB_NAME>-db.us-east-1.rds.amazonaws.com -u admin -p -e "CREATE DATABASE mydb;"
```

**Option B: Interactive SQL Shell**
```sql
-- Login to MariaDB, then run:
SHOW PROCESSLIST; -- Identify and KILL any active connections to mydb if necessary
DROP DATABASE IF EXISTS mydb;
CREATE DATABASE mydb;
exit;
```

---

## Phase 4: Import Data to DEV

**1. Start a Screen Session (Optional but Recommended)**
Since imports can take a long time and might drop if your SSH connection dies, run it inside a `screen`.
```bash
screen -S dev_import
```

**2. Import the Sanitized Production Dump**
```bash
mariadb -h dev-<DB_NAME>-db.us-east-1.rds.amazonaws.com -P 3306 -u admin -p mydb < production_dump_2026-06-16.sql
```

---

## Phase 5: Post-Import Steps (Restore DEV Secrets & Validate)

After importing production data, you need to overwrite the production secrets with the DEV secrets.

**1. Drop the Production Secrets Table**
```bash
mariadb -h dev-<DB_NAME>-db.us-east-1.rds.amazonaws.com -P 3306 -u admin -p -e "DROP TABLE IF EXISTS mydb.secrets;"
```

**2. Import the DEV Secrets Backup**
```bash
mariadb -h dev-<DB_NAME>-db.us-east-1.rds.amazonaws.com -P 3306 -u admin -p mydb < dev_secrets_backup.sql
```

**3. Final Validation**
Log into the database and verify the import was successful by comparing against the metrics gathered in Phase 0.
```bash
# Log in to DEV database
mariadb -h dev-<DB_NAME>-db.us-east-1.rds.amazonaws.com -P 3306 -u admin -p mydb
```
```sql
-- Check total table count (Compare with Phase 0)
SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'mydb';

-- Check total trigger count (Compare with Phase 0)
SELECT COUNT(*) FROM information_schema.triggers WHERE trigger_schema = 'mydb';

-- Verify the secrets table exists and has data
SHOW TABLES LIKE 'secrets';
SELECT COUNT(*) FROM secrets;
```
