#!/usr/bin/env python3
"""Repository safety and structure guards for ansible-infrastructure-automation-lab.

Callable from CLI (`python scripts/validate-repository.py`) and imported by pytest.
Checks secrets, private keys, unsafe patterns, inventory hygiene, collection layout,
idempotence guards, and CI soft-guards without touching real infrastructure.
"""

from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable

try:
    import yaml
except ImportError:  # pragma: no cover - exercised when PyYAML missing
    yaml = None  # type: ignore[assignment]

ROOT = Path(__file__).resolve().parents[1]

SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    ".ansible",
    ".molecule",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    "__pycache__",
    "reports",
    "artifacts",
    "results",
    "output",
    "temp",
    "tmp",
    "dist",
    "build",
    "node_modules",
    # Test sources intentionally embed detector needles (keys, gmail, vault markers).
    "tests",
}

SKIP_SUFFIXES = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".pyc",
    ".whl",
    ".tar",
    ".gz",
    ".zip",
    ".ico",
}

EXPECTED_NAMESPACE = "salvomazzaglia"
EXPECTED_COLLECTION_NAME = "infrastructure_automation"
EXPECTED_VERSION = "1.0.0"

EXPECTED_ROLES = (
    "accounts",
    "automatic_updates",
    "common",
    "firewall_policy",
    "logging",
    "package_management",
    "service_health",
    "ssh_hardening",
    "time_sync",
    "web_service",
)

EXPECTED_PLAYBOOKS = (
    "baseline.yml",
    "check.yml",
    "drift.yml",
    "health.yml",
    "security.yml",
    "site.yml",
    "web.yml",
)

STATE_CHANGING_PLAYBOOKS = (
    "baseline.yml",
    "security.yml",
    "site.yml",
    "web.yml",
)

EXPECTED_INVENTORY_GROUPS = (
    "bastion",
    "web",
    "application",
    "app",
    "database",
    "monitoring",
)

EXPECTED_HOSTS = (
    "ansible-bastion-01.lab.example.invalid",
    "ansible-web-01.lab.example.invalid",
    "ansible-web-02.lab.example.invalid",
    "ansible-app-01.lab.example.invalid",
    "ansible-db-01.lab.example.invalid",
    "ansible-monitor-01.lab.example.invalid",
)

ALLOWED_ENVIRONMENTS = frozenset({"synthetic", "lab", "authorized", "molecule"})

FIREWALL_PROTOCOLS = frozenset({"tcp", "udp", "icmp"})

REAL_DOMAIN_DENYLIST = (
    "gmail.com",
    "google.com",
    "company.com",
    "corp.com",
    "microsoft.com",
    "amazon.com",
    "aws.amazon.com",
    "github.com",  # hostnames only — docs may mention GitHub URLs; inventory hosts checked separately
)

RFC1918 = [
    re.compile(r"\b10\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"),
    re.compile(r"\b192\.168\.\d{1,3}\.\d{1,3}\b"),
    re.compile(r"\b172\.(1[6-9]|2\d|3[0-1])\.\d{1,3}\.\d{1,3}\b"),
]

# Public documentation / TEST-NET ranges are OK in docs explaining examples.
TEST_NET_OK = [
    re.compile(r"\b192\.0\.2\.\d{1,3}\b"),
    re.compile(r"\b198\.51\.100\.\d{1,3}\b"),
    re.compile(r"\b203\.0\.113\.\d{1,3}\b"),
]

