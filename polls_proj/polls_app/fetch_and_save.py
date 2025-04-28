from polls.polls_proj.polls_app.management.commands.data import fetch_data_from_api, save_data_to_db

# Abrufen der Daten von der API
data = fetch_data_from_api()

# Wenn die Daten erfolgreich abgerufen wurden, speichere sie in der DB
if data:
    save_data_to_db(data)