import csv
import os
import time
from api_calls import make_api_call

def create_directory(save_directory):
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

def download_documents_from_csv(csv_file, save_directory):

    with open(csv_file, 'r') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # Preskoči zaglavlje

        for row in csv_reader:
            document_url = row[7]  # stupac sadrži URL dokumenta
            document_title = row[2].replace("/", "_")  # stupac sadrži naslov dokumenta
            doc_path = "<putanja>/DownloadedStudentFiles/" + document_title + ".pdf" #path do moguceg postojeceg dokumenta
            if os.path.exists(doc_path):
                print("Dokument već postoji!")
            else:
                document_url += "/datastream/PDF/download"
                print(document_url)
                document_content = make_api_call(document_url)

                if document_content:
                    with open(os.path.join(save_directory, f"{document_title}.pdf"), 'wb') as doc_file:
                        doc_file.write(document_content)
                    print(f"Dokument '{document_title}' uspješno preuzet i spremljen.")
                else:
                    print(f"Dokument '{document_title}' nije uspješno preuzet.")

                time.sleep(10)

save_directory = '<putanja>/DownloadedStudentFiles'
create_directory(save_directory)

# Postavi putanju do CSV datoteke i direktorij za spremanje dokumenata
for i in range(1, 5):
    csv_file_path = f"<putanja>/scripts/dabar_popis_radova_{i}.csv"

    download_documents_from_csv(csv_file_path, save_directory)