PRIVATE_KEY = re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |DSA |ED25519 )?PRIVATE KEY-----")
# Split markers so this source file does not match its own detectors.
VAULT_BLOB = re.compile(r"\$" + r"ANSIBLE_VAULT;")
GMAIL = re.compile(r"@" + r"gmail\.com\b", re.IGNORECASE)
CURL_BASH = re.compile(r"curl\s+[^\n|]*\|\s*(?:ba)?sh", re.IGNORECASE)
WGET_BASH = re.compile(r"wget\s+[^\n|]*\|\s*(?:ba)?sh", re.IGNORECASE)
CHMOD_777 = re.compile(r"chmod\s+(?:-R\s+)?(?:0?777|a\+rwx)\b")
STATE_LATEST = re.compile(r"^\s*state:\s*['\"]?latest['\"]?\s*$", re.MULTILINE | re.IGNORECASE)
HOST_KEY_FALSE = re.compile(r"host_key_checking\s*=\s*False", re.IGNORECASE)
RANDOM_FILTER = re.compile(r"\{\{[^}]*\brandom\s*\(")
CHANGED_WHEN_FALSE = re.compile(r"^\s*changed_when:\s*false\s*$", re.MULTILINE | re.IGNORECASE)
PASSWORD_ASSIGN = re.compile(
    r"(?i)(?:password|passwd|secret|token|api_key)\s*[:=]\s*['\"]([^'\"]{8,})['\"]"
)
IPV4 = re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d?\d)\b")
ACTION_SHA = re.compile(r"uses:\s*[^\s@]+@([0-9a-f]{40})\b", re.IGNORECASE)
ACTION_UNPINNED = re.compile(r"uses:\s*[^\s@]+@(?:v?\d|main|master|latest)\b", re.IGNORECASE)

PORT_OPTION_HINTS = ("port", "listen_port", "ssh_port", "remote_port")


# --------------------------------------------------------------------------- paths
def iter_text_files(root: Path | None = None) -> list[Path]:
    base = root or ROOT
    files: list[Path] = []
    for path in base.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix.lower() in SKIP_SUFFIXES:
            continue
        files.append(path)
    return files


def rel(path: Path, root: Path | None = None) -> str:
    base = root or ROOT
    return path.relative_to(base).as_posix()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_yaml(path: Path) -> Any:
    if yaml is None:
        raise RuntimeError("PyYAML is required")
    return yaml.safe_load(read_text(path))


# --------------------------------------------------------------------------- schema helpers (argument_specs)
def load_argument_specs(role: str, root: Path | None = None) -> dict[str, Any]:
    base = root or ROOT
    path = base / "roles" / role / "meta" / "argument_specs.yml"
    data = load_yaml(path)
    if not isinstance(data, dict) or "argument_specs" not in data:
        raise ValueError(f"invalid argument_specs for role {role}")
    return data["argument_specs"]


def iter_option_specs(
    specs: dict[str, Any],
    prefix: str = "",
) -> Iterable[tuple[str, dict[str, Any]]]:
    main = specs.get("main") or {}
    options = main.get("options") or {}
    for name, option in options.items():
        if not isinstance(option, dict):
            continue
        full = f"{prefix}{name}" if not prefix else f"{prefix}.{name}"
        yield full, option
        nested = option.get("options")
        if isinstance(nested, dict):
            for nested_name, nested_opt in nested.items():
                if isinstance(nested_opt, dict):
                    yield f"{full}.{nested_name}", nested_opt


def is_port_option(name: str) -> bool:
    lower = name.lower().rsplit(".", 1)[-1]
    return any(hint in lower for hint in PORT_OPTION_HINTS)


def validate_port(value: Any) -> bool:
    """Return True when value is a valid TCP/UDP port (1-65535)."""
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return 1 <= value <= 65535
    if isinstance(value, str) and value.isdigit():
        return 1 <= int(value) <= 65535
    return False


def validate_firewall_protocol(value: Any, allowed: Iterable[str] | None = None) -> bool:
    choices = frozenset(allowed) if allowed is not None else FIREWALL_PROTOCOLS
    return isinstance(value, str) and value.lower() in {c.lower() for c in choices}


def validate_environment(value: Any) -> bool:
    return isinstance(value, str) and value in ALLOWED_ENVIRONMENTS


