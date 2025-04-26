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
        # API-Endpunkt
        api_url = "https://api.dawum.de/"
        response = requests.get(api_url)

        if response.status_code == 200:
            data = response.json()

            # Institute aus den API-Daten extrahieren
            institutes = data.get("Institutes", {})
            if not institutes:
                self.stdout.write(self.style.ERROR("Keine Institute in den API-Daten gefunden."))
                return

            # Institute hinzufügen oder aktualisieren
            for institute_id, institute_data in institutes.items():
                name = institute_data.get("Name")
                if not name:
                    self.stdout.write(self.style.ERROR(f"Institut mit ID {institute_id} hat keinen Namen."))
                    continue

                # Erstelle oder aktualisiere das Institut mit der API-ID
                institute, created = Institute.objects.update_or_create(
                    id=institute_id, defaults={"name": name}
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Institut '{name}' mit ID {institute_id} hinzugefügt."))
                else:
                    self.stdout.write(f"Institut '{name}' mit ID {institute_id} aktualisiert.")

            # Parteien aus den API-Daten extrahieren
            parties = data.get("Parties", {})
            if not parties:
                self.stdout.write(self.style.ERROR("Keine Parteien in den API-Daten gefunden."))
            else:
                for party_id, party_data in parties.items():
                    name = party_data.get("Name")
                    color = party_data.get("Color", "#000000")  # Standardfarbe Schwarz, falls keine Farbe angegeben ist
                    if not name:
                        self.stdout.write(self.style.ERROR(f"Partei mit ID {party_id} hat keinen Namen."))
                        continue

                    # Erstelle oder aktualisiere die Partei
                    party, created = Party.objects.get_or_create(name=name, defaults={"color": color})
                    if created:
                        self.stdout.write(self.style.SUCCESS(f"Partei '{name}' hinzugefügt."))
                    else:
                        self.stdout.write(f"Partei '{name}' existiert bereits.")

            # API-Daten in eine Datei schreiben
            with open("api_data_debug.json", "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)

            self.stdout.write("API-Daten wurden in 'api_data_debug.json' gespeichert.")

            # Polls und Ergebnisse aktualisieren
            for poll_id, poll_data in data.items():
                poll_date = poll_data.get("Date")
                institute_id = poll_data.get("Institute_ID")
                results = poll_data.get("Results", {})

                # Debugging-Ausgabe
                self.stdout.write(f"Verarbeite Poll-ID {poll_id}: {poll_data}")

                # Validierung der Daten
                if not poll_date or not institute_id or not isinstance(results, dict):
                    self.stdout.write(self.style.ERROR(f"Ungültige Daten für Poll-ID {poll_id}: {poll_data}"))
                    continue

                try:
                    # Datum umwandeln und validieren
                    pub_date = timezone.make_aware(datetime.strptime(poll_date, '%Y-%m-%d'))
                except ValueError:
                    self.stdout.write(self.style.ERROR(f"Ungültiges Datum: {poll_date} für Poll-ID {poll_id}"))
                    continue

                try:
                    with transaction.atomic():  # Start einer Transaktion
                        # Erstelle oder finde das Institute
                        institute_name = f"Institution {institute_id}"  # Beispielname
                        institute, created = Institute.objects.get_or_create(name=institute_name)

                        # Erstelle das Poll
                        poll = Poll.objects.create(
                            institute=institute,
                            pub_date=pub_date
                        )

                        # PollResult für jedes Ergebnis hinzufügen
                        for party_id, percentage in results.items():
                            # Erstelle oder finde die Partei (z. B. Party 1, Party 2 etc.)
                            party_name = f"Party {party_id}"
                            party, _ = Party.objects.get_or_create(name=party_name)

                            # Erstelle das PollResult
                            PollResult.objects.create(
                                poll=poll,
                                party=party,
                                percentage=percentage
                            )
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Fehler beim Speichern der Daten für Poll-ID {poll_id}: {e}"))
                    continue

            # Bundestagswahlumfragen aus den API-Daten extrahieren
            surveys = data.get("Surveys", {})
            if not surveys:
                self.stdout.write(self.style.ERROR("Keine Umfragen in den API-Daten gefunden."))
            else:
                for poll_id, poll_data in surveys.items():
                    poll_date = poll_data.get("Date")
                    institute_id = poll_data.get("Institute_ID")
                    results = poll_data.get("Results", {})

                    # Umfragen auf das Jahr 2025 beschränken
                    if not poll_date.startswith("2025"):
                        continue

                    # Debugging-Ausgabe
                    self.stdout.write(f"Verarbeite Umfrage-ID {poll_id}: {poll_data}")

                    # Validierung der Daten
                    if not poll_date or not institute_id or not isinstance(results, dict):
                        self.stdout.write(self.style.ERROR(f"Ungültige Daten für Umfrage-ID {poll_id}: {poll_data}"))
                        continue

                    try:
                        # Datum umwandeln und validieren
                        pub_date = timezone.make_aware(datetime.strptime(poll_date, '%Y-%m-%d'))
                    except ValueError:
                        self.stdout.write(self.style.ERROR(f"Ungültiges Datum: {poll_date} für Umfrage-ID {poll_id}"))
                        continue

                    try:
                        with transaction.atomic():  # Start einer Transaktion
                            # Erstelle oder finde das Institut
                            institute = Institute.objects.filter(id=institute_id).first()
                            if not institute:
                                self.stdout.write(self.style.ERROR(f"Institut mit ID {institute_id} nicht gefunden."))
                                continue

                            # Erstelle die Umfrage (Poll)
                            poll = Poll.objects.create(
                                institute=institute,
                                pub_date=pub_date
                            )

                            # Ergebnisse (PollResults) hinzufügen
                            for party_id, percentage in results.items():
                                # Partei anhand des Namens suchen
                                party_name = parties.get(str(party_id), {}).get("Name")
                                if not party_name:
                                    self.stdout.write(self.style.ERROR(f"Partei mit ID {party_id} hat keinen gültigen Namen in den API-Daten."))
                                    continue

                                # Partei suchen oder erstellen
                                party, created = Party.objects.get_or_create(name=party_name, defaults={"color": "#000000"})
                                if created:
                                    self.stdout.write(self.style.SUCCESS(f"Partei '{party_name}' wurde erstellt."))
                                else:
                                    self.stdout.write(f"Partei '{party_name}' existiert bereits.")

                                # PollResult erstellen
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
