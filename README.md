# AI Študentski Asistent

## Opis projekta

AI Študentski Asistent je spletna aplikacija, razvita v okviru predmeta Mobilna interakcija. Namen projekta je uporabnikom omogočiti interakcijo s pogovornim sistemom prek različnih vhodnih načinov, kot so besedilo, govor in video povezave.

Sistem temelji na ogrodju Rasa za obdelavo naravnega jezika ter Flask strežniku za povezavo med uporabniškim vmesnikom in chatbotom. Podatki se shranjujejo v SQLite podatkovne baze.

---

## Glavne funkcionalnosti

### 1. Besedilna komunikacija

Uporabnik lahko komunicira z chatbotom preko tekstovnega vnosa.

Primeri:

* Kdo predava Mobilna interakcija?
* Koliko ECTS ima predmet Internet stvari?
* Kdaj potekajo Optične komunikacije?

### 2. Glasovni vnos

Aplikacija podpira prepoznavanje govora preko Web Speech API.

Uporabnik lahko:

* klikne gumb "Govori"
* izgovori vprašanje
* chatbot samodejno obdela prepoznano besedilo

### 3. Obdelava video povezav

Uporabnik lahko pošlje YouTube ali MP4 povezavo.

Možnosti:

* shranjevanje povezave
* analiza videa
* prikaz zadnjih shranjenih videov

### 4. Upravljanje predmetov

Uporabnik lahko:

* pridobi informacije o predmetih
* dodaja nove predmete
* briše obstoječe predmete

Podatki vključujejo:

* ime predmeta
* profesorja
* število ECTS kreditov
* termin izvajanja

---

## Tehnologije

### Backend

* Python 3.8+
* Flask
* Rasa
* Rasa SDK
* SQLite

### Frontend

* HTML
* CSS
* JavaScript

### Knjižnice

* yt-dlp
* unidecode
* sqlite3

---

## Podatkovne baze

### student_info.db

Tabela predmeti:

| Stolpec  | Opis             |
| -------- | ---------------- |
| ime      | Ime predmeta     |
| profesor | Nosilec predmeta |
| krediti  | ECTS krediti     |
| termin   | Termin izvajanja |

### video_links.db

Tabela video_links:

| Stolpec | Opis           |
| ------- | -------------- |
| id      | ID povezave    |
| url     | Video povezava |

---

## Zagon projekta

### 1. Aktivacija virtualnega okolja

```bash
source venv/bin/activate
```

### 2. Zagon Action Serverja

```bash
rasa run actions
```

### 3. Zagon Rasa strežnika

```bash
rasa run --enable-api
```

### 4. Zagon Flask aplikacije

```bash
python app.py
```

### 5. Odpri aplikacijo

V brskalniku odpri:

```text
http://localhost:5000
```

---

## Primer uporabe

### Informacije o predmetu

```text
Kdo predava Internet stvari?
```

Odgovor:

```text
Internet stvari predava Iztok Kramberger, ima 5 ECTS, poteka pa Ponedeljek ob 8:00.
```

### Shranjevanje videa

```text
https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

```text
Shrani video
```

### Prikaz zadnjih videov

```text
Pokaži mi videe
```

---


