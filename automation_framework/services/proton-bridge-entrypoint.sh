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
    # Proton Bridge binds to 127.0.0.1 only. Forward from 0.0.0.0 for
    # container-to-container access.
    socat TCP-LISTEN:11143,fork,reuseaddr,bind=0.0.0.0 TCP:127.0.0.1:1143 &
    socat TCP-LISTEN:11025,fork,reuseaddr,bind=0.0.0.0 TCP:127.0.0.1:1025 &
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
TOTP_CODE=""
if [ -n "${PROTON_TOTP_SECRET:-}" ]; then
    if command -v oathtool &>/dev/null; then
        TOTP_CODE="$(oathtool --totp --base32 "${PROTON_TOTP_SECRET}")"
        echo "[entrypoint] Generated TOTP code for 2FA."
    else
        echo "[entrypoint] WARNING: PROTON_TOTP_SECRET set but oathtool not installed."
        echo "[entrypoint] Install oath-toolkit if you need 2FA support."
    fi
fi

# Use expect to drive the Bridge CLI login.
# Bridge v3 uses a bubbletea TUI with raw terminal mode and escape
# sequences. Credentials are passed via environment variables to avoid
# Tcl interpolation issues with special characters in passwords.
export _BRIDGE_USER="${PROTON_USERNAME}"
export _BRIDGE_PASS="${PROTON_PASSWORD}"
export _BRIDGE_TOTP="${TOTP_CODE}"
export _BRIDGE_BIN="${BRIDGE_BIN}"

/usr/bin/expect <<'EXPECT_SCRIPT'
set timeout 120
log_user 1

# Read credentials from env vars (avoids Tcl special char issues)
set bridge_bin $env(_BRIDGE_BIN)
set username $env(_BRIDGE_USER)
set password $env(_BRIDGE_PASS)
set totp_code $env(_BRIDGE_TOTP)

# Force a simple terminal to reduce escape sequence noise
set env(TERM) dumb

spawn $bridge_bin --cli

# Wait for the initial CLI prompt (>>> appears after the banner)
expect {
    ">>>" { }
    timeout { puts "ERROR: Bridge CLI did not start"; exit 1 }
}

# Small delay for the TUI to settle
sleep 1

# Send login command
send -- "login\r"

# Wait for username prompt
expect {
    -re {[Uu]sername} { }
    timeout { puts "ERROR: No username prompt"; exit 1 }
}

sleep 0.5
send -- "$username\r"

# Wait for password prompt (bridge verifies username with Proton first)
expect {
    -re {[Pp]assword} { }
    timeout { puts "ERROR: No password prompt (may be a network issue)"; exit 1 }
}

sleep 0.5
send -- "$password\r"

# Handle 2FA or success
expect {
    -re {[Tt]wo.[Ff]actor|2[Ff][Aa]|TOTP|[Cc]ode} {
        if { $totp_code ne "" } {
            sleep 0.5
            send -- "$totp_code\r"
        } else {
            puts "ERROR: 2FA required but no PROTON_TOTP_SECRET provided"
            exit 1
        }
        exp_continue
    }
    -re {[Aa]ccount.*added|[Ll]ogged.in|[Ss]uccessfully} {
        puts "\n\[entrypoint\] Login successful."
    }
    -re {[Ii]nvalid|[Ii]ncorrect|[Ff]ailed|[Bb]ad password} {
        puts "\n\[entrypoint\] ERROR: Login failed. Check credentials."
        exit 1
    }
    ">>>" {
        puts "\n\[entrypoint\] Got prompt after login (assuming success)."
    }
    timeout {
        puts "\n\[entrypoint\] ERROR: Login timed out."
        exit 1
    }
}

# Wait for a clean prompt
sleep 2
expect {
    ">>>" { }
    timeout { }
}

# Get account info (logs bridge password for first-run reference)
send -- "info\r"
expect {
    ">>>" { }
    timeout { }
}

# Exit the CLI
send -- "exit\r"
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

# --- 4. Start Bridge with socat forwarders ---
# Proton Bridge binds IMAP/SMTP to 127.0.0.1 only. For container-to-container
# communication we need them on 0.0.0.0. Run socat forwarders in background.
echo "[entrypoint] Starting socat forwarders (0.0.0.0 -> 127.0.0.1)..."
socat TCP-LISTEN:11143,fork,reuseaddr,bind=0.0.0.0 TCP:127.0.0.1:1143 &
socat TCP-LISTEN:11025,fork,reuseaddr,bind=0.0.0.0 TCP:127.0.0.1:1025 &

echo "[entrypoint] Starting Bridge..."
exec "${BRIDGE_BIN}" --noninteractive
