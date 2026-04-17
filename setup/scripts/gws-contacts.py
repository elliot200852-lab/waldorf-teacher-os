#!/usr/bin/env python3
"""
GWS Contacts Wrapper — People API direct access
=================================================
Workaround for gws CLI bug: People API calls return 403 even with
valid contacts scope. This script reads gws credentials and calls
the People API directly.

Usage:
    python3 setup/scripts/gws-contacts.py search "謝易霖"
    python3 setup/scripts/gws-contacts.py list
    python3 setup/scripts/gws-contacts.py list --filter "謝"

Requires: gws auth login (credentials at ~/.config/gws/credentials.enc)

When gws CLI fixes this bug, this script can be retired and replaced
with: gws people people searchContacts / connections list
"""

import sys
import json
import subprocess
import urllib.request
import urllib.parse
import urllib.error
import argparse


def get_credentials():
    """Read credentials from gws auth export."""
    try:
        result = subprocess.run(
            ["gws", "auth", "export", "--unmasked"],
            capture_output=True, text=True, timeout=10
        )
        # gws outputs "Using keyring backend: keyring" on stderr
        # and JSON on stdout
        output = result.stdout.strip()
        if not output:
            # Sometimes all output goes to stderr, parse from there
            lines = result.stderr.strip().split("\n")
            json_lines = [l for l in lines if l.strip().startswith("{") or l.strip().startswith('"') or l.strip().startswith("}")]
            output = "\n".join(json_lines)
        return json.loads(output)
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error reading gws credentials: {e}", file=sys.stderr)
        print("Make sure gws is installed and you have run: gws auth login", file=sys.stderr)
        sys.exit(2)


def get_access_token(creds):
    """Exchange refresh token for access token."""
    data = urllib.parse.urlencode({
        "client_id": creds["client_id"],
        "client_secret": creds["client_secret"],
        "refresh_token": creds["refresh_token"],
        "grant_type": "refresh_token"
    }).encode()
    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())["access_token"]
    except urllib.error.HTTPError as e:
        print(f"Auth error: {e.code} - {e.read().decode()[:200]}", file=sys.stderr)
        sys.exit(2)


def api_get(access_token, url):
    """Make authenticated GET request to Google API."""
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {access_token}"})
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()[:300]
        print(f"API error: {e.code} - {error_body}", file=sys.stderr)
        return None


def search_contacts(access_token, query):
    """Search contacts using People API searchContacts."""
    encoded_query = urllib.parse.quote(query)
    url = (
        f"https://people.googleapis.com/v1/people:searchContacts"
        f"?query={encoded_query}"
        f"&readMask=names,emailAddresses,phoneNumbers"
        f"&pageSize=30"
    )
    data = api_get(access_token, url)
    if not data:
        return []
    results = []
    for r in data.get("results", []):
        person = r.get("person", {})
        results.append(format_person(person))
    return results


def list_contacts(access_token, name_filter=None):
    """List all contacts, optionally filtered by name."""
    all_contacts = []
    page_token = ""
    while True:
        url = (
            f"https://people.googleapis.com/v1/people/me/connections"
            f"?personFields=names,emailAddresses,phoneNumbers"
            f"&pageSize=1000"
        )
        if page_token:
            url += f"&pageToken={page_token}"
        data = api_get(access_token, url)
        if not data:
            break
        for c in data.get("connections", []):
            person = format_person(c)
            if name_filter:
                if name_filter.lower() in person["name"].lower():
                    all_contacts.append(person)
            else:
                all_contacts.append(person)
        page_token = data.get("nextPageToken")
        if not page_token:
            break
    return all_contacts


def format_person(person):
    """Extract name, emails, phones from a person resource."""
    names = person.get("names", [])
    emails = person.get("emailAddresses", [])
    phones = person.get("phoneNumbers", [])
    return {
        "name": names[0]["displayName"] if names else "(no name)",
        "emails": [e["value"] for e in emails],
        "phones": [p["value"] for p in phones],
    }


def print_results(results, output_json=False):
    """Print contact results."""
    if output_json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return
    if not results:
        print("No contacts found.")
        return
    for r in results:
        print(f"Name: {r['name']}")
        for e in r["emails"]:
            print(f"  Email: {e}")
        for p in r["phones"]:
            print(f"  Phone: {p}")
        print()


def main():
    parser = argparse.ArgumentParser(description="Search Google Contacts via People API")
    subparsers = parser.add_subparsers(dest="command", help="Command")

    # search command
    search_parser = subparsers.add_parser("search", help="Search contacts by name")
    search_parser.add_argument("query", help="Search query (name)")
    search_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # list command
    list_parser = subparsers.add_parser("list", help="List all contacts")
    list_parser.add_argument("--filter", help="Filter by name substring")
    list_parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    creds = get_credentials()
    access_token = get_access_token(creds)

    if args.command == "search":
        results = search_contacts(access_token, args.query)
        if not results:
            # Fallback to list + filter
            results = list_contacts(access_token, args.query)
        print_results(results, args.json)

    elif args.command == "list":
        results = list_contacts(access_token, args.filter)
        print_results(results, args.json)


if __name__ == "__main__":
    main()