def option_accepts_value(option: dict[str, Any], value: Any) -> bool:
    """Lightweight schema check mirroring Ansible argument_specs constraints."""
    opt_type = str(option.get("type", "str")).lower()
    choices = option.get("choices")

    if choices is not None:
        if value not in choices:
            return False

    if opt_type == "bool":
        return isinstance(value, bool)
    if opt_type == "int":
        if isinstance(value, bool) or not isinstance(value, int):
            # also allow digit strings for port-like inputs in our lab validators
            if isinstance(value, str) and value.lstrip("-").isdigit():
                return True
            return False
        return True
    if opt_type == "str":
        return isinstance(value, str)
    if opt_type == "list":
        return isinstance(value, list)
    if opt_type == "dict":
        return isinstance(value, dict)
    if opt_type == "float":
        return isinstance(value, float) and not isinstance(value, bool)
    return True


def port_option_accepts(option: dict[str, Any], value: Any) -> bool:
    if not option_accepts_value(option, value):
        # Still reject out-of-range ints even when type matches
        pass
    if not isinstance(value, int) or isinstance(value, bool):
        if isinstance(value, str) and value.lstrip("-").isdigit():
            value = int(value)
        else:
            return False
    if not validate_port(value):
        return False
    return option_accepts_value(option, value) if option.get("choices") else True


def find_firewall_protocol_option(root: Path | None = None) -> dict[str, Any]:
    specs = load_argument_specs("firewall_policy", root=root)
    for name, option in iter_option_specs(specs):
        if name.endswith("protocol") or name.split(".")[-1] == "protocol":
            return option
    raise KeyError("firewall protocol option not found")


def find_port_options(root: Path | None = None) -> list[tuple[str, str, dict[str, Any]]]:
    """Return list of (role, option_name, option_spec) for port-like ints."""
    found: list[tuple[str, str, dict[str, Any]]] = []
    for role in EXPECTED_ROLES:
        specs = load_argument_specs(role, root=root)
        for name, option in iter_option_specs(specs):
            if is_port_option(name) and str(option.get("type", "")).lower() == "int":
                found.append((role, name, option))
    return found


# --------------------------------------------------------------------------- inventory
def inventory_host_names(data: Any) -> list[str]:
    hosts: list[str] = []

    def walk(node: Any) -> None:
        if not isinstance(node, dict):
            return
        h = node.get("hosts")
        if isinstance(h, dict):
            hosts.extend(str(k) for k in h.keys())
        children = node.get("children")
        if isinstance(children, dict):
            for child in children.values():
                walk(child)

    if isinstance(data, dict):
        walk(data.get("all") or data)
    return hosts


def inventory_group_names(data: Any) -> set[str]:
    groups: set[str] = set()

    def walk(node: Any, name: str | None = None) -> None:
        if not isinstance(node, dict):
            return
        if name:
            groups.add(name)
        children = node.get("children")
        if isinstance(children, dict):
            for child_name, child in children.items():
                walk(child, str(child_name))

    if isinstance(data, dict):
        walk(data.get("all") or data, "all")
    return groups


def inventory_text_blob(root: Path | None = None) -> str:
    base = root or ROOT
    inv = base / "inventories"
    parts: list[str] = []
    for path in inv.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".yml", ".yaml"}:
            parts.append(read_text(path))
    return "\n".join(parts)


# --------------------------------------------------------------------------- scanners
def scan_matches(pattern: re.Pattern[str], root: Path | None = None) -> list[str]:
    hits: list[str] = []
    for path in iter_text_files(root):
        try:
            text = read_text(path)
        except (OSError, UnicodeDecodeError):
            continue
        if pattern.search(text):
            hits.append(rel(path, root))
    return hits


def scan_state_latest(root: Path | None = None) -> list[str]:
    """Flag state: latest outside documented comments / README exceptions."""
    hits: list[str] = []
    base = root or ROOT
    allowed_suffix_docs = {".md"}
    for path in iter_text_files(base):
        if path.suffix.lower() in allowed_suffix_docs:
            continue
        # package_management docs in defaults comments are OK if they say NEVER
        try:
            text = read_text(path)
        except (OSError, UnicodeDecodeError):
            continue
        for match in STATE_LATEST.finditer(text):
            # Allow lines that are only in comments explaining prohibition
            line_start = text.rfind("\n", 0, match.start()) + 1
            line = text[line_start : text.find("\n", match.start())]
            stripped = line.lstrip()
            if stripped.startswith("#"):
                continue
            hits.append(f"{rel(path, base)}:{line.strip()}")
    return hits


