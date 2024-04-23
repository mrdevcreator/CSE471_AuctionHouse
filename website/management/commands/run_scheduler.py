from django.core.management.base import BaseCommand
import schedule
import time
from django.utils import timezone
from website.views import past_auction_items

class Command(BaseCommand):
    help = 'Runs scheduled tasks using the schedule library'

    def handle(self, *args, **options):
        def schedule_past_auction_items():
            current_time = timezone.now()
            past_auction_items(None)
            self.stdout.write(self.style.SUCCESS("Task completed."))

        schedule.every().minute.do(schedule_past_auction_items)

        while True:
            schedule.run_pending()
            time.sleep(1)