"""
SEBE Klaxxon Client — Manage reminders and schedules via Klaxxon API.

Stateless CLI/library client for the Klaxxon reminder system. All state
lives on the Klaxxon API server. This tool handles auth, serialisation
and human-readable formatting.

Credentials read from .env at repo root (KLAXXON_API_URL, KLAXXON_API_TOKEN).
Tokens are never displayed in output.

Usage (CLI, from automation_framework/):
    python -m tools.klaxxon health
    python -m tools.klaxxon create --title "AI Strategy" --starts-at "2026-03-17T19:30:00Z"
    python -m tools.klaxxon list
    python -m tools.klaxxon list --state pending
    python -m tools.klaxxon get --id 37
    python -m tools.klaxxon ack --id 37
    python -m tools.klaxxon skip --id 37
    python -m tools.klaxxon delete --id 37
    python -m tools.klaxxon create-schedule --title "Standup" --time "09:00" --recurrence daily
    python -m tools.klaxxon list-schedules
    python -m tools.klaxxon list --json

Usage (library):
    from tools.klaxxon import create_reminder, list_reminders, health
    result = create_reminder(title="Meeting", starts_at="2026-03-17T19:30:00Z")
    reminders = list_reminders(state="pending")
"""

import argparse
import json
import ssl
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Optional


# ── Paths ──────────────────────────────────────────────────────────────

FRAMEWORK_ROOT = Path(__file__).parent.parent  # automation_framework/
REPO_ROOT = FRAMEWORK_ROOT.parent  # SEBE/
ENV_FILE = REPO_ROOT / ".env"


# ── .env reader ────────────────────────────────────────────────────────


