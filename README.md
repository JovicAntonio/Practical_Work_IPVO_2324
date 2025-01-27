# IIS projekt 2025

## Scraping podataka

Prije treniranja modela potrebno je bilo skinuti podatke za treniranje istog. Korištenjem različitih filtera na stranici dabar.srce.hr skinuli smo podatke 2000 radova iz 7 različitih polja:

 1. biomedicina i zdravstvo
 2. biotehničke znanosti
 3. društvene znanosti
 4. humanističke znanosti
 5. prirodne znanosti
 6. tehničke znanosti
 7. umjetničko područje

Rezultat je csv datoteka od 14000 radova koja sadrži URL do rada, naslov, autore i sl. Nažalost, izvozom u CSV koji nudi dabar.srce.hr ne preuzmu se sažetak i ključne riječi, pa smo za iste napravili skriptu za scrape-anje podatake.

Prvo smo podijelili CSV od 14000 radova na više CSV datoteka veličine 500 radova kako, ukoliko se prilikom scrape-anja podataka dogodi greška, ne izgubi sav prethodno preuzeti trud.

### Dijeljenje glavne CSV datoteke u više manjih CSV datoteka

```py
import pandas as pd
import os

def split_csv(file_path, output_dir, rows_per_file=500):
    put directory exists
    os.makedirs(output_dir, exist_ok=True)
    data = pd.read_csv(file_path, delimiter=';', encoding='utf-8-sig')
    total_rows = data.shape[0]
    file_count = 0

    for start_row in range(0, total_rows, rows_per_file):
        file_count += 1
        subset = data.iloc[start_row:start_row + rows_per_file]
        output_file = os.path.join(output_dir, f'{file_count}.csv')
        subset.to_csv(output_file, index=False, sep=';', encoding='utf-8-sig')

    print(f"CSV file split into {file_count} files in '{output_dir}'.")

file_path = '/Volumes/Samsung_T5/IIS/csv/sve_with_summaries.csv'
output_dir = '/Volumes/Samsung_T5/IIS/csv' 
split_csv(file_path, output_dir)

```

### Scraping sažetaka

Nakon razdvajanja na više manjih CSV datoteka, ideja je bila da pomoću for petlje prolazimo kroz svaku datoteku i onda tražimo podudaranje s HTML elementom kako bi skinuli sažetak svakog rada, s obzirom da HTML forma svakog rada je ista. Kad bi skripta pronašla podudaranje onda bi isto nadodalo u postojeću datoteku na kraj. S obzirom da nismo imali mogućnost preuzimanja podataka preko API-a repozitorija Dabar, a imamo iskustva sa Selenium paketom, koji omogućava automatizirano upravljanje procesima poput otvaranja određene poveznice u pregledniku, klikanje određenih tipki i sl., odlučili smo se za koriđtenje istog kako bi prikupili podatke. Ideja je bila otvoriti svaki link, pričetaki dvije sekunde da se stranica učita, potražiti uvjet definiran u programskom kodu te ukoliko nađe podudaranje uvjeta s HTML elementom, preuzimanje sadržaja.

```py
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

input_files = [f"/Volumes/Samsung_T5/IIS/csv/{i}.csv" for i in range(1, 29)]
output_files = [f"/Volumes/Samsung_T5/IIS/csvSummaries/{i}_with_summaries.csv" for i in range(1, 29)]

chrome_options = Options()
chrome_options.add_argument('--headless')

driver = webdriver.Chrome(options=chrome_options)

for input_file, output_file in zip(input_files, output_files):
    data = pd.read_csv(input_file, sep=";", encoding="utf-8-sig")
    urls = data.iloc[:, 6].dropna()
    summaries = []

    try:
        for url in urls:
            print(f"Opening URL: {url}")
            driver.get(url)
            time.sleep(2) 

            try:
                sazetak_element = driver.find_element(By.XPATH, "//tr[contains(@class, 'odd') or contains(@class, 'even')]/td[2]/div[@class='shorten pre-wrap']")
                sazetak_html = sazetak_element.get_attribute("innerHTML")
                sazetak_html = sazetak_html.replace('<span style="display: inline;">... </span>', "")
                sazetak_html = sazetak_html.replace('<a href="#" class="shorten-more" style="display: inline;">Više</a>', "")
                sazetak_html = sazetak_html.replace('<span style="display: none;">', "")
                sazetak_html = sazetak_html.replace('</span>', "")
                sazetak_html = sazetak_html.replace('<a href="#" class="shorten-less">Sakrij dio sažtka</a>', "")
                summary_cleaned = sazetak_html.strip()
                summaries.append(summary_cleaned)
            except Exception as e:
                print(f"Could not extract summary for URL {url}: {e}")
                summaries.append("")  

    finally:
        print(f"Finished processing {input_file}")

    updated_data = data.copy()
    updated_data["Summary"] = summaries + [""] * (len(updated_data) - len(summaries))
    updated_data.to_csv(output_file, sep=";", encoding="utf-8-sig", index=False)
    print(f"Updated CSV file saved to {output_file}")
driver.quit()
print("Browser closed.")

```

