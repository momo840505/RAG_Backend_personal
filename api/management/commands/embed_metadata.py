from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Sanity check: this is a stub for embedding metadata."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=5)

    def handle(self, *args, **opts):
        self.stdout.write(self.style.SUCCESS(
            f"embed_metadata command wired up. limit={opts['limit']}"
        ))