def _load_env() -> dict[str, str]:
    """Parse .env file into a dict. Simple KEY=VALUE, no interpolation."""
    env: dict[str, str] = {}
    if not ENV_FILE.exists():
        return env
    with open(ENV_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            env[key.strip()] = value.strip()
    return env


def _get_config() -> tuple[str, str]:
    """Load and validate Klaxxon credentials from .env.

    Returns:
        (base_url, token) tuple.

    Raises:
        SystemExit: if required keys are missing.
    """
    env = _load_env()
    url = env.get("KLAXXON_API_URL", "").rstrip("/")
    token = env.get("KLAXXON_API_TOKEN", "")
    missing = []
    if not url:
        missing.append("KLAXXON_API_URL")
    if not token:
        missing.append("KLAXXON_API_TOKEN")
    if missing:
        print(
            f"Error: Missing .env keys: {', '.join(missing)}\nExpected in {ENV_FILE}",
            file=sys.stderr,
        )
        sys.exit(1)
    return url, token


# ── HTTP transport ─────────────────────────────────────────────────────


def _request(
    method: str,
    path: str,
    body: Optional[dict] = None,
    *,
    base_url: Optional[str] = None,
    token: Optional[str] = None,
) -> dict[str, Any]:
    """Make an authenticated JSON request to the Klaxxon API.

    Single Responsibility: all HTTP, auth, serialisation and error
    handling lives here. Every public function delegates to this.

    Args:
        method: HTTP method (GET, POST, PATCH, DELETE).
        path: API path (e.g. "/api/reminders").
        body: Optional JSON body for POST/PATCH.
        base_url: Override base URL (default: from .env).
        token: Override bearer token (default: from .env).

    Returns:
        Parsed JSON response as dict, or {"success": True} for 204.
    """
    if base_url is None or token is None:
        _url, _token = _get_config()
        base_url = base_url or _url
        token = token or _token

    url = f"{base_url}{path}"
    data = json.dumps(body).encode("utf-8") if body else None

    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    req.add_header("User-Agent", "SEBE-Klaxxon-Client/1.0")

    ctx = ssl.create_default_context()

    try:
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            if resp.status == 204:
                return {"success": True}
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {"success": True}
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        try:
            detail = json.loads(error_body)
        except (json.JSONDecodeError, ValueError):
            detail = {"detail": error_body}
        return {
            "success": False,
            "status": e.code,
            "error": detail.get("detail", str(detail)),
        }
    except urllib.error.URLError as e:
        return {
            "success": False,
            "error": f"Connection failed: {e.reason}",
        }


# ── Reminder operations ────────────────────────────────────────────────


def create_reminder(
    title: str,
    starts_at: str,
    duration_min: int = 30,
    link: Optional[str] = None,
    description: Optional[str] = None,
    profile: str = "meeting",
    source: str = "sebe-tool",
    escalate_to: Optional[str] = None,
    lead_time_min: Optional[int] = None,
    nag_interval_min: Optional[int] = None,
) -> dict:
    """Create a new reminder."""
    payload: dict[str, Any] = {
        "title": title,
        "starts_at": starts_at,
        "duration_min": duration_min,
        "profile": profile,
        "source": source,
    }
    if link is not None:
        payload["link"] = link
    if description is not None:
        payload["description"] = description
    if escalate_to is not None:
        payload["escalate_to"] = escalate_to
    if lead_time_min is not None:
        payload["lead_time_min"] = lead_time_min
    if nag_interval_min is not None:
        payload["nag_interval_min"] = nag_interval_min
    return _request("POST", "/api/reminders", payload)


def list_reminders(state: Optional[str] = None) -> dict:
    """List reminders, optionally filtered by state."""
    path = "/api/reminders"
    if state:
        path = f"{path}?state={state}"
    return _request("GET", path)


def get_reminder(reminder_id: int) -> dict:
    """Get a single reminder by ID."""
    return _request("GET", f"/api/reminders/{reminder_id}")


def update_reminder(reminder_id: int, **fields) -> dict:
    """Partial update of a reminder's fields."""
    return _request("PATCH", f"/api/reminders/{reminder_id}", fields)


def delete_reminder(reminder_id: int) -> dict:
    """Delete a reminder."""
    return _request("DELETE", f"/api/reminders/{reminder_id}")


def ack_reminder(reminder_id: int, keyword: str = "ack") -> dict:
    """Acknowledge a reminder (stops notifications)."""
    return _request("POST", f"/api/reminders/{reminder_id}/ack", {"keyword": keyword})


def skip_reminder(reminder_id: int) -> dict:
    """Skip a reminder deliberately."""
    return _request("POST", f"/api/reminders/{reminder_id}/skip")


def resend_reminder(reminder_id: int) -> dict:
    """Resend notification for a reminder."""
    return _request("POST", f"/api/reminders/{reminder_id}/resend")


# ── Schedule operations ────────────────────────────────────────────────


def create_schedule(
    title: str,
    time_of_day: str,
    recurrence: str,
    recurrence_rule: Optional[str] = None,
    duration_min: int = 0,
    link: Optional[str] = None,
    description: Optional[str] = None,
    profile: str = "meeting",
    escalate_to: Optional[str] = None,
    lead_time_min: Optional[int] = None,
    nag_interval_min: Optional[int] = None,
) -> dict:
    """Create a new recurring schedule."""
    payload: dict[str, Any] = {
        "title": title,
        "time_of_day": time_of_day,
        "recurrence": recurrence,
        "profile": profile,
    }
    if recurrence_rule is not None:
        payload["recurrence_rule"] = recurrence_rule
    if duration_min:
        payload["duration_min"] = duration_min
    if link is not None:
        payload["link"] = link
    if description is not None:
        payload["description"] = description
    if escalate_to is not None:
        payload["escalate_to"] = escalate_to
    if lead_time_min is not None:
        payload["lead_time_min"] = lead_time_min
    if nag_interval_min is not None:
        payload["nag_interval_min"] = nag_interval_min
    return _request("POST", "/api/schedules", payload)


def list_schedules(active_only: bool = True) -> dict:
    """List schedules."""
    path = f"/api/schedules?active_only={'true' if active_only else 'false'}"
    return _request("GET", path)


def get_schedule(schedule_id: int) -> dict:
    """Get a single schedule by ID."""
    return _request("GET", f"/api/schedules/{schedule_id}")


def update_schedule(schedule_id: int, **fields) -> dict:
    """Partial update of a schedule's fields."""
    return _request("PATCH", f"/api/schedules/{schedule_id}", fields)


def delete_schedule(schedule_id: int) -> dict:
    """Deactivate a schedule (soft delete)."""
    return _request("DELETE", f"/api/schedules/{schedule_id}")


# ── System ─────────────────────────────────────────────────────────────


def health() -> dict:
    """Check Klaxxon API health."""
    return _request("GET", "/api/health")


# ── Formatters ─────────────────────────────────────────────────────────


def _format_reminder(r: dict) -> str:
    """Format a single reminder for human-readable output."""
    lines = [
        f"  ID:          {r['id']}",
        f"  Title:       {r['title']}",
        f"  State:       {r['state']}",
        f"  Starts:      {r['starts_at']}",
        f"  Duration:    {r['duration_min']} min",
        f"  Profile:     {r['profile']}",
    ]
    if r.get("description"):
        lines.append(f"  Description: {r['description']}")
    if r.get("link"):
        lines.append(f"  Link:        {r['link']}")
    if r.get("escalate_to"):
        lines.append(f"  Escalate to: {r['escalate_to']}")
    if r.get("schedule_id"):
        lines.append(f"  Schedule:    #{r['schedule_id']}")
    if r.get("ack_at"):
        lines.append(f"  Acked at:    {r['ack_at']}")
    return "\n".join(lines)


def _format_schedule(s: dict) -> str:
    """Format a single schedule for human-readable output."""
    lines = [
        f"  ID:          {s['id']}",
        f"  Title:       {s['title']}",
        f"  Time:        {s['time_of_day']}",
        f"  Recurrence:  {s['recurrence']}",
        f"  Profile:     {s['profile']}",
        f"  Active:      {s.get('is_active', True)}",
    ]
    if s.get("recurrence_rule"):
        lines.append(f"  Days:        {s['recurrence_rule']}")
    if s.get("description"):
        lines.append(f"  Description: {s['description']}")
    if s.get("link"):
        lines.append(f"  Link:        {s['link']}")
    if s.get("duration_min"):
        lines.append(f"  Duration:    {s['duration_min']} min")
    if s.get("escalate_to"):
        lines.append(f"  Escalate to: {s['escalate_to']}")
    return "\n".join(lines)


def _print_result(result: dict, as_json: bool = False) -> None:
    """Print an API result, handling both success and error cases."""
    if as_json:
        print(json.dumps(result, indent=2, default=str))
        return

    if result.get("success") is False:
        status = result.get("status", "")
        error = result.get("error", "Unknown error")
        prefix = f"Error ({status})" if status else "Error"
        print(f"{prefix}: {error}", file=sys.stderr)
        sys.exit(1)

    # Health response
    if "signal_connected" in result:
        print(f"Status:            {result['status']}")
        print(f"Version:           {result['version']}")
        print(f"Signal connected:  {result['signal_connected']}")
        print(f"DB OK:             {result['db_ok']}")
        print(f"Pending:           {result['reminders_pending']}")
        print(f"Reminding:         {result['reminders_reminding']}")
        if result.get("next_reminder"):
            print(f"Next reminder:     {result['next_reminder']}")
        return

    # Reminder list
    if "reminders" in result:
        count = result.get("count", len(result["reminders"]))
        print(f"Reminders: {count}\n")
        for r in result["reminders"]:
            print(_format_reminder(r))
            print()
        return

    # Schedule list
    if "schedules" in result:
        count = result.get("count", len(result["schedules"]))
        print(f"Schedules: {count}\n")
        for s in result["schedules"]:
            print(_format_schedule(s))
            print()
        return

    # Single reminder (has "state" and "starts_at")
    if "state" in result and "starts_at" in result:
        print(_format_reminder(result))
        return

    # Single schedule (has "time_of_day")
    if "time_of_day" in result:
        print(_format_schedule(result))
        return

    # Resend response
    if "sent" in result and "reminder_id" in result:
        print(f"Reminder #{result['reminder_id']}: {result['message']}")
        if result.get("ack_url"):
            print(f"Ack URL: {result['ack_url']}")
        return

    # Delete / generic success
    if result.get("success"):
        print("OK")
        return

    # Fallback
    print(json.dumps(result, indent=2, default=str))


# ── CLI ────────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(
        description="SEBE Klaxxon Client — Manage reminders and schedules"
    )
    sub = parser.add_subparsers(dest="action", required=True)

    # Shared --json flag added to every subparser via parent
    _json_parent = argparse.ArgumentParser(add_help=False)
    _json_parent.add_argument("--json", action="store_true", help="Output as JSON")

    # -- health --
    sub.add_parser("health", help="Check Klaxxon API health", parents=[_json_parent])

    # -- create --
    p_create = sub.add_parser(
        "create", help="Create a reminder", parents=[_json_parent]
    )
    p_create.add_argument("--title", required=True, help="Reminder title")
    p_create.add_argument("--starts-at", required=True, help="Start time (ISO 8601)")
    p_create.add_argument(
        "--duration", type=int, default=30, help="Duration in minutes (default: 30)"
    )
    p_create.add_argument("--link", help="Meeting/event link")
    p_create.add_argument("--description", help="Description text")
    p_create.add_argument(
        "--profile", default="meeting", help="Escalation profile (default: meeting)"
    )
    p_create.add_argument(
        "--source", default="sebe-tool", help="Source identifier (default: sebe-tool)"
    )
    p_create.add_argument("--escalate-to", help="Escalation phone number (E.164)")
    p_create.add_argument("--lead-time", type=int, help="Lead time override (minutes)")
    p_create.add_argument(
        "--nag-interval", type=int, help="Nag interval override (minutes)"
    )

    # -- list --
    p_list = sub.add_parser("list", help="List reminders", parents=[_json_parent])
    p_list.add_argument(
        "--state",
        help="Filter by state (pending, reminding, acknowledged, skipped, missed)",
    )

    # -- get --
    p_get = sub.add_parser("get", help="Get a single reminder", parents=[_json_parent])
    p_get.add_argument("--id", type=int, required=True, help="Reminder ID")

    # -- update --
    p_update = sub.add_parser(
        "update", help="Update a reminder", parents=[_json_parent]
    )
    p_update.add_argument("--id", type=int, required=True, help="Reminder ID")
    p_update.add_argument("--title", help="New title")
    p_update.add_argument("--starts-at", help="New start time (ISO 8601)")
    p_update.add_argument("--duration", type=int, help="New duration (minutes)")
    p_update.add_argument("--link", help="New link")
    p_update.add_argument("--description", help="New description")
    p_update.add_argument("--profile", help="New escalation profile")
    p_update.add_argument("--escalate-to", help="New escalation number (E.164)")
    p_update.add_argument("--lead-time", type=int, help="Lead time override (minutes)")
    p_update.add_argument(
        "--nag-interval", type=int, help="Nag interval override (minutes)"
    )

    # -- ack --
    p_ack = sub.add_parser("ack", help="Acknowledge a reminder", parents=[_json_parent])
    p_ack.add_argument("--id", type=int, required=True, help="Reminder ID")
    p_ack.add_argument("--keyword", default="ack", help="Ack keyword (default: ack)")

    # -- skip --
    p_skip = sub.add_parser("skip", help="Skip a reminder", parents=[_json_parent])
    p_skip.add_argument("--id", type=int, required=True, help="Reminder ID")

    # -- resend --
    p_resend = sub.add_parser(
        "resend", help="Resend notification for a reminder", parents=[_json_parent]
    )
    p_resend.add_argument("--id", type=int, required=True, help="Reminder ID")

    # -- delete --
    p_delete = sub.add_parser(
        "delete", help="Delete a reminder", parents=[_json_parent]
    )
    p_delete.add_argument("--id", type=int, required=True, help="Reminder ID")

    # -- create-schedule --
    p_csched = sub.add_parser(
        "create-schedule", help="Create a recurring schedule", parents=[_json_parent]
    )
    p_csched.add_argument("--title", required=True, help="Schedule title")
    p_csched.add_argument("--time", required=True, help="Time of day (HH:MM)")
    p_csched.add_argument(
        "--recurrence", required=True, help="Recurrence (daily, weekly, custom)"
    )
    p_csched.add_argument(
        "--days", help="Day list for weekly/custom (e.g. mon,wed,fri)"
    )
    p_csched.add_argument(
        "--duration", type=int, default=0, help="Duration in minutes (default: 0)"
    )
    p_csched.add_argument("--link", help="Meeting/event link")
    p_csched.add_argument("--description", help="Description text")
    p_csched.add_argument(
        "--profile", default="meeting", help="Escalation profile (default: meeting)"
    )
    p_csched.add_argument("--escalate-to", help="Escalation phone number (E.164)")
    p_csched.add_argument("--lead-time", type=int, help="Lead time override (minutes)")
    p_csched.add_argument(
        "--nag-interval", type=int, help="Nag interval override (minutes)"
    )

    # -- list-schedules --
    p_lsched = sub.add_parser(
        "list-schedules", help="List schedules", parents=[_json_parent]
    )
    p_lsched.add_argument(
        "--all", action="store_true", help="Include inactive schedules"
    )

    # -- get-schedule --
    p_gsched = sub.add_parser(
        "get-schedule", help="Get a single schedule", parents=[_json_parent]
    )
    p_gsched.add_argument("--id", type=int, required=True, help="Schedule ID")

    # -- update-schedule --
    p_usched = sub.add_parser(
        "update-schedule", help="Update a schedule", parents=[_json_parent]
    )
    p_usched.add_argument("--id", type=int, required=True, help="Schedule ID")
    p_usched.add_argument("--title", help="New title")
    p_usched.add_argument("--time", help="New time of day (HH:MM)")
    p_usched.add_argument("--recurrence", help="New recurrence (daily, weekly, custom)")
    p_usched.add_argument("--days", help="New day list (e.g. mon,wed,fri)")
    p_usched.add_argument("--duration", type=int, help="New duration (minutes)")
    p_usched.add_argument("--link", help="New link")
    p_usched.add_argument("--description", help="New description")
    p_usched.add_argument("--profile", help="New escalation profile")
    p_usched.add_argument("--escalate-to", help="New escalation number (E.164)")
    p_usched.add_argument(
        "--active", choices=["true", "false"], help="Set active state"
    )

    # -- delete-schedule --
    p_dsched = sub.add_parser(
        "delete-schedule", help="Deactivate a schedule", parents=[_json_parent]
    )
    p_dsched.add_argument("--id", type=int, required=True, help="Schedule ID")

    args = parser.parse_args()
    result: dict

    # ── Dispatch ───────────────────────────────────────────────────────

    if args.action == "health":
        result = health()

    elif args.action == "create":
        result = create_reminder(
            title=args.title,
            starts_at=args.starts_at,
            duration_min=args.duration,
            link=args.link,
            description=args.description,
            profile=args.profile,
            source=args.source,
            escalate_to=args.escalate_to,
            lead_time_min=args.lead_time,
            nag_interval_min=args.nag_interval,
        )

    elif args.action == "list":
        result = list_reminders(state=args.state)

    elif args.action == "get":
        result = get_reminder(args.id)

    elif args.action == "update":
        fields: dict[str, Any] = {}
        if args.title is not None:
            fields["title"] = args.title
        if args.starts_at is not None:
            fields["starts_at"] = args.starts_at
        if args.duration is not None:
            fields["duration_min"] = args.duration
        if args.link is not None:
            fields["link"] = args.link
        if args.description is not None:
            fields["description"] = args.description
        if args.profile is not None:
            fields["profile"] = args.profile
        if args.escalate_to is not None:
            fields["escalate_to"] = args.escalate_to
        if args.lead_time is not None:
            fields["lead_time_min"] = args.lead_time
        if args.nag_interval is not None:
            fields["nag_interval_min"] = args.nag_interval
        if not fields:
            print(
                "Error: No fields to update. Provide at least one field.",
                file=sys.stderr,
            )
            sys.exit(1)
        result = update_reminder(args.id, **fields)

    elif args.action == "ack":
        result = ack_reminder(args.id, keyword=args.keyword)

    elif args.action == "skip":
        result = skip_reminder(args.id)

    elif args.action == "resend":
        result = resend_reminder(args.id)

    elif args.action == "delete":
        result = delete_reminder(args.id)

    elif args.action == "create-schedule":
        result = create_schedule(
            title=args.title,
            time_of_day=args.time,
            recurrence=args.recurrence,
            recurrence_rule=args.days,
            duration_min=args.duration,
            link=args.link,
            description=args.description,
            profile=args.profile,
            escalate_to=args.escalate_to,
            lead_time_min=args.lead_time,
            nag_interval_min=args.nag_interval,
        )

    elif args.action == "list-schedules":
        result = list_schedules(active_only=not args.all)

    elif args.action == "get-schedule":
        result = get_schedule(args.id)

    elif args.action == "update-schedule":
        fields = {}
        if args.title is not None:
            fields["title"] = args.title
        if args.time is not None:
            fields["time_of_day"] = args.time
        if args.recurrence is not None:
            fields["recurrence"] = args.recurrence
        if args.days is not None:
            fields["recurrence_rule"] = args.days
        if args.duration is not None:
            fields["duration_min"] = args.duration
        if args.link is not None:
            fields["link"] = args.link
        if args.description is not None:
            fields["description"] = args.description
        if args.profile is not None:
            fields["profile"] = args.profile
        if args.escalate_to is not None:
            fields["escalate_to"] = args.escalate_to
        if args.active is not None:
            fields["is_active"] = args.active == "true"
        if not fields:
            print(
                "Error: No fields to update. Provide at least one field.",
                file=sys.stderr,
            )
            sys.exit(1)
        result = update_schedule(args.id, **fields)

    elif args.action == "delete-schedule":
        result = delete_schedule(args.id)

    else:
        parser.print_help()
        sys.exit(1)

    _print_result(result, as_json=args.json)


if __name__ == "__main__":
    main()
