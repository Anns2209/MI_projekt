# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []
import sqlite3
import os
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import yt_dlp
from unidecode import unidecode
import re

# Pot do baze za shranjevanje video povezav
VIDEO_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "video_links.db")
PREDMETI_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "student_info.db")

class ActionShraniVideo(Action):
    def name(self) -> Text:
        return "action_shrani_video"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Poišči zadnje sporočilo uporabnika, ki je povezava
        for event in reversed(tracker.events):
            if event.get("event") == "user" and "text" in event:
                text = event["text"]
                if "http" in text and ("youtube" in text or ".mp4" in text):
                    link = text.strip()
                    break
        else:
            dispatcher.utter_message(text="Ne najdem nobene video povezave za shranjevanje.")
            return []

        # Poveži se z bazo
        conn = sqlite3.connect(VIDEO_DB_PATH)
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS video_links (id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT)")

        # Preveri, če je povezava že v bazi
        c.execute("SELECT COUNT(*) FROM video_links WHERE url = ?", (link,))
        count = c.fetchone()[0]

        if count > 0:
            dispatcher.utter_message(text="Ta video je že bil shranjen.")
        else:
            c.execute("INSERT INTO video_links (url) VALUES (?)", (link,))
            conn.commit()
            dispatcher.utter_message(text=f"Povezava {link} je bila shranjena.")

        conn.close()
        return []


class ActionAnalizirajVideo(Action):
    def name(self) -> Text:
        return "action_analiziraj_video"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        for event in reversed(tracker.events):
            if event.get("event") == "user" and "text" in event:
                text = event["text"]
                if "http" in text and "youtube.com" in text:
                    link = text
                    break
        else:
            dispatcher.utter_message(text="Nisem našla nobene video povezave za analizo.")
            return []

        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(link, download=False)
                naslov = info.get("title", "neznan")
                dispatcher.utter_message(text=f"Naslov videa je: {naslov}")
        except Exception as e:
            dispatcher.utter_message(text=f"Napaka pri analizi videa: {str(e)}")

        return []


class ActionVrniInformacije(Action):
    def name(self) -> Text:
        return "action_vrni_informacije"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_input = unidecode(tracker.latest_message.get("text").lower())

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(BASE_DIR, "..", "student_info.db")

        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT ime FROM predmeti")
        vsi_predmeti = [row[0] for row in c.fetchall()]
        conn.close()

        predmet = next(
            (p for p in vsi_predmeti if unidecode(p.lower()) in user_input), None
        )

        if not predmet:
            dispatcher.utter_message(text="Ne prepoznam predmeta.")
            return []

        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT profesor, krediti, termin FROM predmeti WHERE ime=?", (predmet,))
        result = c.fetchone()
        conn.close()

        if result:
            odgovor = f"{predmet} predava {result[0]}, ima {result[1]} ECTS, poteka pa {result[2]}."
        else:
            odgovor = "Za ta predmet nimam podatkov."

        dispatcher.utter_message(text=odgovor)
        return []


class ActionPrikaziVidee(Action):
    def name(self) -> Text:
        return "action_prikazi_videe"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "video_links.db")
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT url FROM video_links ORDER BY id DESC LIMIT 5")
        result = c.fetchall()
        conn.close()

        if result:
            povezave = "\n".join([r[0] for r in result])
            dispatcher.utter_message(text=f"Zadnje shranjene video povezave:\n{povezave}")
        else:
            dispatcher.utter_message(text="Ni shranjenih video povezav.")

        return []

class ActionDodajPredmet(Action):
    def name(self) -> Text:
        return "action_dodaj_predmet"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        text = tracker.latest_message.get("text").lower()

        try:
            ime_match = re.search(r'predmet\s+([^,]+)', text)
            profesor_match = re.search(r'profesor\s+([^,]+)', text)
            krediti_match = re.search(r'(\d+)\s*(ects|kredit)', text)
            termin_match = re.search(r'(ponedeljek|torek|sreda|četrtek|petek).*?ob\s+\d{1,2}(:\d{2})?', text)

            if not all([ime_match, profesor_match, krediti_match, termin_match]):
                raise ValueError("Manjkajo podatki")

            ime = ime_match.group(1).strip().title()
            profesor = profesor_match.group(1).strip().title()
            krediti = int(krediti_match.group(1))
            termin = termin_match.group(0).strip().capitalize()

        except Exception as e:
            dispatcher.utter_message(
                text="Nisem razumela vseh podatkov. Prosim uporabi: 'Dodaj predmet Ime, profesor Ime, 6 ECTS, dan ob uri'."
            )
            return []

        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "student_info.db")
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        c.execute("CREATE TABLE IF NOT EXISTS predmeti (ime TEXT, profesor TEXT, krediti INTEGER, termin TEXT)")

        c.execute("SELECT * FROM predmeti WHERE ime=?", (ime,))
        if c.fetchone():
            dispatcher.utter_message(response="utter_predmet_obstaja")
            conn.close()
            return []

        c.execute("INSERT INTO predmeti (ime, profesor, krediti, termin) VALUES (?, ?, ?, ?)",
                  (ime, profesor, krediti, termin))
        conn.commit()
        conn.close()

        dispatcher.utter_message(response="utter_potrditev_dodajanja")
        return []


class ActionIzbrisiPredmet(Action):
    def name(self) -> Text:
        return "action_izbrisi_predmet"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        text = tracker.latest_message.get("text").lower()
        if "predmet" in text:
            ime = text.split("predmet")[-1].strip().title()
        else:
            dispatcher.utter_message(text="Napiši ime predmeta, ki ga želiš izbrisati.")
            return []

        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "student_info.db")
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        c.execute("SELECT * FROM predmeti WHERE ime=?", (ime,))
        if not c.fetchone():
            dispatcher.utter_message(response="utter_ne_obstaja")
            conn.close()
            return []

        c.execute("DELETE FROM predmeti WHERE ime=?", (ime,))
        conn.commit()
        conn.close()

        dispatcher.utter_message(response="utter_potrditev_brisanja")
        return []