def scan_changed_when_false_abuse(root: Path | None = None) -> list[str]:
    """Flag changed_when: false without a nearby justification comment."""
    hits: list[str] = []
    base = root or ROOT
    for path in iter_text_files(base):
        if path.suffix.lower() not in {".yml", ".yaml"}:
            continue
        try:
            text = read_text(path)
        except (OSError, UnicodeDecodeError):
            continue
        lines = text.splitlines()
        for idx, line in enumerate(lines):
            if not CHANGED_WHEN_FALSE.match(line):
                continue
            window = lines[max(0, idx - 3) : idx + 1]
            justified = any(
                re.search(r"(?i)justif|idempoten|read-only|no change|intentional", w)
                and w.lstrip().startswith("#")
                for w in window
            )
            if not justified:
                hits.append(f"{rel(path, base)}:{idx + 1}")
    return hits


def scan_random_filters(root: Path | None = None) -> list[str]:
    hits: list[str] = []
    base = root or ROOT
    for path in (base / "roles").rglob("*.j2"):
        try:
            text = read_text(path)
        except (OSError, UnicodeDecodeError):
            continue
        if RANDOM_FILTER.search(text):
            hits.append(rel(path, base))
    return hits


def is_rfc1918_ip(ip: str) -> bool:
    for pattern in RFC1918:
        if pattern.fullmatch(ip) or pattern.search(ip):
            # fullmatch on whole string
            if re.fullmatch(pattern.pattern, ip):
                return True
            if pattern.search(ip) and ip == pattern.search(ip).group(0):  # type: ignore[union-attr]
                return True
    # Direct parse
    parts = ip.split(".")
    if len(parts) != 4:
        return False
    try:
        nums = [int(p) for p in parts]
    except ValueError:
        return False
    if nums[0] == 10:
        return True
    if nums[0] == 192 and nums[1] == 168:
        return True
    if nums[0] == 172 and 16 <= nums[1] <= 31:
        return True
    return False


def is_test_net_ip(ip: str) -> bool:
    return any(p.search(ip) for p in TEST_NET_OK)


def extract_ipv4s(text: str) -> list[str]:
    return IPV4.findall(text)


def check_ci_workflow(root: Path | None = None) -> list[str]:
    """Soft-guard CI when present. Returns errors (empty if CI absent)."""
    base = root or ROOT
    errors: list[str] = []
    workflows = list((base / ".github" / "workflows").glob("*.yml")) + list(
        (base / ".github" / "workflows").glob("*.yaml")
    )
    if not workflows:
        return errors
    for wf in workflows:
        text = read_text(wf)
        r = rel(wf, base)
        if "self-hosted" in text:
            errors.append(f"self-hosted runner in {r}")
        if "pull_request_target" in text:
            errors.append(f"pull_request_target in {r}")
        if ACTION_UNPINNED.search(text) and not ACTION_SHA.search(text):
            # Require at least some SHA pins when actions are used
            if re.search(r"uses:\s*", text):
                unpinned = ACTION_UNPINNED.findall(text)
                if unpinned:
                    errors.append(f"unpinned actions in {r}: {unpinned}")
        # Every uses: line should prefer 40-char SHA
        for line in text.splitlines():
            if "uses:" not in line or line.strip().startswith("#"):
                continue
            m = re.search(r"uses:\s*(\S+)", line)
            if not m:
                continue
            ref = m.group(1)
            if "@" not in ref:
                continue
            _, ver = ref.rsplit("@", 1)
            if not re.fullmatch(r"[0-9a-f]{40}", ver):
                errors.append(f"action not pinned to 40-char SHA in {r}: {ref}")
    return errors


