"""Load configs_local.ini for the receiving_pacs008 service.

Every module that needs URLs, XPaths, cert paths, or amount limits goes
through ConfigsParser.parser(section). Values are read at import time, so
changing the INI requires a process restart (or a new Gunicorn worker).

Search order (first existing file wins):
  1. APP_CONFIG_FILE or CONFIG_FILE environment variable
  2. ./configs/configs_local.ini          (cwd — container workdir /app)
  3. ../configs/configs_local.ini         (local runs from app/)
  4. /app/configs/configs_local.ini       (explicit container path)

Sections this service actually uses:
  [APP]        logging_level
  [REQUEST]    IPS + signing URLs/timeouts, inbound pacs.008 XPaths/namespaces
  [RESPONSE]   outbound pacs.002 / admi.002 XML namespace
  [SIGNATURE]  mTLS key/cert/CA paths for the IPS POST
  [AMOUNT]     sandbox lowest_amount / highest_amount
  [DB-SERVICE] reserved; not on the live sandbox path yet

Docker Compose mounts ./configs to /app/configs. If parser returns {}, check
logs for "ConfigsParser error" — missing file or unknown section name.

Do not commit secrets in the INI; point [SIGNATURE] at mounted key files.
"""

import configparser
import os
from pathlib import Path

class ConfigsParser():
    """Reads one INI section into a plain dict of string key/value pairs.

    CONFIG_DEV / CONFIG_PROD are unused placeholders kept for compatibility
    with other A2A services that share this parser pattern.
    """
    #declaration
    CONFIG_DEV=None
    CONFIG_PROD=None

    @staticmethod
    def parser(section='DATABASE'):
        """Return dict(configs.items(section)) from the resolved configs_local.ini.

        Args:
            section: INI section name. For this service use 'APP', 'REQUEST',
                'RESPONSE', 'SIGNATURE', 'AMOUNT', or 'DB-SERVICE'.
                Default 'DATABASE' is a shared-parser leftover; do not rely on it here.

        Returns:
            dict of string values on success.
            {} on any error (file missing, section missing, parse failure).
            Callers that do ConfigsParser().parser('X')['key'] will then KeyError —
            check logs for "ConfigsParser error" first.

        Example:
            >>> request_cfg = ConfigsParser().parser('REQUEST')
            >>> request_cfg['payment_status_report_url']
        """
        try:
            # Resolve configs_local.ini. Order matches the module docstring.
            cwd_path = Path(os.getcwd())
            candidates = [
                cwd_path / "configs" / "configs_local.ini",              # /app/configs/configs_local.ini (container default)
                cwd_path.parent / "configs" / "configs_local.ini",       # ../configs/configs_local.ini (local runs from app/)
                Path("/app/configs/configs_local.ini"),                  # explicit container path
            ]

            # Helm/Compose can point at a different mount via APP_CONFIG_FILE or CONFIG_FILE.
            env_path = os.environ.get("APP_CONFIG_FILE") or os.environ.get("CONFIG_FILE")
            if env_path:
                candidates.insert(0, Path(env_path))

            config_path = None
            for p in candidates:
                if p and Path(p).is_file():
                    config_path = str(p)
                    break

            #print("Resolved config path:", config_path)

            # Initialize and read
            configs = configparser.ConfigParser()
            if not config_path:
                raise RuntimeError("configs_local.ini not found in expected locations: " + ", ".join([str(p) for p in candidates]))

            files = configs.read(config_path)
            if not files:
                raise RuntimeError(f"configparser failed to read: {config_path}")

            # Read the items in the given section
            if not configs.has_section(section):
                raise RuntimeError(f"Section '{section}' not found in {config_path}")

            config_dict = dict(configs.items(section))
            return config_dict
        except Exception as e:
            print("ConfigsParser error:", e)
            return {}