### Scraping ključnih riječi

Prvotna ideja bila nam je trenirati model koristeći jedino sažetke radova, no u procesu smo odlučili dotrenirati isti s ključnim riječima, također preuzetih s dabar.srce.hr stranice.

```py
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

input_files = [f"/Volumes/Samsung_T5/IIS/csv/{i}.csv" for i in range(29, 30)]
output_files = [f"/Volumes/Samsung_T5/IIS/csvSummaries/sve_with_summaries_{i}_with_keywords.csv" for i in range(29, 30)]
chrome_options = Options()
chrome_options.add_argument('--headless')
driver = webdriver.Chrome(options=chrome_options)

for input_file, output_file in zip(input_files, output_files):
    data = pd.read_csv(input_file, sep=";", encoding="utf-8-sig")
    urls = data.iloc[:, 6].dropna()
    summaries = []
    try:
        for url in urls:
            print(f"Opening URL: {url}")
            driver.get(url)
            time.sleep(2)  

            try:
                keyword_row = driver.find_element(By.XPATH,
                                                  "//tr[contains(@class, 'even') or contains(@class, 'odd')][td[text()='Ključne riječi']]")
                button_elements = keyword_row.find_elements(By.XPATH, ".//td[2]//button")
                summary_cleaned = ";".join(button.text.strip() for button in button_elements)
                summaries.append(summary_cleaned)
            except Exception as e:
                print(f"Could not extract content for URL {url}: {e}")
                summaries.append("")  
    finally:
        print(f"Finished processing {input_file}")

    updated_data = data.copy()
    if len(updated_data.columns) < 10:
        for _ in range(10 - len(updated_data.columns)):
            updated_data[f"Column{len(updated_data.columns) + 1}"] = ""

    updated_data.iloc[:, 9] = summaries + [""] * (len(updated_data) - len(summaries))
    updated_data.to_csv(output_file, sep=";", encoding="utf-8-sig", index=False)
    print(f"Updated CSV file saved to {output_file}")

driver.quit()
print("Browser closed.")
```

### Spajanje u jednu CSV datoteku

Po završetku smo skriptom za spajanje datoteka spojili manje CSV datoteke natrag u jednu glavnu CSV datoteku.

```py
import pandas as pd
import os

def join_csv_files(input_dir, output_file, delimiter=';', encoding='utf-8-sig'):

    data_frames = []
    for i in range(1, 31):
        csv_file = f"sve_with_summaries_{i}_with_keywords.csv"
        file_path = os.path.join(input_dir, csv_file)

        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            continue

        print(f"Processing file: {file_path}")

        try:
            if len(data_frames) == 0:
                df = pd.read_csv(file_path, delimiter=delimiter, encoding=encoding)
            else:
                df = pd.read_csv(file_path, delimiter=delimiter, encoding=encoding, header=0)
            data_frames.append(df)
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            continue
    combined_df = pd.concat(data_frames, ignore_index=True)

    combined_df.to_csv(output_file, index=False, sep=delimiter, encoding=encoding)
    print(f"All CSV files joined into '{output_file}'.")

input_dir = '/Volumes/Samsung_T5/IIS/csvSummaries' 
output_file = '/Volumes/Samsung_T5/IIS/csvSummaries/combined.csv'
join_csv_files(input_dir, output_file)
```

### Rješavanje anomalija

Provjerom prikupljenih podataka primjetili smo nekoliko anomalija, uglavnom istog tipa. Ispostavilo se da su određeni matematički radovi za prikaz formule u HTML-u koristili zaseban tag, te isto nismo predvidjeli. Taj dio trebali smo ručno ispravljati, no srećom bilo je samo 142 rada gdje je trebalo ručno spremniti sažetak.