# --------------------------------------------------------------------------- aggregate checks
def check_collection_layout(root: Path | None = None) -> list[str]:
    base = root or ROOT
    errors: list[str] = []
    galaxy_path = base / "galaxy.yml"
    if not galaxy_path.is_file():
        return ["missing galaxy.yml"]
    galaxy = load_yaml(galaxy_path)
    if galaxy.get("namespace") != EXPECTED_NAMESPACE:
        errors.append(f"galaxy namespace expected {EXPECTED_NAMESPACE}")
    if galaxy.get("name") != EXPECTED_COLLECTION_NAME:
        errors.append(f"galaxy name expected {EXPECTED_COLLECTION_NAME}")
    if str(galaxy.get("version")) != EXPECTED_VERSION:
        errors.append(f"galaxy version expected {EXPECTED_VERSION}")

    runtime = base / "meta" / "runtime.yml"
    if not runtime.is_file():
        errors.append("missing meta/runtime.yml")
    else:
        data = load_yaml(runtime)
        if "requires_ansible" not in (data or {}):
            errors.append("runtime.yml missing requires_ansible")

    for role in EXPECTED_ROLES:
        role_dir = base / "roles" / role
        if not role_dir.is_dir():
            errors.append(f"missing role {role}")
            continue
        for req in (
            "tasks/main.yml",
            "defaults/main.yml",
            "meta/main.yml",
            "meta/argument_specs.yml",
        ):
            if not (role_dir / req).is_file():
                errors.append(f"role {role} missing {req}")

    for pb in EXPECTED_PLAYBOOKS:
        if not (base / "playbooks" / pb).is_file():
            errors.append(f"missing playbook {pb}")

    for needed in (
        "plugins/callback/automation_report.py",
        "inventories/synthetic/hosts.yml",
        "playbooks/tasks/preflight.yml",
    ):
        if not (base / needed).is_file():
            errors.append(f"missing {needed}")
    return errors


def check_secrets_and_keys(root: Path | None = None) -> list[str]:
    base = root or ROOT
    errors: list[str] = []
    vault_password_globs = (
        "**/vault-password*",
        "**/.vault-password*",
        "**/*.vault-password",
    )
    for pattern in vault_password_globs:
        for path in base.glob(pattern):
            if path.is_file() and ".git" not in path.parts:
                errors.append(f"vault password file tracked: {rel(path, base)}")

    for path in iter_text_files(base):
        r = rel(path, base)
        try:
            text = read_text(path)
        except (OSError, UnicodeDecodeError):
            continue
        if PRIVATE_KEY.search(text):
            errors.append(f"private key material in {r}")
        if VAULT_BLOB.search(text) and "vault.example" not in r:
            errors.append(f"ansible-vault blob in {r}")
        if GMAIL.search(text):
            errors.append(f"gmail address in {r}")

        if r == "examples/vault.example.yml":
            if "CHANGE_ME_WITH_ANSIBLE_VAULT" not in text:
                errors.append("vault.example.yml missing placeholders")
            for match in PASSWORD_ASSIGN.finditer(text):
                val = match.group(1)
                if not val.startswith("CHANGE_ME"):
                    errors.append(f"vault.example.yml non-placeholder secret: {val[:12]}...")
    return errors


def check_dangerous_shell_patterns(root: Path | None = None) -> list[str]:
    errors: list[str] = []
    for path in iter_text_files(root):
        r = rel(path, root)
        # Skip this validator itself when documenting patterns via separate constants
        try:
            text = read_text(path)
        except (OSError, UnicodeDecodeError):
            continue
        if CURL_BASH.search(text):
            errors.append(f"curl|bash pattern in {r}")
        if WGET_BASH.search(text):
            errors.append(f"wget|bash pattern in {r}")
        if CHMOD_777.search(text) and path.suffix.lower() in {".yml", ".yaml", ".sh", ".j2"}:
            errors.append(f"chmod 777 in {r}")
    return errors


