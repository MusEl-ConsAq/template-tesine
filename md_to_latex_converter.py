# --- START OF FILE md_to_latex_converter.py ---
import re
import os
from pathlib import Path
import logging
# --- Configurazione ---

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
# Directory di input contenente i file Markdown (.md)
# Assumiamo che lo script sia eseguito dalla directory GRDM-TETDRA-I
# e che i file .md siano direttamente in essa (o in una sottodirectory specificata)
INPUT_DIR_MD = Path("sections_md") # Directory corrente, dove si trovano i file .md
# Se i tuoi file .md fossero in una sottodirectory, ad esempio "markdown_sources":
# INPUT_DIR_MD = Path("markdown_sources")

# Nomi dei file Markdown di input nell'ordine desiderato per le sezioni LaTeX
# Questo ordine verrà usato per generare i file sezioni/sezioneN.tex
# e per l'inclusione in sections/all.tex
MD_FILES_ORDER = [
    "introduzione.md",
    "sezioneI.md",
    "sezioneII.md",
    "sezioneIII.md",
    "sezioneIV.md"
    # Aggiungi qui "conclusione.md" se lo avrai
]

# Directory di output per i file .tex generati
OUTPUT_DIR_TEX = Path("sexons") # Creeremo una nuova cartella per non sovrascrivere la tua 'sections'

# File principale LaTeX e file di stile (per riferimento, non li modifichiamo in questa fase)
MAIN_TEX_FILE = Path("main.tex")
STYLE_FILE = Path("ME_AQ_temp.sty")
BIB_FILE_PATH = Path("bibliography_generated.bib") # Percorso per il file .bib generato

BIB_FILE = Path("bibliography.bib") # Nome per il file .bib generato
ALL_TEX_FILE_GENERATED = OUTPUT_DIR_TEX / "all.tex" # File che includerà tutte le sezioni generate

PERSONA_APPLIED_SET = set()

# Lista predefinita di persone note e loro varianti/dettagli.
# Formato: "Nome Canonico": {"variants": ["Variante 1", "Altro Nome"], "birth": "AAAA", "death": "BBBB"}
# Le varianti devono essere ordinate dalla più lunga/specifica alla più corta.
KNOWN_PEOPLE = {
}

raw_bibliography_notes = {} # { (filename, md_key): "full citation text" }
bibtex_entries = {}         # { bibtex_key: {"type": "...", "fields": {...}} }
markdown_key_to_bibtex_key_map = {} # { (filename, md_key): bibtex_key }

# --- Funzioni di Utility ---
def ensure_dir_exists(path: Path):
    """Assicura che una directory esista, creandola se necessario."""
    path.mkdir(parents=True, exist_ok=True)
    print(f"Directory assicurata: {path}")

