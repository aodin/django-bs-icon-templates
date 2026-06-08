import io
import json
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError


GITHUB_API_LATEST = "https://api.github.com/repos/twbs/icons/releases/latest"

# Register so ElementTree serialises back to clean `<svg xmlns="...">` not `<ns0:svg ...>`
ET.register_namespace("", "http://www.w3.org/2000/svg")
ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")


def _process_svg(content: str) -> str:
    """Remove width attribute and replace height value with a Django template variable."""
    root = ET.fromstring(content)
    root.attrib.pop("width", None)
    root.attrib["height"] = "{{ height|default:16 }}"
    return ET.tostring(root, encoding="unicode")


class Command(BaseCommand):
    help = "Download and pre-process Bootstrap Icons SVGs into Django templates."

    def add_arguments(self, parser):
        parser.add_argument(
            "--version",
            default=None,
            help="Bootstrap Icons release tag to download (e.g. v1.13.1). Defaults to latest.",
        )
        parser.add_argument(
            "--output-dir",
            default=None,
            help=(
                "Directory to write processed SVG templates. "
                "Defaults to the templates/bs_icon/ "
                "directory inside this app."
            ),
        )

    def handle(self, *args, **options):
        output_dir = self._resolve_output_dir(options["output_dir"])
        output_dir.mkdir(parents=True, exist_ok=True)

        version = options["version"]
        zip_url, resolved_version = self._resolve_release(version)

        self.stdout.write(f"Downloading Bootstrap Icons {resolved_version}...")
        zip_bytes = self._fetch(zip_url)

        self.stdout.write("Processing SVG files...")
        count = self._extract_and_process(zip_bytes, output_dir)

        self.stdout.write(
            self.style.SUCCESS(f"Done. {count} icons written to {output_dir}")
        )

    def _resolve_output_dir(self, raw: str | None) -> Path:
        if raw:
            return Path(raw)
        app_dir = Path(__file__).resolve().parent.parent.parent
        return app_dir / "templates" / "bs_icon"

    def _resolve_release(self, version: str | None) -> tuple[str, str]:
        if version:
            tag = version if version.startswith("v") else f"v{version}"
            zip_url = f"https://github.com/twbs/icons/archive/refs/tags/{tag}.zip"
            return zip_url, tag

        self.stdout.write("Fetching latest release info from GitHub...")
        data = json.loads(self._fetch(GITHUB_API_LATEST))
        tag = data["tag_name"]
        zip_url = data["zipball_url"]
        return zip_url, tag

    def _fetch(self, url: str) -> bytes:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "django-bs-icon-templates/0.1"},
        )
        try:
            with urllib.request.urlopen(req) as resp:
                return resp.read()
        except Exception as exc:
            raise CommandError(f"Failed to fetch {url}: {exc}") from exc

    def _extract_and_process(self, zip_bytes: bytes, output_dir: Path) -> int:
        count = 0
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
            for entry in zf.infolist():
                # Icons live at <root>/icons/*.svg inside the archive
                parts = Path(entry.filename).parts
                if (
                    len(parts) == 3
                    and parts[1] == "icons"
                    and parts[2].endswith(".svg")
                ):
                    raw = zf.read(entry.filename).decode("utf-8")
                    processed = _process_svg(raw)
                    dest = output_dir / parts[2]
                    dest.write_text(processed, encoding="utf-8")
                    count += 1
        return count