def check_ssh_secure_defaults(root: Path | None = None) -> list[str]:
    base = root or ROOT
    errors: list[str] = []
    defaults = base / "roles" / "ssh_hardening" / "defaults" / "main.yml"
    if not defaults.is_file():
        return ["missing ssh_hardening defaults"]
    text = read_text(defaults)
    data = load_yaml(defaults) or {}
    if data.get("aial_ssh_permit_root_login") == "yes":
        errors.append("PermitRootLogin yes as default")
    if data.get("aial_ssh_password_authentication") is True:
        errors.append("PasswordAuthentication yes as secure default")
    if re.search(r"(?i)permitrootlogin\s+yes", text) and not text.strip().startswith("#"):
        # defaults YAML uses ansible vars not sshd keywords; still guard
        if "aial_ssh_permit_root_login: yes" in text:
            errors.append("aial_ssh_permit_root_login: yes in defaults")
    return errors


def check_ansible_cfg(root: Path | None = None) -> list[str]:
    base = root or ROOT
    errors: list[str] = []
    cfg = base / "ansible.cfg"
    if not cfg.is_file():
        return ["missing ansible.cfg"]
    text = read_text(cfg)
    if HOST_KEY_FALSE.search(text):
        errors.append("host_key_checking = False in ansible.cfg")
    return errors


def check_inventory_guards(root: Path | None = None) -> list[str]:
    base = root or ROOT
    errors: list[str] = []
    hosts_path = base / "inventories" / "synthetic" / "hosts.yml"
    if not hosts_path.is_file():
        return ["missing synthetic hosts.yml"]
    data = load_yaml(hosts_path)
    names = inventory_host_names(data)
    if len(names) != 6:
        errors.append(f"expected 6 hosts, found {len(names)}")
    for host in EXPECTED_HOSTS:
        if host not in names:
            errors.append(f"missing host {host}")
    for host in names:
        if not (
            host.endswith(".lab.example.invalid") or host.endswith(".example.invalid")
        ):
            errors.append(f"host not .example.invalid: {host}")
        if host in {"localhost", "127.0.0.1"}:
            errors.append("localhost in inventory")

    blob = inventory_text_blob(base)
    if re.search(r"(?m)^\s*ansible_host\s*:", blob):
        errors.append("ansible_host present in inventory")
    if re.search(r"(?i)\blocalhost\b", blob) and "molecule" not in blob.lower():
        # comments mentioning localhost prohibition are OK
        for line in blob.splitlines():
            if re.search(r"(?i)\blocalhost\b", line) and not line.lstrip().startswith("#"):
                errors.append("localhost reference in inventory data")
                break
    for pattern in RFC1918:
        if pattern.search(blob):
            errors.append("RFC1918 literal in inventory")
            break

    all_vars = load_yaml(base / "inventories" / "synthetic" / "group_vars" / "all.yml") or {}
    if all_vars.get("aial_environment") != "synthetic":
        errors.append("aial_environment must be synthetic")
    if all_vars.get("aial_safe_to_apply") is not False:
        errors.append("aial_safe_to_apply must be false")
    return errors


def check_callback_contract(root: Path | None = None) -> list[str]:
    base = root or ROOT
    errors: list[str] = []
    callback = base / "plugins" / "callback" / "automation_report.py"
    if not callback.is_file():
        return ["missing plugins/callback/automation_report.py"]
    src = read_text(callback)
    for needle in ("REDACTED", "no_log", "AIAL_REPORT_DIR", "CALLBACK_NEEDS_ENABLED", "_sanitize_value"):
        if needle not in src:
            errors.append(f"callback missing {needle}")
    return errors


def check_gitignore(root: Path | None = None) -> list[str]:
    base = root or ROOT
    errors: list[str] = []
    gitignore = base / ".gitignore"
    if not gitignore.is_file():
        return ["missing .gitignore"]
    gi = read_text(gitignore)
    for needle in ("reports/", "*.retry", "vault-password", ".venv/"):
        if needle not in gi:
            errors.append(f".gitignore missing {needle}")
    return errors


