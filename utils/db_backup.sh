#!/bin/bash

# Configuration
CONFIG_FILE="/home/<user>/Kiosk/config.json"
SQLITE_DB_FILE="/home/<user>/Kiosk/src/database/kiosk.db"
BACKUP_DIR="/home/<user>/DB-Backup/"

mkdir -p ${BACKUP_DIR}

get_db_type() {
    if [ ! -f "$CONFIG_FILE" ]; then
        echo "ERROR: Config file not found: $CONFIG_FILE"
        exit 1
    fi
    
    DB_TYPE=$(python3 -c "
import json
with open('$CONFIG_FILE', 'r') as f:
    config = json.load(f)
    print(config.get('database', {}).get('type', 'sqlite').lower())
" 2>/dev/null)
    
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to read database type from config"
        exit 1
    fi
    
    echo "$DB_TYPE"
}

backup_sqlite() {
    echo "Creating SQLite backup..."
    
    if [ ! -f "$SQLITE_DB_FILE" ]; then
        echo "ERROR: SQLite database file not found: $SQLITE_DB_FILE"
        exit 1
    fi
    
    BACKUP_FILE="${BACKUP_DIR}/sqlite_backup_$(date +%Y-%m-%d_%H-%M-%S).db"
    
    cp "${SQLITE_DB_FILE}" "${BACKUP_FILE}"
    
    if [ $? -eq 0 ]; then
        echo "SUCCESS: SQLite backup created: $BACKUP_FILE"
        echo "Backup size: $(du -h "$BACKUP_FILE" | cut -f1)"
    else
        echo "ERROR: Failed to create SQLite backup"
        exit 1
    fi
}

backup_postgresql() {
    echo "Creating PostgreSQL backup..."
    
    PG_CONFIG=$(python3 -c "
import json
with open('$CONFIG_FILE', 'r') as f:
    config = json.load(f)
    pg_config = config.get('database', {}).get('postgresql', {})
    print(f\"{pg_config.get('host', 'localhost')}:{pg_config.get('port', 5432)}:{pg_config.get('database', 'kiosk')}:{pg_config.get('username', 'kiosk')}:{pg_config.get('password', '')}\")
" 2>/dev/null)
    
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to read PostgreSQL configuration"
        exit 1
    fi
    
    IFS=':' read -r PG_HOST PG_PORT PG_DATABASE PG_USERNAME PG_PASSWORD <<< "$PG_CONFIG"
    
    BACKUP_FILE="${BACKUP_DIR}/postgres_backup_$(date +%Y-%m-%d_%H-%M-%S).sql"
    
    # Set environment variables for pg_dump
    export PGPASSWORD="$PG_PASSWORD"
    
    pg_dump -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USERNAME" -d "$PG_DATABASE" \
            --no-password --verbose --clean --if-exists --create > "$BACKUP_FILE" 2>/dev/null
    
    if [ $? -eq 0 ] && [ -s "$BACKUP_FILE" ]; then
        echo "SUCCESS: PostgreSQL backup created: $BACKUP_FILE"
        echo "Backup size: $(du -h "$BACKUP_FILE" | cut -f1)"
        
        gzip "$BACKUP_FILE"
        echo "Backup compressed: ${BACKUP_FILE}.gz"
    else
        echo "ERROR: Failed to create PostgreSQL backup"
        rm -f "$BACKUP_FILE" 2>/dev/null
        exit 1
    fi
    
    # Delete the password environment variable
    unset PGPASSWORD
}

cleanup_old_backups() {
    echo "Cleaning up old backups (keeping last 7)..."
    
    find "$BACKUP_DIR" -name "sqlite_backup_*.db" -type f -mtime +7 -delete 2>/dev/null
    
    find "$BACKUP_DIR" -name "postgres_backup_*.sql.gz" -type f -mtime +7 -delete 2>/dev/null
    find "$BACKUP_DIR" -name "postgres_backup_*.sql" -type f -mtime +7 -delete 2>/dev/null
    
    echo "Cleanup completed"
}

main() {
    echo "=== Database Backup Script ==="
    echo "Timestamp: $(date)"
    echo "Config file: $CONFIG_FILE"
    
    DB_TYPE=$(get_db_type)
    echo "Database type: $DB_TYPE"
    
    case "$DB_TYPE" in
        "sqlite")
            backup_sqlite
            ;;
        "postgresql")
            backup_postgresql
            ;;
        *)
            echo "ERROR: Unsupported database type: $DB_TYPE"
            echo "Supported types: sqlite, postgresql"
            exit 1
            ;;
    esac
    
    cleanup_old_backups
    
    echo "=== Backup completed ==="
}

# Check whether required tools are available
check_dependencies() {
    if ! command -v python3 &> /dev/null; then
        echo "ERROR: python3 is required but not installed"
        exit 1
    fi
    
    if [ "$(get_db_type)" = "postgresql" ]; then
        if ! command -v pg_dump &> /dev/null; then
            echo "ERROR: pg_dump is required for PostgreSQL backups but not installed"
            echo "Install with: sudo apt-get install postgresql-client"
            exit 1
        fi
    fi
}

check_dependencies

main