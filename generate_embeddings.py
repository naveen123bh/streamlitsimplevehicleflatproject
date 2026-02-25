from embeddings import InstrumentRecognizer

# CSV file jisme item_name, image_url, embedding
CSV_FILE = "plasma.csv"

recognizer = InstrumentRecognizer(CSV_FILE)

# Tumhare items
items = [
    ("harmonic cable", "https://drive.google.com/uc?export=download&id=17YHshrLdblSwyceN5dufRo2C_1WByxr5"),
    ("Arthrex remote pump (Arthroscopy) 3rd floor", "https://drive.google.com/uc?export=download&id=1Dm_c-tKqtuDb5HpH4dfav4jIGOLZ3HZN"),
    ("light cable without band", "https://drive.google.com/uc?export=download&id=1vxadWgoXsjcAwZG7UGRe4S6ek3wnjd_H"),
    ("Smith and nephew light cable 3rd floor", "https://drive.google.com/uc?export=download&id=1MCJLCDVlwxbmBwONi3k8yTyjVYEzgWn3")
]

for name, url in items:
    try:
        print(f"Processing: {name}")
        recognizer.add_to_database(url, name=name)
        print("✅ Done")
    except Exception as e:
        print(f"❌ Failed: {name} -> {e}")