def check_retry_files(root: Path | None = None) -> list[str]:
    base = root or ROOT
    errors: list[str] = []
    for path in base.rglob("*.retry"):
        if ".git" in path.parts:
            continue
        errors.append(f"retry file present: {rel(path, base)}")
    return errors


def check_fqcn_preference(root: Path | None = None) -> list[str]:
    """Flag bare Ansible module invocations in playbooks/roles tasks.

    Only task-level module keys are considered (same indent as a nearby ``name:``).
    Parameter keys such as ``shell:`` / ``command:`` under modules are ignored.
    """
    base = root or ROOT
    # Modules rarely used as nested parameter names — avoids false positives.
    module_names = (
        "apt",
        "yum",
        "dnf",
        "template",
        "copy",
        "service",
        "systemd",
        "set_fact",
        "debug",
        "assert",
        "fail",
        "include_tasks",
        "import_tasks",
        "include_role",
        "import_role",
        "package",
        "uri",
        "wait_for",
        "stat",
        "lineinfile",
        "blockinfile",
        "get_url",
        "apt_key",
        "apt_repository",
        "user",
        "group",
    )
    bare_line = re.compile(
        r"(?m)^(?P<indent>\s*)(?P<mod>" + "|".join(module_names) + r")\s*:\s*$"
    )
    name_line = re.compile(r"^(?P<indent>\s*)name\s*:")
    errors: list[str] = []
    paths = list((base / "playbooks").rglob("*.yml")) + list(
        (base / "roles").rglob("tasks/*.yml")
    )
    for path in paths:
        lines = read_text(path).splitlines()
        name_indents: set[int] = set()
        for line in lines:
            m = name_line.match(line)
            if m:
                name_indents.add(len(m.group("indent")))
        for line in lines:
            m = bare_line.match(line)
            if not m:
                continue
            indent = len(m.group("indent"))
            # Task keys sit at the same indent as ``name:``; params are deeper.
            if indent in name_indents:
                errors.append(f"bare module '{m.group('mod')}' in {rel(path, base)}")
    return errors


def run_all_checks(root: Path | None = None) -> list[str]:
    errors: list[str] = []
    errors.extend(check_gitignore(root))
    errors.extend(check_collection_layout(root))
    errors.extend(check_secrets_and_keys(root))
    errors.extend(check_dangerous_shell_patterns(root))
    errors.extend(check_ssh_secure_defaults(root))
    errors.extend(check_ansible_cfg(root))
    errors.extend(check_inventory_guards(root))
    errors.extend(check_callback_contract(root))
    errors.extend(check_retry_files(root))
    errors.extend(check_ci_workflow(root))

    for hit in scan_state_latest(root):
        errors.append(f"state: latest -> {hit}")
    for hit in scan_random_filters(root):
        errors.append(f"random filter in template {hit}")
    for hit in scan_changed_when_false_abuse(root):
        errors.append(f"changed_when: false without justification at {hit}")
    for hit in check_fqcn_preference(root):
        errors.append(hit)

    # RFC1918 in inventories / examples / playbooks / roles (docs may explain TEST-NET)
    base = root or ROOT
    for path in iter_text_files(base):
        if not any(p in path.parts for p in ("inventories", "examples", "playbooks", "roles")):
            continue
        try:
            text = read_text(path)
        except (OSError, UnicodeDecodeError):
            continue
        for pattern in RFC1918:
            if pattern.search(text):
                errors.append(f"RFC1918 literal in {rel(path, base)}")
                break
    return sorted(set(errors))


def main() -> int:
    errors = run_all_checks()
    if errors:
        print("REPOSITORY GUARD FAILURES:")
        for err in errors:
            print(f" - {err}")
        return 1
    print("Repository safety guards PASSED")
    print(f" Checked roles={len(EXPECTED_ROLES)} playbooks={len(EXPECTED_PLAYBOOKS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
