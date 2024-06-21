# Template LaTeX per Tesine di Musica Elettronica del Conservatorio di L'Aquila A. Casella 

Questo repository contiene un template LaTeX per la stesura delle tesine di musica elettronica del Conservatorio A. Casella. Il template è progettato per rispettare le linee guida specifiche del conservatorio riguardo la formattazione dei documenti.

## Struttura del Repository

- `mystyle.sty`: Il file di stile personalizzato che definisce la formattazione del documento.
- `main.tex`: Il file principale del documento LaTeX che utilizza il file di stile.
- `bibliography.bib`: Il file contenente le voci bibliografiche in formato BibTeX.
- `Makefile`: File GNU make, contenente i targets per la compilazione.
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


6. **For Dummies: Utilizzo di make e make clean**:
Il repository include un Makefile per semplificare il processo di compilazione e gestione del progetto LaTeX. Ecco come utilizzare i comandi principali:

   - **Compilazione del Documento**

        Per compilare il documento LaTeX utilizzando make, segui questi passaggi:

     - Compila il documento principale:

     - Assicurati di trovarti nella directory principale del repository.
        ```bash
        make
        ```
        Questo comando eseguirà la compilazione del documento LaTeX utilizzando xelatex.

        Se necessario, il comando make può essere esplicitamente specificato con il nome del file principale del tuo documento (senza l'estensione .tex), ad esempio make main.
   - **Pulizia del Progetto**
        Per pulire i file temporanei generati durante la compilazione, puoi utilizzare il comando make clean:

      - Pulisci i file temporanei:

        ```bash
        make clean
        ```
        Questo comando rimuoverà i file intermedi e i file ausiliari generati durante la compilazione, come i file .aux, .log, e altri file temporanei.

   - **Personalizzazione**
        Il file Makefile può essere personalizzato per includere altri target o adattarsi alle tue specifiche esigenze di compilazione.

        Assicurati che il file main.tex contenga tutte le configurazioni necessarie per la tua tesina, inclusi i pacchetti e le impostazioni personalizzate.

    Utilizzando make e make clean in questo modo, puoi gestire facilmente la compilazione e la pulizia del tuo progetto LaTeX, mantenendo il tuo ambiente di sviluppo organizzato e efficiente.

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
