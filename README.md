# Template LaTeX per Tesine di Musica Elettronica del Conservatorio di L'Aquila A. Casella 

Questo repository contiene un template LaTeX per la stesura delle tesine di musica elettronica del Conservatorio A. Casella. Il template è progettato per rispettare le linee guida specifiche del conservatorio riguardo la formattazione dei documenti.

## Struttura del Repository

- `mystyle.sty`: Il file di stile personalizzato che definisce la formattazione del documento.
- `main.tex`: Il file principale del documento LaTeX che utilizza il file di stile.
- `bibliography.bib`: Il file contenente le voci bibliografiche in formato BibTeX.
- `README.md`: Questo file, contenente informazioni su come utilizzare il template.

## Caratteristiche del Template

- Formato carta: A4 (210 x 297 mm).
- Margini: 2,5 cm superiori e inferiori, 2 cm destro e sinistro.
- Numerazione delle pagine: Attivata su tutte le pagine.
- Formattazione della prima pagina: Titolo e riassunto.
- Inizio del contenuto principale: Dalla seconda pagina.
- Titolo della tesina: Arial, corpo 14, grassetto, maiuscolo.
- Altre intestazioni: Arial, corpo 12.
- Titoli delle sezioni: Arial, corpo 12, grassetto, maiuscolo.
- Titoli delle sottosezioni: Arial, corpo 12, corsivo, non maiuscolo.
- Corpo principale del testo: Interlinea singola, margini giustificati, senza indentazione dei paragrafi.
- Note a piè di pagina: Arial, corpo 10.



## Come Utilizzare il Template

1. **Clona il repository o scarica i file**:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Compila il documento:**

- Assicurati di avere una distribuzione LaTeX installata sul tuo sistema (ad esempio, TeX Live o MiKTeX).
- Compila main.tex con il tuo editor LaTeX preferito o da linea di comando:

    ```bash
    xelatex main.tex
    ```

3. **Genera la bibliografia:**
Per generare la bibliografia usando BibTeX, segui questi passaggi:
- Compila il documento con XeLaTeX:
    ```bash
    xelatex main.tex
    ```
- Esegui BibTeX per generare la bibliografia:
    ```bash
    bibtex main.aux
    ```
- Compila nuovamente il documento due volte con XeLaTeX per aggiornare le citazioni e la bibliografia:
    ```bash
    xelatex main.tex
    xelatex main.tex
    ```

## Modifica il contenuto

1. **Apri il file `main.tex`**:
   - Modifica il titolo, il riassunto e il contenuto delle sezioni secondo le tue esigenze.
   - Puoi aggiungere nuove sezioni e sottosezioni seguendo la struttura esistente.

2. **Gestisci la bibliografia con BibTeX**:
   - Crea o modifica il file `bibliography.bib` per includere tutte le voci bibliografiche necessarie nel formato BibTeX.
   - Inserisci le citazioni nel testo utilizzando i comandi LaTeX appropriati (come `\cite{}`).

3. **Compila la bibliografia con BibTeX**:
   - Dopo aver compilato `main.tex` con XeLaTeX o LuaLaTeX, esegui BibTeX per generare la bibliografia.
     ```bash
     bibtex main.aux
     ```
   - Questo comando utilizzerà le citazioni nel documento per estrarre le informazioni bibliografiche dal file `bibliography.bib` e generare correttamente la bibliografia.

4. **Compila nuovamente il documento**:
   - Dopo aver eseguito BibTeX, compila nuovamente `main.tex` due volte con XeLaTeX o LuaLaTeX per aggiornare le citazioni e la bibliografia nel documento finale.
     ```bash
     xelatex main.tex
     xelatex main.tex
     ```

5. **Verifica e revisiona**:
   - Controlla il documento compilato per assicurarti che le citazioni siano correttamente collegate alla bibliografia generata.

Assicurati di seguire questi passaggi per gestire e aggiornare la bibliografia nel tuo documento LaTeX utilizzando BibTeX.

## Dipendenze

Per utilizzare correttamente questo template, assicurati di avere i seguenti pacchetti e strumenti installati:

1. **Distribuzione LaTeX**:
   - Una distribuzione LaTeX completa come TeX Live (consigliato per Linux e macOS) o MiKTeX (consigliato per Windows).

2. **Pacchetti LaTeX**:
   - `geometry`: Per impostare i margini della pagina.
   - `setspace`: Per la gestione dell'interlinea.
   - `titlesec`: Per personalizzare i titoli delle sezioni e delle sottosezioni.
   - `fontspec`: Per impostare il carattere Arial (richiede l'uso di XeLaTeX o LuaLaTeX).
   - `fancyhdr`: Per personalizzare l'intestazione e il piè di pagina.
   - `hyperref`: Per i collegamenti ipertestuali.

### Installazione dei Pacchetti

- Se utilizzi TeX Live, puoi installare i pacchetti richiesti con il seguente comando:

    ```bash
    tlmgr install geometry setspace titlesec fontspec fancyhdr hyperref
    ```
- Se utilizzi MiKTeX, i pacchetti possono essere installati automaticamente alla prima compilazione del documento oppure manualmente tramite il gestore di pacchetti di MiKTeX.
