import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = (
        "Copy processed Bootstrap Icon templates from this app into another "
        "directory (e.g. your project's templates/bs_icon/)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "names",
            nargs="+",
            metavar="ICON",
            help="Icon names to copy (with or without the .svg suffix), e.g. alarm gear.",
        )
        parser.add_argument(
            "--source-dir",
            default=None,
            help=(
                "Directory to copy processed SVG templates from. "
                "Defaults to the templates/bs_icon/ directory inside this app."
            ),
        )
        parser.add_argument(
            "--output-dir",
            default=str(Path(settings.BASE_DIR) / "templates" / "bs_icon"),
            help=(
                "Directory to copy processed SVG templates into. "
                "Defaults to your project's BASE_DIR/templates/bs_icon."
            ),
        )

    def handle(self, *args, **options):
        source_dir = self._resolve_source_dir(options["source_dir"])
        output_dir = Path(options["output_dir"])
        output_dir.mkdir(parents=True, exist_ok=True)

        count = 0
        for name in options["names"]:
            filename = name if name.endswith(".svg") else f"{name}.svg"
            src = source_dir / filename
            if not src.is_file():
                raise CommandError(
                    f"Icon {filename!r} not found in {source_dir}. "
                    "Run 'download_bs_icons' first or check the name."
                )
            shutil.copy2(src, output_dir / filename)
            count += 1

        self.stdout.write(
            self.style.SUCCESS(f"Done. {count} icons copied to {output_dir}")
        )

    def _resolve_source_dir(self, raw: str | None) -> Path:
        if raw:
            return Path(raw)
        app_dir = Path(__file__).resolve().parent.parent.parent
        return app_dir / "templates" / "bs_icon"
