"""Resolve a credential without ever printing it to logs.

Order: environment variable (cloud runs) -> local .env file (Label: value format).
Usage as a script writes the value to a file, never stdout:
  python3 ch_secret.py base44 <out_file>
"""
import os, sys

LEGACY_ENV_FILE = "C:/Users/Will Ritchings/Desktop/Claude/GTM_ENG/The Reserve/T-tools/API Keys and Access/.env"

# name -> (environment variable, .env label prefix)
SECRETS = {
    "hubspot": ("HUBSPOT_TOKEN", "HubSpot API Service Key"),
    "gong_secret": ("GONG_ACCESS_SECRET", "Gong API Key"),
    "gong_key": ("GONG_ACCESS_KEY", "Access Key ID"),
    "base44": ("BASE44_TOKEN", "api_key"),
}


def get(name):
    var, label = SECRETS[name]
    val = os.environ.get(var)
    if val:
        return val.strip().strip('"').strip("'")
    env_file = os.environ.get("CH_ENV_FILE", LEGACY_ENV_FILE)
    if os.path.exists(env_file):
        with open(env_file, encoding="utf-8") as f:
            for line in f:
                if line.startswith(label + ":"):
                    return line.split(":", 1)[1].strip().strip('"').strip("'")
    raise SystemExit(f"missing credential '{name}': set {var} or add '{label}: ...' to {env_file}")


if __name__ == "__main__":
    name, out = sys.argv[1], sys.argv[2]
    with open(out, "w") as f:
        f.write(get(name))
    print(f"wrote {name} credential to {out} ({os.path.getsize(out)} chars)")