def read_md_file(filepath: Path) -> str:
    """Legge il contenuto di un file Markdown."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"Letto file: {filepath}")
        return content
    except FileNotFoundError:
        print(f"ERRORE: File non trovato {filepath}")
        return ""
    except Exception as e:
        print(f"ERRORE: Impossibile leggere il file {filepath}: {e}")
        return ""

def write_tex_file(filepath: Path, content: str):
    """Scrive il contenuto LaTeX in un file .tex."""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Scritto file: {filepath}")
    except Exception as e:
        print(f"ERRORE: Impossibile scrivere il file {filepath}: {e}")

def generate_bibtex_key(authors_str, year_str, title_str):
    """Genera una chiave BibTeX ragionevolmente unica."""
    key_part_author = ""
    if authors_str:
        first_author_surname = authors_str.split(',')[0].split()[-1]
        key_part_author = re.sub(r'[^A-Za-z]', '', first_author_surname)
    
    key_part_year = year_str if year_str else "YYYY"
    
    key_part_title = ""
    if title_str:
        title_words = re.findall(r'\b\w+\b', title_str.lower())
        if title_words:
            key_part_title = title_words[0]
            if len(title_words) > 1: key_part_title += title_words[1][:3] # Prime 3 lettere della seconda parola

    base_key = f"{key_part_author}{key_part_year}{key_part_title}".capitalize()
    
    # Assicura unicità se la base_key è già usata
    final_key = base_key
    counter = 1
    while final_key in bibtex_entries:
        final_key = f"{base_key}{counter}"
        counter += 1
    return final_key

def parse_citation_text(citation_text: str, md_filename: str, md_key: str):
    """
    Tenta di parsare una stringa di citazione in campi BibTeX.
    Questa è una funzione euristica e molto semplificata.
    """
    fields = {}
    bib_type = "misc" # Default type

    # Tentativo di estrarre autori (molto basico)
    # Bernardini, N., "Title"... -> Bernardini, N.
    # Bernardini, N., Pellegrini, A.C., "Title"... -> Bernardini, N. and Pellegrini, A.C.
    author_match = re.match(r"((?:[\w\s\.-]+,\s*[\w\s\.-]+)(?:\s*and\s*[\w\s\.-]+,\s*[\w\s\.-]+)*),", citation_text)
    if not author_match: # Prova formato "Cognome N." senza virgola finale
        author_match = re.match(r"((?:[\w\s\.-]+,\s*[\w\s\.-]+)(?:\s*and\s*[\w\s\.-]+,\s*[\w\s\.-]+)*|\w+\s*\w\.)\s*(?:,|\(|``)", citation_text)

    authors_str = ""
    if author_match:
        authors_str = author_match.group(1).strip()
        # Sostituisci ", " tra autori con " and " se necessario per BibTeX
        # Esempio: "Bernardini, N., Pellegrini, A.C." -> "Bernardini, N. and Pellegrini, A.C."
        # Questo è complesso, per ora prendiamo la stringa così com'è
        fields["author"] = authors_str

    # Tentativo di estrarre titolo tra virgolette
    title_match = re.search(r'["“](.+?)["”]', citation_text)
    title_str = ""
    if title_match:
        title_str = title_match.group(1)
        fields["title"] = title_str

    # Tentativo di estrarre l'anno (4 cifre)
    year_match = re.search(r'\b(\d{4})\b', citation_text)
    year_str = ""
    if year_match:
        year_str = year_match.group(1)
        fields["year"] = year_str

    # Tentativo di estrarre pagine (p. X, pp. X-Y)
    pages_match = re.search(r'[,\s](?:p|pp)\.?\s*([\d\-]+)', citation_text)
    if pages_match:
        fields["pages"] = pages_match.group(1)

    # Inferenza del tipo di BibTeX (molto euristica)
    if "Proceedings of" in citation_text or "Conference" in citation_text:
        bib_type = "inproceedings"
        booktitle_match = re.search(r'(?:in|in:)\s*\*?([\w\s:,]+?)(?:\*?,\s*(?:edited|Copenhagen|Berlin))', citation_text, re.IGNORECASE)
        if booktitle_match: fields["booktitle"] = booktitle_match.group(1).strip().replace("*","")
        if "Copenhagen" in citation_text: fields["address"] = "Copenhagen"
        if "International Computer Music Association" in citation_text: fields["publisher"] = "International Computer Music Association"

    elif "edited by" in citation_text or "in:" in citation_text and "Springer" in citation_text : # Assumendo che 'in:' seguito da libro sia InCollection
        bib_type = "incollection"
        # Estrai booktitle e editor
        booktitle_match = re.search(r'(?:in|in:)\s*\*?(.+?)(?:\*?,\s*(?:edited by|Berlin))', citation_text, re.IGNORECASE)
        if booktitle_match: fields["booktitle"] = booktitle_match.group(1).strip().replace("*","")
        
        editor_match = re.search(r'edited by\s+([^,]+)', citation_text, re.IGNORECASE)
        if editor_match: fields["editor"] = editor_match.group(1).strip()
        if "Springer" in citation_text : fields["publisher"] = "Springer"
        if "Berlin" in citation_text : fields["address"] = "Berlin"


    elif "Journal" in citation_text: # Es. Computer Music Journal
        bib_type = "article"
        journal_match = re.search(r'([A-Za-z\s]+ Journal)', citation_text)
        if journal_match: fields["journal"] = journal_match.group(1).strip()
        
        volume_match = re.search(r',\s*(\d+)\(\d+\)', citation_text) # es. , 18(4)
        if volume_match: fields["volume"] = volume_match.group(1)
        
        number_match = re.search(r'\((\d+)\)', citation_text) # es. (4)
        if number_match and "volume" in fields : # Assicurati che sia il numero, non parte di (1994)
            # Cerca un numero tra parentesi che non sia l'anno
            num_search = re.search(r'\((\d+)\)(?!,)', citation_text) # es. 18(4),
            if num_search and num_search.group(1) != fields.get("year"):
                 fields["number"] = num_search.group(1)

    # Gestione di Ibid. e cit.
    is_ibid = citation_text.lower().startswith("ibid.")
    is_cit = ", cit." in citation_text.lower()

    if is_ibid or is_cit:
        # Trova la chiave della nota precedente nello stesso file
        # Questo richiede che le note siano numerate sequenzialmente o che md_key sia un numero
        try:
            prev_md_key_num = int(md_key) - 1
            if prev_md_key_num > 0:
                prev_md_tuple_key = (md_filename, str(prev_md_key_num))
                if prev_md_tuple_key in markdown_key_to_bibtex_key_map:
                    bibtex_key_ref = markdown_key_to_bibtex_key_map[prev_md_tuple_key]
                    # Per Ibid e cit., non creiamo una nuova voce, ma mappiamo alla precedente
                    # e potenzialmente aggiorniamo le pagine se specificate
                    if pages_match: # Se Ibid., p. X
                        # Dobbiamo memorizzare questa informazione di pagina per la sostituzione \cite
                        # Non lo facciamo qui direttamente, ma la funzione di sostituzione \cite dovrà gestirlo
                        pass
                    logging.info(f"Risolto {'Ibid.' if is_ibid else 'cit.'} per ({md_filename}, {md_key}) a {bibtex_key_ref}")
                    return bibtex_key_ref, None, None # Restituisce la chiave esistente
        except ValueError:
            logging.warning(f"Impossibile risolvere Ibid./cit. per chiave non numerica: {md_key}")
        except Exception as e:
            logging.warning(f"Errore risoluzione Ibid./cit. per ({md_filename}, {md_key}): {e}")
    
    # Se non è Ibid/cit o non risolto, genera nuova chiave
    bibtex_key = generate_bibtex_key(authors_str, year_str, title_str)
    return bibtex_key, bib_type, fields

# --- START OF REVISED FUNCTION collect_and_parse_bibliography ---
def collect_and_parse_bibliography(md_files_dict: dict):
    """
    Passo 1: Colleziona tutte le note bibliografiche, filtrando via le "Trascrizioni".
    Passo 2: Parsale e crea le voci BibTeX.
    """
    global raw_bibliography_notes, bibtex_entries, markdown_key_to_bibtex_key_map
    raw_bibliography_notes.clear()
    bibtex_entries.clear()
    markdown_key_to_bibtex_key_map.clear()

    # Passo 1: Colleziona tutte le note [^key]: text da tutti i file,
    # escludendo quelle identificate come "Trascrizione".
    temp_raw_notes_for_bib = {} # Usiamo un dizionario temporaneo per le note valide
    for md_filename, md_content in md_files_dict.items():
        # Trova tutte le definizioni di note [^key]: testo
        matches = re.findall(r"\[\^(\w+)\]:\s*(.+)", md_content)
        for key, text_content_of_note in matches:
            # Filtra esplicitamente le note "Trascrizione"
            if "trascrizione" in text_content_of_note.lower():
                logging.info(f"BIB_FILTER: Esclusa nota Trascrizione '[^{key}]' dal file '{md_filename}' per il BibTeX.")
                # Opzionale: potremmo voler comunque mappare questa chiave a un valore speciale
                # se la funzione `replace_markdown_citations_in_text` dovesse comportarsi
                # diversamente per le trascrizioni (ma attualmente le rimuove `remove_transcription_citations`)
                continue # Salta questa nota, non la considerare per il BibTeX

            # Se non è una trascrizione, aggiungila per il processamento BibTeX
            temp_raw_notes_for_bib[(md_filename, key.strip())] = text_content_of_note.strip()
    
    # Ora raw_bibliography_notes conterrà solo le note valide per il BibTeX
    raw_bibliography_notes = temp_raw_notes_for_bib

    # Passo 2: Parsa le note raccolte (e filtrate) e risolvi Ibid/cit.
    # Ordina le note per file e poi per chiave (assumendo che le chiavi siano numeriche per Ibid.)
    # per aiutare con la risoluzione di Ibid.
    # Usiamo raw_bibliography_notes che ora è già filtrato
    sorted_valid_notes = sorted(raw_bibliography_notes.items(), key=lambda item: (item[0][0], int(item[0][1]) if item[0][1].isdigit() else item[0][1]))

    for (md_filename, md_key), citation_text in sorted_valid_notes:
        bib_key_or_ref, bib_type, fields = parse_citation_text(citation_text, md_filename, md_key)
        
        current_map_key = (md_filename, md_key) # Chiave della nota Markdown originale

        if fields is not None: # È una nuova voce BibTeX da creare/referenziare
            # bib_key_or_ref è la chiave BibTeX generata
            if bib_key_or_ref not in bibtex_entries: 
                bibtex_entries[bib_key_or_ref] = {
                    "type": bib_type, 
                    "fields": fields, 
                    "original_text": citation_text # Conserviamo il testo originale per debug/note
                }
            # Mappa sempre la nota Markdown alla chiave BibTeX (nuova o esistente se `cit.` puntava lì)
            markdown_key_to_bibtex_key_map[current_map_key] = bib_key_or_ref

        elif bib_key_or_ref is not None: # È un riferimento (Ibid./cit.) a una chiave BibTeX esistente
            # bib_key_or_ref è la chiave BibTeX a cui Ibid./cit. si riferisce
            markdown_key_to_bibtex_key_map[current_map_key] = bib_key_or_ref
        else:
            # Caso in cui parse_citation_text non restituisce né fields né una bib_key_or_ref
            # (dovrebbe essere raro se la logica di parse_citation_text è completa)
            logging.warning(f"Impossibile processare la nota ({md_filename}, {md_key}): {citation_text[:50]}... Nessuna azione BibTeX intrapresa.")
            
    logging.info(f"Raccolte {len(raw_bibliography_notes)} note bibliografiche valide per il BibTeX (dopo filtro Trascrizioni).")
    logging.info(f"Generate {len(bibtex_entries)} voci BibTeX uniche.")
# --- END OF REVISED FUNCTION collect_and_parse_bibliography ---

def write_bibtex_file():
    """Scrive il file .bib con le voci raccolte."""
    if not bibtex_entries:
        logging.info("Nessuna voce BibTeX da scrivere.")
        return

    content = "@Comment{Questo file BIB è stato generato automaticamente dallo script Python.}\n\n"
    for key, entry_data in bibtex_entries.items():
        content += f"@{entry_data['type']}{{{key},\n"
        for field, value in entry_data["fields"].items():
            # Pulisci il valore da eventuali caratteri LaTeX problematici o aggiungi graffe
            # Esempio: titoli con due punti o caratteri speciali
            # value_cleaned = value.replace("{", "\\{").replace("}", "\\}")
            content += f"  {field:<10} = {{{value}}},\n"
        content += f"  note        = {{Orig: {entry_data['original_text'][:50]}...}}\n" # Nota per debug
        content += "}\n\n"
    
    try:
        with open(BIB_FILE_PATH, 'w', encoding='utf-8') as f:
            f.write(content)
        logging.info(f"Scritto file BibTeX: {BIB_FILE_PATH}")
    except Exception as e:
        logging.error(f"Impossibile scrivere il file BibTeX {BIB_FILE_PATH}: {e}")

def replace_markdown_citations_in_text(text: str, md_filename_current_processing: str) -> str:
    """Sostituisce [^key] e [^key, p. X] con cite{bib_key} o cite[p.X]{bib_key}."""
    
    def replacer_logic(match_obj):
        md_key = match_obj.group("key")
        pages_arg_text = match_obj.group("pages_text") # Questo è il testo completo ", p. XXX" o None
        
        map_tuple = (md_filename_current_processing, md_key)
        
        if map_tuple in markdown_key_to_bibtex_key_map:
            bibtex_key = markdown_key_to_bibtex_key_map[map_tuple]
            
            page_info_for_cite = ""
            if pages_arg_text:
                # Estrai solo la parte dopo ", " es. "p. XXX"
                page_info_for_cite = pages_arg_text.strip(", ") 
            else:
                # Se non ci sono pagine nel richiamo, controlla se la nota originale (Ibid/cit) le aveva
                original_note_text = raw_bibliography_notes.get(map_tuple, "")
                if "Ibid." in original_note_text or ", cit." in original_note_text:
                    ibid_pages_match = re.search(r'[,\s](p|pp)\.?\s*([\d\-]+)', original_note_text)
                    if ibid_pages_match:
                        page_info_for_cite = f"{ibid_pages_match.group(1)}. {ibid_pages_match.group(2)}" # es. "p. 123"

            if page_info_for_cite:
                return f"\\cite[{page_info_for_cite}]{{{bibtex_key}}}"
            else:
                return f"\\cite{{{bibtex_key}}}"
        else:
            logging.warning(f"Nessuna chiave BibTeX trovata per la nota Markdown ({md_filename_current_processing}, {md_key}). Lasciato invariato: {match_obj.group(0)}")
            return match_obj.group(0) # Lascia invariato se non trovato

    # Regex unica che cattura:
    # - [^key]
    # - [^key, p. NNN]
    # - [^key, pp. NNN-MMM]
    # Il gruppo (?P<pages_text>...) è opzionale.
    # (?!:) è un negative lookahead per assicurarsi che non stiamo matchando una definizione di nota [^key]:
    citation_pattern = re.compile(
        r"\[\^(?P<key>\w+)"                             # Cattura la chiave, es. [^123
        r"(?P<pages_text>,\s*(?:p|pp)\.?\s*[\d\-]+)?"   # Opzionalmente cattura la parte delle pagine, es. , p. 123
        r"\](?!:)"                                      # Chiusura parentesi, non seguita da :
    )
    
    processed_text = citation_pattern.sub(replacer_logic, text)
    
    logging.info(f"    - Sostituite citazioni Markdown con \\cite per {md_filename_current_processing}")
    return processed_text

def remove_transcription_citations(text: str) -> str:
    """Rimuove le citazioni del tipo [^N]: Trascrizione ... e i loro richiami."""
    # Prima, trova tutti i 'key' delle note "Trascrizione"
    transcription_note_keys = re.findall(r"\[\^(\w+)\]:\s*Trascrizione.*", text, flags=re.IGNORECASE) # Aggiunto IGNORECASE
    
    # Rimuovi le definizioni delle note "Trascrizione"
    text = re.sub(r"\[\^(\w+)\]:\s*Trascrizione.*\n?", "", text, flags=re.IGNORECASE) # Aggiunto IGNORECASE
    
    # Rimuovi i richiami a queste note nel testo
    for key in transcription_note_keys:
        # Rimuove [^key] o [^key, dettagli]
        text = re.sub(rf"\[\^{re.escape(key)}(?:,[^\]]*)?\]", "", text)
        
    print("    - Rimosse citazioni 'Trascrizione...' e loro definizioni dal testo LaTeX")
    return text

def convert_headings(text: str) -> str:
    text = re.sub(r"^\s*###\s*\*\*[\d\.]*\s*(.*?)\*\*\s*$", r"\\subsection{\1}", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*##\s*\*\*[\d\.]*\s*(.*?)\*\*\s*$", r"\\section{\1}", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*#\s*\*\*(.*?)\*\*\s*$", r"\\section{\1}", text, flags=re.MULTILINE)
    logging.info("    - Convertiti i titoli")
    return text

def convert_emphasis_quotes(text: str) -> str:
    text = re.sub(r'"(.*?)"', r"''\1''", text)
    logging.info("    - Convertite virgolette doppie in virgolette LaTeX")
    return text

def convert_numbered_lists(text: str) -> str:
    """Converte elenchi numerati Markdown in ambiente enumerate LaTeX."""
    # Cerca blocchi di elenchi numerati
    processed_text = []
    in_list = False
    for line in text.splitlines():
        match = re.match(r"^\s*(\d+)\.\s+(.*)", line)
        if match:
            item_content = match.group(2)
            # Semplice gestione del grassetto negli item (es. 1. **Titolo**: testo)
            item_content = re.sub(r"\*\*(.*?)\*\*", r"\\textbf{\1}", item_content)
            if not in_list:
                processed_text.append("\\begin{enumerate}")
                in_list = True
            processed_text.append(f"    \\item {item_content}")
        else:
            if in_list:
                processed_text.append("\\end{enumerate}")
                in_list = False
            processed_text.append(line)
    
    if in_list: # Chiudi l'elenco se il file finisce con esso
        processed_text.append("\\end{enumerate}")
        
    logging.info("    - Convertiti elenchi numerati")
    return "\n".join(processed_text)


def manage_paragraphs(text: str) -> str:
    """Assicura la corretta spaziatura tra paragrafi per LaTeX."""
    # In LaTeX, i paragrafi sono separati da una o più righe vuote.
    # Il template usa \setlength{\parskip}{\baselineskip} e \setlength{\parindent}{0pt},
    # quindi una riga vuota tra i paragrafi nel sorgente .tex è sufficiente.
    # Questa funzione si assicura che multiple righe vuote nel Markdown
    # diventino una singola riga vuota nel LaTeX (per pulizia).
    # E che i newline singoli diventino spazi (comportamento standard MD -> LaTeX).
    
    lines = text.splitlines()
    processed_lines = []
    for i, line in enumerate(lines):
        if not line.strip(): # Riga vuota
            if processed_lines and processed_lines[-1].strip(): # Aggiungi solo se la precedente non era vuota
                processed_lines.append("")
        else:
            # Se la riga precedente non era un comando di sezione/lista e questa non inizia un comando
            # e la riga precedente terminava con testo (non era vuota),
            # allora il newline singolo in MD dovrebbe essere uno spazio (a meno che non sia fine paragrafo)
            # Questa logica è complessa e spesso gestita meglio da parser Markdown completi.
            # Per ora, manteniamo i newline, il template gestisce \parskip.
            processed_lines.append(line)
            
    # Un approccio più semplice: collassa multiple righe vuote a una singola riga vuota.
    text = re.sub(r"(\n\s*){2,}", "\n\n", text)
    logging.info("    - Gestiti i paragrafi (collassate righe vuote multiple)")
    return text


def apply_persona_command(text: str) -> str:
    """Applica il comando \persona alle persone note, solo la prima volta."""
    global PERSONA_APPLIED_SET # Riferimento allo stato globale
    
    processed_text = text
    
    # Itera attraverso le persone note
    for canonical_name, details in KNOWN_PEOPLE.items():
        birth = details.get("birth", "0000")
        death = details.get("death", "9999")
        
        # Itera attraverso le varianti del nome, dalla più lunga alla più corta
        for variant in sorted(details["variants"], key=len, reverse=True):
            # Cerca la variante esatta nel testo. Usiamo \b per word boundaries.
            # Dobbiamo fare attenzione a non sostituire parzialmente (es. "Bernardini" dentro "Prof. Nicola Bernardini")
            # Lo facciamo processando le varianti più lunghe prima.
            
            # Costruisci la regex per trovare la variante, assicurandoti che non sia già parte di un comando LaTeX
            # Questo è per evitare di processare \persona{Giacinto Scelsi} di nuovo.
            # La regex negativa lookbehind (?<!\\persona{) è un po' limitata in Python standard re.
            # Semplifichiamo: se troviamo il nome e il canonico non è in PERSONA_APPLIED_SET, lo sostituiamo.
            # Poi aggiungiamo a PERSONA_APPLIED_SET. Se è già dentro, non facciamo nulla per \persona.

            # Pattern per trovare la variante
            # Usare re.escape per i caratteri speciali nel nome (es. "Prof.")
            pattern = r"\b" + re.escape(variant) + r"\b"
            
            # Funzione di sostituzione per re.sub
            def replace_with_persona(match):
                global PERSONA_APPLIED_SET
                matched_text = match.group(0) # Il testo completo che ha matchato
                
                if canonical_name not in PERSONA_APPLIED_SET:
                    PERSONA_APPLIED_SET.add(canonical_name)
                    print(f"    - Applicato \\persona per {canonical_name} (variante: {variant})")
                    return f"\\persona{{{canonical_name}}}{{{birth}}}{{{death}}}"
                else:
                    # Se già "personato", restituisci il testo originale (o il nome canonico, se la variante è diversa)
                    # Per semplicità, restituiamo il testo matchato originale.
                    # Questo significa che "Prof. Nicola Bernardini" rimane tale se \persona è già stato applicato
                    # a "Bernardini". Potremmo volerlo normalizzare al nome canonico.
                    # Ma il tuo template \persona non influenza la visualizzazione oltre la prima volta.
                    return matched_text 

            processed_text = re.sub(pattern, replace_with_persona, processed_text)

    # todo: Aggiungere una seconda passata per identificare persone non in KNOWN_PEOPLE
    # usando pattern come "Nome Cognome (AAAA-BBBB)" o "Nome Cognome [A-Z][a-z]+ [A-Z][a-z]+".
    # Questo è più complesso e soggetto a falsi positivi.

    logging.info("    - Tentativo di applicazione comando \\persona")
    return processed_text

def process_markdown_content(md_content: str, md_filename_for_this_content: str, section_index: int, is_first_section: bool) -> str:
    logging.info(f"Processando contenuto per la sezione {section_index} ({md_filename_for_this_content})...")
    
    latex_content = md_content
    
    # Fase 2 e precedenti:
    latex_content = remove_transcription_citations(latex_content) # Rimuove anche i richiami, non solo le definizioni
    latex_content = convert_headings(latex_content)
    latex_content = convert_numbered_lists(latex_content)
    latex_content = convert_emphasis_quotes(latex_content)
    
    # Fase 3:
    latex_content = apply_persona_command(latex_content)
    
    # Fase 4: Sostituisci i richiami bibliografici [^key] con \cite{bib_key}
    # Questa deve avvenire DOPO la rimozione delle trascrizioni (che rimuove anche i loro richiami)
    # e DOPO la raccolta bibliografica globale.
    latex_content = replace_markdown_citations_in_text(latex_content, md_filename_for_this_content)

    # Pulizia finale dei paragrafi e rimozione delle definizioni di note bibliografiche rimaste (quelle non-trascrizione)
    latex_content = re.sub(r"\[\^(\w+)\]:\s*.+\n?", "", latex_content) # Rimuove tutte le definizioni di note rimaste
    latex_content = manage_paragraphs(latex_content)
    
    latex_content = f"% --- Contenuto LaTeX autogenerato da {md_filename_for_this_content} (sezione {section_index}) ---\n\n" + latex_content
    return latex_content

# --- Script Principale (logica di naming e generazione all.tex aggiornata) ---
def main():
    logging.info("Avvio conversione Markdown -> LaTeX...")
    ensure_dir_exists(OUTPUT_DIR_TEX)
    global PERSONA_APPLIED_SET
    PERSONA_APPLIED_SET.clear() # Resetta lo stato all'inizio di ogni esecuzione completa

    # Carica tutti i contenuti Markdown in un dizionario per la raccolta bibliografica
    all_md_contents = {}
    for md_filename_str in MD_FILES_ORDER:
        md_filepath = INPUT_DIR_MD / md_filename_str
        content = read_md_file(md_filepath)
        if content:
            all_md_contents[md_filename_str] = content
    # Passo 1 della Fase 4: Colleziona e parsa TUTTA la bibliografia da TUTTI i file
    collect_and_parse_bibliography(all_md_contents)
    
    # Passo 2 della Fase 4: Scrivi il file .bib
    write_bibtex_file()


    generated_tex_filenames_for_all_tex = []

    for i, md_filename_str in enumerate(MD_FILES_ORDER):
        if md_filename_str not in all_md_contents:
            logging.warning(f"Salto {md_filename_str} perché non è stato letto correttamente.")
            continue
        
        current_md_content = all_md_contents[md_filename_str]
        base_name_md = Path(md_filename_str).stem.lower()
        tex_filename_out = ""
        
        is_intro = (i == 0 and base_name_md == "introduzione")
        is_concl = (i == len(MD_FILES_ORDER) - 1 and base_name_md == "conclusione")

        if is_intro:
            tex_filename_out = "introduzione.tex"
        elif is_concl:
            tex_filename_out = "conclusione.tex"
        else:
            section_num_if_intro_exists = i 
            section_num_if_no_intro = i + 1
            if MD_FILES_ORDER and Path(MD_FILES_ORDER[0]).stem.lower() == "introduzione":
                current_section_number_for_file = section_num_if_intro_exists
            else:
                current_section_number_for_file = section_num_if_no_intro
            tex_filename_out = f"sezione{current_section_number_for_file}.tex"

        latex_output_path = OUTPUT_DIR_TEX / tex_filename_out
        generated_tex_filenames_for_all_tex.append(tex_filename_out)

        # Ora processa il contenuto del singolo file per le conversioni testuali
        # Passa md_filename_str per permettere a replace_markdown_citations_in_text di sapere il contesto del file
        latex_content = process_markdown_content(current_md_content, md_filename_str, i + 1, is_first_section=(i==0))
        write_tex_file(latex_output_path, latex_content)

    if generated_tex_filenames_for_all_tex:
        all_tex_content_final = f"% --- File di inclusione generato automaticamente ---\n"
        for fname in generated_tex_filenames_for_all_tex:
            all_tex_content_final += f"\\input{{{OUTPUT_DIR_TEX}/{fname}}}  % Auto-generated: include {fname}\n"
        write_tex_file(OUTPUT_DIR_TEX / "all.tex", all_tex_content_final)
        logging.info(f"Generato file di inclusione: {OUTPUT_DIR_TEX / 'all.tex'}")
    else:
        logging.info("Nessun file .tex generato, quindi 'all.tex' non è stato creato.")

    logging.info(f"Conversione terminata. Persone processate con \\persona: {PERSONA_APPLIED_SET}")
    logging.info(f"Mappa da chiavi Markdown a BibTeX: {markdown_key_to_bibtex_key_map}")


if __name__ == "__main__":
    main()
# --- END OF FILE md_to_latex_converter.py ---