### Izrada modela

Nakon prikupljenih podataka, došao je red na izradu modela. Kako bismo efikasno rješili problem koristilo se dva modela: model za klasifikaciju radova i model za komputizaciju vektorskih embedding-a iz teksta, odnosno generiranje numeričkih vektorskih reprezentacija, te enkoder kojim smo pretvarali klase (područja znanstvenih radova) iz znakovnih nizova (string) u cijele brojeve (int).

Za komputizaciju vektorskih embedding-a, koristili smo već pretrenirani `all-MiniLM-L6` model, kojim smo tekst, neovisno jesu li to sažetci ili ključne riječi, koji bi dali za treniranje pretvarali u vektore. Model je radio na hrvatskim riječima i bez dodatne konfiguracije jer se radi od višejezičnom modelu koji je, u svrhe ovog projekta, i više nego dovoljno zadovoljio potrebe projekta. Za treniranje modela se koristio omjer 80:20, gdje je 80% podataka korišteno za treniranje, a preostali dio za testiranje.

```py
from sentence_transformers import SentenceTransformer
import torch

embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

train_summary_embeddings = torch.tensor(embedder.encode(X_train_summaries.reset_index(drop=True).tolist(), convert_to_tensor=True))
test_summary_embeddings = torch.tensor(embedder.encode(X_test_summaries.reset_index(drop=True).tolist(), convert_to_tensor=True))

train_keyword_embeddings = torch.tensor(embedder.encode(X_train_keywords.reset_index(drop=True).tolist(), convert_to_tensor=True))
test_keyword_embeddings = torch.tensor(embedder.encode(X_test_keywords.reset_index(drop=True).tolist(), convert_to_tensor=True))
```

Kod drugog modela, koje je efektivno neuronska mreža koji služi za unos podataka (u ovom slučaju se radi o višeslojnom unosu posebno za sažetke i posebno za ključne riječi), te o izlaznom sloju na kojem se generira odluka mreže bazirana na oba unesena seta podataka.

```py
class MultiInputClassifier(nn.Module):
    def __init__(self, input_dim, hidden_dim, num_classes):
        super(MultiInputClassifier, self).__init__()

        # Separate pathways for summaries and keywords
        self.summary_fc = nn.Linear(input_dim, hidden_dim)
        self.keyword_fc = nn.Linear(input_dim, hidden_dim)

        # Combined pathway
        self.fc_out = nn.Linear(hidden_dim * 2, num_classes)

    def forward(self, summary_embeddings, keyword_embeddings):
        summary_out = torch.relu(self.summary_fc(summary_embeddings))
        keyword_out = torch.relu(self.keyword_fc(keyword_embeddings))

        combined = torch.cat((summary_out, keyword_out), dim=1)  # Combine features
        output = self.fc_out(combined)
        return output
```

Model je treniran algoritmom Cross Entropy Loss, koji se često koristi i prikladan je za rad sa tekstom, te se koristi Adam optimizator, koji podešava težine modela ovisno o gradijentima.

```py
model = MultiInputClassifier(input_dim, hidden_dim, num_classes)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)
```

Nakon toga se vrši treniranje kroz epohe, iz čega se vidi da je loss vrlo nizak, što može značiti da je model dobar.

```py
Epoch 1/10, Loss: 0.0442
Epoch 2/10, Loss: 0.0312
Epoch 3/10, Loss: 0.0281
Epoch 4/10, Loss: 0.0265
Epoch 5/10, Loss: 0.0254
Epoch 6/10, Loss: 0.0245
Epoch 7/10, Loss: 0.0239
Epoch 8/10, Loss: 0.0232
Epoch 9/10, Loss: 0.0227
Epoch 10/10, Loss: 0.0222
```

Nakon evaluacije modela, generiran je klasifikacijski izvještaj, u kojem se gleda preciznost, odziv i F1-score. Preciznost je omjer istinitih pozitivnih predikcija i pozitivnih predikcija, neovisno jesu li lažne ili istinite. Odziv je omjer istinitih pozitivnih predikcija te zbroja istinitih pozitivnih predikcija i lažnih negativnih predikcija. F1-score je dvostruki omjer umnoška preciznosti i odziva te zbroja preciznosti i odziva.

