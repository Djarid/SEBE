#!/bin/bash
set -euo pipefail

# SEBE Proton Bridge entrypoint
#
# Automatically initialises pass/GPG and logs in via env vars.
# After first successful login, credentials persist in the /root volume
# and subsequent starts skip straight to running the bridge.
#
# Required env vars (first run only):
#   PROTON_USERNAME   — Proton email address
#   PROTON_PASSWORD   — Proton account password
#
# Optional:
#   PROTON_TOTP_SECRET — TOTP secret (base32) for 2FA auto-generation

BRIDGE_BIN="/usr/local/bin/proton-bridge"
GPG_PARAMS="/tmp/gpgparams"
MARKER="/root/.bridge-initialised"

# --- 1. Initialise pass/GPG if needed ---
if ! gpg --list-keys "bridge-key" &>/dev/null; then
    echo "[entrypoint] Generating GPG key for pass..."
    cat > "${GPG_PARAMS}" <<EOF
%no-protection
Key-Type: RSA
Key-Length: 2048
Name-Real: bridge-key
Expire-Date: 0
%commit
EOF
    gpg --batch --gen-key "${GPG_PARAMS}"
    rm -f "${GPG_PARAMS}"
    echo "[entrypoint] GPG key generated."
fi

if [ ! -d "/root/.password-store" ]; then
    echo "[entrypoint] Initialising pass store..."
    pass init bridge-key
    echo "[entrypoint] pass store ready."
fi

# --- 2. Check if Bridge already has an account ---
if [ -f "${MARKER}" ]; then
    echo "[entrypoint] Bridge already initialised, starting normally."
    exec "${BRIDGE_BIN}" --noninteractive
fi

# --- 3. First-run: auto-login via expect ---
if [ -z "${PROTON_USERNAME:-}" ] || [ -z "${PROTON_PASSWORD:-}" ]; then
    echo "[entrypoint] ERROR: First run requires PROTON_USERNAME and PROTON_PASSWORD."
    echo "[entrypoint] Set them in .env and restart."
    exit 1
fi

echo "[entrypoint] First run detected. Logging in as ${PROTON_USERNAME}..."

# Generate TOTP code if secret is provided
TOTP_CMD=""
if [ -n "${PROTON_TOTP_SECRET:-}" ]; then
    if command -v oathtool &>/dev/null; then
        TOTP_CMD="oathtool --totp --base32 '${PROTON_TOTP_SECRET}'"
    else
        echo "[entrypoint] WARNING: PROTON_TOTP_SECRET set but oathtool not installed."
        echo "[entrypoint] Install oath-toolkit if you need 2FA support."
    fi
fi

# Use expect to drive the Bridge CLI login
/usr/bin/expect <<EXPECT_SCRIPT
set timeout 120

spawn ${BRIDGE_BIN} --cli

# Wait for the CLI prompt
expect {
    ">>>" { }
    timeout { puts "ERROR: Bridge CLI did not start"; exit 1 }
}

# Send login command
send "login\r"

expect {
    -re "(?i)username|email" { }
    timeout { puts "ERROR: No username prompt"; exit 1 }
}
send "${PROTON_USERNAME}\r"

expect {
    -re "(?i)password" { }
    timeout { puts "ERROR: No password prompt"; exit 1 }
}
send "${PROTON_PASSWORD}\r"

# Handle optional 2FA prompt
expect {
    -re "(?i)two.factor|2fa|totp|code" {
        if { "${TOTP_CMD}" ne "" } {
            set totp_code [exec sh -c "${TOTP_CMD}"]
            send "\$totp_code\r"
        } else {
            puts "ERROR: 2FA required but no PROTON_TOTP_SECRET provided"
            exit 1
        }
        exp_continue
    }
    -re "(?i)account.*added|logged.in|successfully" {
        puts "Login successful."
    }
    -re "(?i)invalid|incorrect|failed|error" {
        puts "ERROR: Login failed. Check credentials."
        exit 1
    }
    ">>>" { }
    timeout { puts "ERROR: Login timed out"; exit 1 }
}

# Wait for the prompt after login
expect ">>>"

# Get account info (logs bridge password to container logs for first-run)
send "info\r"
expect ">>>"

# Exit the CLI
send "exit\r"
expect eof
EXPECT_SCRIPT

LOGIN_EXIT=$?

if [ ${LOGIN_EXIT} -ne 0 ]; then
    echo "[entrypoint] Login failed (exit code ${LOGIN_EXIT})."
    exit 1
fi

echo "[entrypoint] Login complete. Bridge password is in the logs above."
echo "[entrypoint] Copy it to .env as PROTON_BRIDGE_PASSWORD for reference."

# Mark as initialised so subsequent starts skip login
touch "${MARKER}"

# --- 4. Start Bridge ---
echo "[entrypoint] Starting Bridge..."
exec "${BRIDGE_BIN}" --noninteractive
