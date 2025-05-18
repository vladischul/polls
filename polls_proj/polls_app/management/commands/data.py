import requests
from django.utils import timezone
from polls_app.models import Question, Poll, PollResult, Institute, Party
from django.core.management.base import BaseCommand
from datetime import datetime
from django.db import transaction
import json

class Command(BaseCommand):
    help = "Füge Institute aus der API hinzu"

    def handle(self, *args, **kwargs):
        self.stdout.write("Lösche alle bestehenden Polls und PollResults...")
        PollResult.objects.all().delete()
        Poll.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("Alle Polls und PollResults wurden gelöscht."))

        api_url = "https://api.dawum.de/"
        response = requests.get(api_url)

        if response.status_code == 200:
            data = response.json()

            institutes = data.get("Institutes", {})
            if not institutes:
                self.stdout.write(self.style.ERROR("Keine Institute in den API-Daten gefunden."))
                return

            for institute_id, institute_data in institutes.items():
                name = institute_data.get("Name")
                if not name:
                    self.stdout.write(self.style.ERROR(f"Institut mit ID {institute_id} hat keinen Namen."))
                    continue

                institute, created = Institute.objects.update_or_create(
                    id=institute_id, defaults={"name": name}
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Institut '{name}' mit ID {institute_id} hinzugefügt."))
                else:
                    self.stdout.write(f"Institut '{name}' mit ID {institute_id} aktualisiert.")

            parties = data.get("Parties", {})
            if not parties:
                self.stdout.write(self.style.ERROR("Keine Parteien in den API-Daten gefunden."))
            else:
                for party_id, party_data in parties.items():
                    name = party_data.get("Name")
                    color = party_data.get("Color", "#000000")
                    shortcut = party_data.get("Shortcut", "")
                    if not name:
                        self.stdout.write(self.style.ERROR(f"Partei mit ID {party_id} hat keinen Namen."))
                        continue

                    party, created = Party.objects.get_or_create(
                        name=name, defaults={"color": color, "shortcut": shortcut}
                    )
                    if created:
                        self.stdout.write(self.style.SUCCESS(f"Partei '{name}' hinzugefügt."))

            with open("api_data_debug.json", "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)

            self.stdout.write("API-Daten wurden in 'api_data_debug.json' gespeichert.")

            for poll_id, poll_data in data.items():
                poll_date = poll_data.get("Date")
                institute_id = poll_data.get("Institute_ID")
                results = poll_data.get("Results", {})

                self.stdout.write(f"Verarbeite Poll-ID {poll_id}: {poll_data}")

                if not poll_date or not institute_id or not isinstance(results, dict):
                    self.stdout.write(self.style.ERROR(f"Ungültige Daten für Poll-ID {poll_id}: {poll_data}"))
                    continue

                try:
                    pub_date = timezone.make_aware(datetime.strptime(poll_date, '%Y-%m-%d'))
                except ValueError:
                    self.stdout.write(self.style.ERROR(f"Ungültiges Datum: {poll_date} für Poll-ID {poll_id}"))
                    continue

                try:
                    with transaction.atomic():
                        institute_name = f"Institution {institute_id}"
                        institute, created = Institute.objects.get_or_create(name=institute_name)

                        poll = Poll.objects.create(
                            institute=institute,
                            pub_date=pub_date
                        )

                        for party_id, percentage in results.items():
                            party_name = f"Party {party_id}"
                            party, _ = Party.objects.get_or_create(name=party_name)

                            PollResult.objects.create(
                                poll=poll,
                                party=party,
                                percentage=percentage
                            )
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Fehler beim Speichern der Daten für Poll-ID {poll_id}: {e}"))
                    continue

            surveys = data.get("Surveys", {})
            if not surveys:
                self.stdout.write(self.style.ERROR("Keine Umfragen in den API-Daten gefunden."))
            else:
                for poll_id, poll_data in surveys.items():
                    poll_date = poll_data.get("Date")
                    institute_id = poll_data.get("Institute_ID")
                    
                    survey_period_data = poll_data.get("Survey_Period", {})
                    survey_period = None
                    if survey_period_data:
                        date_start = survey_period_data.get("Date_Start")
                        date_end = survey_period_data.get("Date_End")
                        if date_start and date_end:
                            survey_period = f"{date_start} - {date_end}"

                    surveyed_persons = poll_data.get("Surveyed_Persons", 0)
                    results = poll_data.get("Results", {})

                    if not poll_date.startswith("2025"):
                        continue

                    self.stdout.write(f"Verarbeite Umfrage-ID {poll_id}: {poll_data}")

                    if not poll_date or not institute_id or not isinstance(results, dict):
                        self.stdout.write(self.style.ERROR(f"Ungültige Daten für Umfrage-ID {poll_id}: {poll_data}"))
                        continue

                    try:
                        pub_date = timezone.make_aware(datetime.strptime(poll_date, '%Y-%m-%d'))
                    except ValueError:
                        self.stdout.write(self.style.ERROR(f"Ungültiges Datum: {poll_date} für Umfrage-ID {poll_id}"))
                        continue

                    try:
                        with transaction.atomic():
                            institute = Institute.objects.filter(id=institute_id).first()
                            if not institute:
                                self.stdout.write(self.style.ERROR(f"Institut mit ID {institute_id} nicht gefunden."))
                                continue

                            poll = Poll.objects.create(
                                institute=institute,
                                pub_date=pub_date,
                                survey_period=survey_period,
                                surveyed_persons=surveyed_persons
                            )

                            for party_id, percentage in results.items():
                                party_name = data.get("Parties", {}).get(str(party_id), {}).get("Name")
                                if not party_name:
                                    self.stdout.write(self.style.ERROR(f"Partei mit ID {party_id} hat keinen gültigen Namen in den API-Daten."))
                                    continue

                                party, created = Party.objects.get_or_create(name=party_name, defaults={"color": "#000000"})
                                if created:
                                    self.stdout.write(self.style.SUCCESS(f"Partei '{party_name}' wurde erstellt."))
                                else:
                                    self.stdout.write(f"Partei '{party_name}' existiert bereits.")

                                PollResult.objects.create(
                                    poll=poll,
                                    party=party,
                                    percentage=percentage
                                )
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Fehler beim Speichern der Daten für Umfrage-ID {poll_id}: {e}"))
                        continue

            self.stdout.write(self.style.SUCCESS("Alle Daten erfolgreich aktualisiert."))
        else:
            self.stdout.write(self.style.ERROR(f"API-Anfrage fehlgeschlagen mit Statuscode: {response.status_code}"))