```py
                           precision    recall  f1-score   support

biomedicina i zdravstvo       0.84      0.77      0.80       400
   biotehničke znanosti       0.66      0.67      0.66       400
     društvene znanosti       0.59      0.71      0.65       400
  humanističke znanosti       0.76      0.65      0.70       400
      prirodne znanosti       0.66      0.66      0.66       400
      tehničke znanosti       0.64      0.62      0.63       400
    umjetničko područje       0.74      0.78      0.76       400

               accuracy                           0.69      2800
              macro avg       0.70      0.69      0.70      2800
           weighted avg       0.70      0.69      0.70      2800
```

Model jako dobro prepoznaje klasu `biomedicina i zdravstvo`, obzirom da je preciznost vrlo visoka, odziv je visok te je omjer između njih dobar. U kategoriji solidnih su  `biotehničke znanosti`, `humanističke znanosti`, `prirodne znanosti`, `tehničke znanosti` i `umjetničko područje`. Najlošije, iako relativno dobro, prepoznaje klasu `društvene znanosti`. Općenito, model jako dobro radi obzirom da su mu i preciznost, odziv i f1-score dobro izbalansirani na otprilike 70%. Model u ovom slučaju je bio sa više ulaznih varijabli.

Model koji je uzimao samo sažetke bio je nešto lošiji, ali je i dalje dosljedno dobro imao klasifikacijski izvještaj:

```py
                             precision    recall  f1-score   support

    biomedicina i zdravstvo       0.75      0.74      0.75       400
    biotehničke znanosti          0.71      0.57      0.63       400
    društvene znanosti            0.59      0.54      0.56       400
    humanističke znanosti         0.67      0.66      0.66       400
    prirodne znanosti             0.59      0.55      0.57       400
    tehničke znanosti             0.59      0.72      0.65       400
    umjetničko područje           0.69      0.80      0.74       400
            accuracy                                  0.66      2800
            macro avg             0.51      0.51      0.51      2800
            weighted avg          0.66      0.66      0.65      2800
```

Model je radio između 5% i 10% lošije nego kad su uvedene i ključne riječi.

### Test modela

![Test modela](Screenshot_2025-01-26_22-48-36.png)

### Izgled sučelja

![Početna stranica](/images/Screenshot_2025-01-26_23-37-17.png)

![Admin stranica](/images/Screenshot_2025-01-26_23-40-23.png)

![Unos dokumenata](/images/Screenshot_2025-01-26_23-38-07.png)

![Pregled dokumenata](/images/Screenshot_2025-01-26_23-37-50.png)

### Izvlačenje podataka

Za izvlačenje podataka iz PDF-a, koristila se biblioteka PyMuPDF, te je osmišljena funkcija koja će učitati PDF te izvući  sažetak i ključne riječi:

```py
def pdf2text(pdf_path):
    word_count = 0
    extracted_keywords = ""
    extracted_sections = {}
    section_titles = ["Sažetak","Summary"]
    section_keywords = ["Ključne riječi", "Keywords"]
    pdf_document = fitz.open(pdf_path)
    
    text_found = False
    keywords_found = False

    with fitz.open(pdf_path) as doc:
        text = chr(12).join([page.get_text() for page in doc])
        word_count = len(text.strip(',.!?:;').split())

    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]
        text = page.get_text()

        if not text_found:
            for title in section_titles:
                if title in text:
                    start_index = text.find(title)
                    section_text = text[start_index:]
                    extracted_sections[title] = section_text
                    text_found = True
                    break

        if not keywords_found:
            for keyword in section_keywords:
                if keyword in text:
                    for line in text.splitlines():
                        if keyword in line:
                            extracted_keywords = line.strip().replace(keyword, "").replace(":", "")
                            keywords_found = True
                            break
        
        if keywords_found and text_found:
            break

    pdf_document.close()
    summary = []
    keywords = []
    summary.append("".join(extracted_sections.values()).replace("\n", " "))
    keywords.append(extracted_keywords)

    return (summary, keywords, word_count)
```

### MLFlow

Zamišljeno je da se koristi i MLFlow, kako bismo servirali modele preko njega i radili pozive na servis, ali kada smo promislili malo i istražili za naš slučaj, i zaključili da nije potrebno servirati tako model jer bi u svakom slučaju trebali prvo preuzeti model sa MLFlow-a i nakon toga ga učitati u aplikaciji što bi vjerovatno opet usporilo rad aplikacije, a obzirom da nismo gradili model preko vlastitih računala nego u Google Colab-u, nije moguće registrirati model u MLFlow-u, već ga samo dodati u log.
