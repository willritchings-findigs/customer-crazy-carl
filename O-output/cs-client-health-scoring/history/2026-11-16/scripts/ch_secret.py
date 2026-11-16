"""Resolve a credential without ever printing it to logs.

Order: network secret (cloud proxy) -> environment variable -> local .env file (Label: value).

Network secrets: the cloud environment's proxy adds the Authorization header to requests for
the secret's hosts, so the key never enters the session. List the services handled that way in
CH_PROXY_AUTH (comma-separated: hubspot, gong, base44). For those, auth_headers() returns no
Authorization header and Base44 curl calls send none.
Usage as a script writes the value to a file, never stdout:
  python3 ch_secret.py base44 <out_file>
  python3 ch_secret.py --check     # which source each credential resolves from; never values
"""
import base64, os, sys

LEGACY_ENV_FILE = "C:/Users/Will Ritchings/Desktop/Claude/GTM_ENG/The Reserve/T-tools/API Keys and Access/.env"

# name -> (environment variable, .env label prefix)
SECRETS = {
    "hubspot": ("HUBSPOT_TOKEN", "HubSpot API Service Key"),
    "gong_secret": ("GONG_ACCESS_SECRET", "Gong API Key"),
    "gong_key": ("GONG_ACCESS_KEY", "Access Key ID"),
    "base44": ("BASE44_TOKEN", "api_key"),
}


# service -> credentials it needs
SERVICES = {"hubspot": ["hubspot"], "gong": ["gong_key", "gong_secret"], "base44": ["base44"]}


def proxied(service):
    return service in {s.strip() for s in os.environ.get("CH_PROXY_AUTH", "").split(",") if s.strip()}


def service_of(name):
    return next(s for s, names in SERVICES.items() if name in names)


def auth_headers(service):
    """Authorization header for a service, or {} when the cloud proxy injects it."""
    if proxied(service):
        return {}
    if service == "gong":
        tok = base64.b64encode(f"{get('gong_key')}:{get('gong_secret')}".encode()).decode()
        return {"Authorization": "Basic " + tok}
    return {"Authorization": "Bearer " + get(service)}


def resolve(name):
    """(value, source) or (None, None). source is 'env:<VAR>' or 'file'."""
    var, label = SECRETS[name]
    val = os.environ.get(var)
    if val and val.strip():
        return val.strip().strip('"').strip("'"), "env:" + var
    env_file = os.environ.get("CH_ENV_FILE", LEGACY_ENV_FILE)
    if os.path.exists(env_file):
        with open(env_file, encoding="utf-8") as f:
            for line in f:
                if line.startswith(label + ":"):
                    v = line.split(":", 1)[1].strip().strip('"').strip("'")
                    if v:
                        return v, "file"
    return None, None


def get(name):
    val, _ = resolve(name)
    if val is None:
        var, label = SECRETS[name]
        env_file = os.environ.get("CH_ENV_FILE", LEGACY_ENV_FILE)
        raise SystemExit(f"missing credential '{name}': set {var} or add '{label}: ...' to {env_file}")
    return val


def check():
    """Return a list of (name, source-or-None). Never touches stdout with a value."""
    return [(n, "proxy (network secret)" if proxied(service_of(n)) else resolve(n)[1]) for n in SECRETS]


if __name__ == "__main__":
    if sys.argv[1:] == ["--check"]:
        rows = check()
        for n, src in rows:
            print(f"{'PASS' if src else 'FAIL'} credential {n}: {src or 'missing (set ' + SECRETS[n][0] + ')'}")
        sys.exit(0 if all(src for _, src in rows) else 1)
    name, out = sys.argv[1], sys.argv[2]
    if proxied(service_of(name)):
        raise SystemExit(f"{name} is a network secret (CH_PROXY_AUTH); send no Authorization header")
    with open(out, "w") as f:
        f.write(get(name))
    print(f"wrote {name} credential to {out} ({os.path.getsize(out)} chars)")
