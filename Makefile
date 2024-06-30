# Makefile per compilare il documento LaTeX con XeLaTeX e BibTeX

# Nome del file principale LaTeX (senza l'estensione .tex)
FILENAME ?= main

# Comandi per i tool
LATEX = xelatex
BIBTEX = bibtex

# Opzioni per il compilatore LaTeX
LATEX_OPTIONS = --halt-on-error

# Target predefinito: compila il documento
all: $(FILENAME).pdf

# Regola per compilare il documento LaTeX
$(FILENAME).pdf: $(FILENAME).tex
	$(LATEX) $(LATEX_OPTIONS) $(FILENAME).tex
	$(BIBTEX) $(FILENAME)
	$(LATEX) $(LATEX_OPTIONS) $(FILENAME).tex
	$(LATEX) $(LATEX_OPTIONS) $(FILENAME).tex

# Pulisce i file temporanei generati durante la compilazione
clean:
	rm -f $(FILENAME).aux $(FILENAME).log $(FILENAME).out $(FILENAME).pdf $(FILENAME).toc $(FILENAME).bbl $(FILENAME).blg

# Pulisce completamente i file intermedi e il PDF finale
clean-all:
	rm -f $(FILENAME).aux $(FILENAME).log $(FILENAME).out $(FILENAME).pdf $(FILENAME).toc $(FILENAME).lof $(FILENAME).lot $(FILENAME).bbl $(FILENAME).blg


# Specifica i target che non sono file
.PHONY: all clean clean-all view
