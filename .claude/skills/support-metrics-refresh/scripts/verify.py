"""Prove saved Sigma results match Sigma (the shared fingerprint check, for this skill).

Usage: python3 verify.py {checks|compare|probes} --run-date YYYY-MM-DD --scratch <dir> [--only a,b]
Same steps as client-health-refresh: save every query result, run `checks`, send each
<name>_<MMDD>_check.sql to Sigma and save its one-row result as <name>_<MMDD>_check.json, then
`compare` must PASS every query. `probes` writes LIMIT 0 column probes for the pre-flight.
"""
import sm_common  # sets CX_SKILL_DIR first
import sigma_verify as sv

if __name__ == "__main__":
    run, ns = sm_common.get_run("Verify saved Sigma results", [
        (("mode",), {"choices": ["checks", "compare", "probes"]}),
        (("--only",), {"default": "", "help": "comma-separated query names"})])
    sv.ONLY = [x for x in ns.only.split(",") if x]
    {"checks": sv.cmd_checks, "compare": sv.cmd_compare, "probes": sv.cmd_probes}[ns.mode](run)
