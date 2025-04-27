#!/bin/bash

# setup_supabase.sh
# Automates Python virtual environment setup, .env creation, Supabase cloud migration
# (link, pull schema, create new migration, push migrations), and superadmin user creation
# for Linux and macOS

# Exit on any error
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Log functions
log_info() {
    echo -e "${GREEN}[INFO] $1${NC}"
}

log_error() {
    echo -e "${RED}[ERROR] $1${NC}" >&2
    exit 1
}

# Validate command availability
command_exists() {
    command -v "$1" >/dev/null 2>&1 || { log_error "$1 is required but not installed."; }
}

# Step 0: Check dependencies and setup virtual environment
log_info "Step 0: Setting up Python virtual environment and installing dependencies"

# Check for python3, pip, and supabase CLI
command_exists python3
command_exists pip3
command_exists supabase

# Verify Supabase CLI login
if ! supabase projects list >/dev/null 2>&1; then
    log_error "Supabase CLI is not logged in. Run 'supabase login' first."
fi

# Create and activate virtual environment
VENV_DIR="venv"
if [ -d "$VENV_DIR" ]; then
    log_info "Virtual environment already exists at $VENV_DIR"
else
    log_info "Creating virtual environment at $VENV_DIR"
    python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment (compatible with Linux/macOS)
source "$VENV_DIR/bin/activate"
log_info "Activated virtual environment"

# Check for requirements.txt and install dependencies
REQUIREMENTS_FILE="requirements.txt"
if [ ! -f "$REQUIREMENTS_FILE" ]; then
    log_error "$REQUIREMENTS_FILE does not exist"
fi

log_info "Installing dependencies from $REQUIREMENTS_FILE"
pip3 install -r "$REQUIREMENTS_FILE"
log_info "Dependencies installed successfully"

# Step 1: Create or update .env file
log_info "Step 1: Creating or updating .env file with environment variables"

ENV_FILE=".env"
if [ -f "$ENV_FILE" ]; then
    read -p ".env file already exists. Overwrite? (y/N): " overwrite
    if [[ ! "$overwrite" =~ ^[Yy]$ ]]; then
        log_info "Keeping existing .env file"
    else
        rm -f "$ENV_FILE"
        log_info "Removed existing .env file"
    fi
fi

# Prompt for environment variables
prompt_var() {
    local var_name=$1
    local prompt_text=$2
    local default_value=$3
    local value
    read -p "$prompt_text${default_value:+ (default: $default_value)}: " value
    if [ -z "$value" ] && [ -n "$default_value" ]; then
        echo "$default_value"
    elif [ -z "$value" ]; then
        log_error "$var_name cannot be empty"
    else
        echo "$value"
    fi
}

# Load existing .env for defaults if not overwriting
if [ -f "$ENV_FILE" ]; then
    source "$ENV_FILE"
fi

SUPABASE_URL=$(prompt_var "SUPABASE_URL" "Enter Supabase URL (e.g., https://your-project.supabase.co)" "${SUPABASE_URL}")
SUPABASE_SERVICE_CLIENT_ROLE_KEY=$(prompt_var "SUPABASE_SERVICE_CLIENT_ROLE_KEY" "Enter Supabase Service Role Key" "${SUPABASE_SERVICE_CLIENT_ROLE_KEY}")
SUPER_ADMIN_EMAIL=$(prompt_var "SUPER_ADMIN_EMAIL" "Enter Superadmin Email (e.g., superadmin@easely.app)" "${SUPER_ADMIN_EMAIL}")
SUPER_ADMIN_PASSWORD=$(prompt_var "SUPER_ADMIN_PASSWORD" "Enter Superadmin Password (min 6 characters)" "${SUPER_ADMIN_PASSWORD}")

# Write to .env file
cat << EOF > "$ENV_FILE"
SUPABASE_URL=$SUPABASE_URL
SUPABASE_SERVICE_CLIENT_ROLE_KEY=$SUPABASE_SERVICE_CLIENT_ROLE_KEY
SUPER_ADMIN_EMAIL=$SUPER_ADMIN_EMAIL
SUPER_ADMIN_PASSWORD=$SUPER_ADMIN_PASSWORD
EOF

log_info ".env file created successfully at $ENV_FILE"

# Secure the .env file
chmod 600 "$ENV_FILE"

# Step 2: Link local project to Supabase cloud, pull schema, create new migration, and push migrations
log_info "Step 2: Linking to Supabase cloud project, pulling schema, creating new migration, and pushing migrations"

# Prompt for Supabase project reference ID
PROJECT_REF=$(prompt_var "PROJECT_REF" "Enter Supabase Project Reference ID (e.g., wrxqlvsslhlyxkzftnej)" "")

# Link local project to cloud
log_info "Linking local project to Supabase cloud project $PROJECT_REF"
if supabase link --project-ref "$PROJECT_REF"; then
    log_info "Successfully linked to cloud project $PROJECT_REF"
else
    log_error "Failed to link to cloud project $PROJECT_REF"
fi

# Ensure migrations directory exists
MIGRATIONS_DIR="supabase/migrations"
if [ ! -d "$MIGRATIONS_DIR" ]; then
    log_info "Creating migrations directory at $MIGRATIONS_DIR"
    mkdir -p "$MIGRATIONS_DIR"
fi

# Pull schema from cloud to synchronize migrations
log_info "Pulling schema from Supabase cloud to synchronize migrations"
if supabase db pull; then
    log_info "Successfully pulled schema from cloud"
else
    log_error "Failed to pull schema from cloud"
fi

# Create a new migration called "new-migration"
log_info "Creating new migration named 'new-migration'"
if supabase migration new new-migration; then
    log_info "Successfully created new migration 'new-migration'"
else
    log_error "Failed to create new migration 'new-migration'"
fi

# Push migrations to cloud with repair fallback
log_info "Pushing migrations to Supabase cloud"
if ! supabase db push; then
    log_info "Migration push failed. Attempting to repair migration history."
    read -p "Enter migration version to repair (e.g., 20240620) or press Enter to skip: " repair_version
    if [ -n "$repair_version" ]; then
        log_info "Repairing migration history for version $repair_version"
        if supabase migration repair --status reverted "$repair_version"; then
            log_info "Migration history repaired. Retrying push..."
            if supabase db push; then
                log_info "Supabase cloud migrations applied successfully after repair"
            else
                log_error "Failed to apply Supabase cloud migrations even after repair"
            fi
        else
            log_error "Failed to repair migration history"
        fi
    else
        log_error "Failed to apply Supabase cloud migrations and no repair version provided"
    fi
else
    log_info "Supabase cloud migrations applied successfully"
fi

# Step 3: Run Python script to create superadmin (optional)
log_info "Step 3: Running Python script to create superadmin user"

PYTHON_SCRIPT="configs/create_admin.py"
if [ ! -f "$PYTHON_SCRIPT" ]; then
    log_info "Python script $PYTHON_SCRIPT does not exist. Skipping superadmin creation."
else
    # Run the Python script
    if python3 "$PYTHON_SCRIPT"; then
        log_info "Superadmin user creation script executed successfully"
    else
        log_error "Failed to execute superadmin user creation script"
    fi
fi

# Deactivate virtual environment
deactivate
log_info "Deactivated virtual environment"

log_info "Cloud migration and setup completed successfully!"