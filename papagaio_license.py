#!/usr/bin/env python3
"""
Papagaio License Manager
Handles trial period and license validation

Author: Alexandre Santos <alexandrehsantos@gmail.com>
Company: Bulvee Company
"""

import os
import sys
import json
import hashlib
import platform
import uuid
from datetime import datetime, timedelta
from pathlib import Path

# Trial configuration
TRIAL_DAYS = 7
PRODUCT_ID = "papagaio"
LICENSE_SERVER = "https://api.gumroad.com/v2/licenses/verify"

# License file location
if platform.system() == "Windows":
    LICENSE_DIR = Path(os.environ.get("APPDATA", "")) / "Papagaio"
else:
    LICENSE_DIR = Path.home() / ".config" / "papagaio"

LICENSE_FILE = LICENSE_DIR / ".license"
TRIAL_FILE = LICENSE_DIR / ".trial"


def get_machine_id():
    """Generate unique machine identifier"""
    try:
        # Try to get hardware-based ID
        if platform.system() == "Linux":
            # Use machine-id on Linux
            machine_id_file = Path("/etc/machine-id")
            if machine_id_file.exists():
                return machine_id_file.read_text().strip()

        elif platform.system() == "Darwin":
            # Use hardware UUID on macOS
            import subprocess
            result = subprocess.run(
                ["ioreg", "-rd1", "-c", "IOPlatformExpertDevice"],
                capture_output=True, text=True
            )
            for line in result.stdout.split("\n"):
                if "IOPlatformUUID" in line:
                    return line.split('"')[-2]

        elif platform.system() == "Windows":
            # Use Windows machine GUID
            import subprocess
            result = subprocess.run(
                ["wmic", "csproduct", "get", "UUID"],
                capture_output=True, text=True
            )
            lines = result.stdout.strip().split("\n")
            if len(lines) > 1:
                return lines[1].strip()

    except Exception:
        pass

    # Fallback: generate based on hostname + username
    fallback = f"{platform.node()}-{os.getlogin()}-{uuid.getnode()}"
    return hashlib.sha256(fallback.encode()).hexdigest()[:32]


def get_trial_info():
    """Get trial start date and remaining days"""
    LICENSE_DIR.mkdir(parents=True, exist_ok=True)

    if not TRIAL_FILE.exists():
        # First run - start trial
        trial_data = {
            "start_date": datetime.now().isoformat(),
            "machine_id": get_machine_id()
        }
        TRIAL_FILE.write_text(json.dumps(trial_data))
        return {
            "started": datetime.now(),
            "remaining_days": TRIAL_DAYS,
            "expired": False
        }

    try:
        trial_data = json.loads(TRIAL_FILE.read_text())
        start_date = datetime.fromisoformat(trial_data["start_date"])
        elapsed = datetime.now() - start_date
        remaining = TRIAL_DAYS - elapsed.days

        return {
            "started": start_date,
            "remaining_days": max(0, remaining),
            "expired": remaining <= 0
        }
    except Exception:
        # Corrupted trial file - treat as expired
        return {
            "started": None,
            "remaining_days": 0,
            "expired": True
        }


def validate_license_key(license_key):
    """Validate license key with Gumroad API"""
    try:
        import urllib.request
        import urllib.parse

        data = urllib.parse.urlencode({
            "product_id": PRODUCT_ID,
            "license_key": license_key,
            "increment_uses_count": "false"
        }).encode()

        req = urllib.request.Request(LICENSE_SERVER, data=data)
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode())

            if result.get("success"):
                return {
                    "valid": True,
                    "email": result.get("purchase", {}).get("email"),
                    "uses": result.get("uses", 0),
                    "message": "License activated successfully"
                }
            else:
                return {
                    "valid": False,
                    "message": result.get("message", "Invalid license key")
                }

    except urllib.error.URLError:
        # Offline validation - check local cache
        return validate_offline(license_key)
    except Exception as e:
        return {
            "valid": False,
            "message": f"Validation error: {str(e)}"
        }


def validate_offline(license_key):
    """Offline license validation using cached data"""
    if LICENSE_FILE.exists():
        try:
            license_data = json.loads(LICENSE_FILE.read_text())
            if license_data.get("key") == license_key:
                return {
                    "valid": True,
                    "email": license_data.get("email"),
                    "message": "License valid (offline mode)"
                }
        except Exception:
            pass

    return {
        "valid": False,
        "message": "Cannot validate license offline"
    }


def activate_license(license_key):
    """Activate and save license"""
    result = validate_license_key(license_key)

    if result["valid"]:
        license_data = {
            "key": license_key,
            "email": result.get("email"),
            "machine_id": get_machine_id(),
            "activated_at": datetime.now().isoformat()
        }
        LICENSE_DIR.mkdir(parents=True, exist_ok=True)
        LICENSE_FILE.write_text(json.dumps(license_data))

    return result


def get_license_status():
    """Get current license status"""
    # Check for valid license
    if LICENSE_FILE.exists():
        try:
            license_data = json.loads(LICENSE_FILE.read_text())
            if license_data.get("key"):
                # Verify machine ID matches
                if license_data.get("machine_id") == get_machine_id():
                    return {
                        "status": "licensed",
                        "email": license_data.get("email"),
                        "message": "License active"
                    }
                else:
                    return {
                        "status": "invalid",
                        "message": "License registered to different machine"
                    }
        except Exception:
            pass

    # Check trial status
    trial = get_trial_info()

    if not trial["expired"]:
        return {
            "status": "trial",
            "remaining_days": trial["remaining_days"],
            "message": f"Trial: {trial['remaining_days']} days remaining"
        }
    else:
        return {
            "status": "expired",
            "message": "Trial expired. Please purchase a license."
        }


def check_license():
    """Main license check - returns True if allowed to run"""
    status = get_license_status()

    if status["status"] == "licensed":
        return True, status["message"]

    if status["status"] == "trial":
        return True, status["message"]

    return False, status["message"]


def deactivate_license():
    """Remove license (for troubleshooting)"""
    if LICENSE_FILE.exists():
        LICENSE_FILE.unlink()
        return True
    return False


# CLI interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Papagaio License Manager")
    parser.add_argument("--status", action="store_true", help="Show license status")
    parser.add_argument("--activate", metavar="KEY", help="Activate license key")
    parser.add_argument("--deactivate", action="store_true", help="Deactivate license")
    parser.add_argument("--machine-id", action="store_true", help="Show machine ID")

    args = parser.parse_args()

    if args.status:
        status = get_license_status()
        print(f"Status: {status['status']}")
        print(f"Message: {status['message']}")
        if status.get('email'):
            print(f"Email: {status['email']}")
        if status.get('remaining_days'):
            print(f"Trial days remaining: {status['remaining_days']}")

    elif args.activate:
        result = activate_license(args.activate)
        if result["valid"]:
            print(f"✓ {result['message']}")
        else:
            print(f"✗ {result['message']}")
            sys.exit(1)

    elif args.deactivate:
        if deactivate_license():
            print("License deactivated")
        else:
            print("No license to deactivate")

    elif args.machine_id:
        print(f"Machine ID: {get_machine_id()}")

    else:
        parser.print_help()
