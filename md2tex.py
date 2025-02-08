import markdown2
import pypandoc
import os

def markdown_to_sections(markdown_file):
    with open(markdown_file, 'r', encoding='utf-8') as file:
        markdown_content = file.read()
    
    # Convert markdown to HTML
    html_content = markdown2.markdown(markdown_content)
    
    # Convert HTML to LaTeX using pandoc
    latex_content = pypandoc.convert_text(html_content, 'latex', format='html')
    
    return latex_content

def save_subsections_to_files(latex_content, output_dir):
    # Split the content into subsections
    subsections = latex_content.split('\\subsection')
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    all_tex_content = ''
    
    for i, subsection in enumerate(subsections):
        if subsection.strip():
            subsection_filename = os.path.join(output_dir, f'subsection_{i+1}.tex')
            with open(subsection_filename, 'w', encoding='utf-8') as file:
                if i == 0:
                    file.write(subsection)
                else:
                    file.write('\\subsection' + subsection)
            
            print(f'Subsection {i+1} saved to {subsection_filename}')
            
            # Aggiungi l'input di questa sezione a all.tex
            all_tex_content += f'\\input{{sections/subsection_{i+1}}}\n'
    
    # Salva il contenuto di all.tex
    all_tex_filename = os.path.join(output_dir, 'all.tex')
    with open(all_tex_filename, 'w', encoding='utf-8') as all_tex_file:
        all_tex_file.write(all_tex_content)
    
    print(f'all.tex saved to {all_tex_filename}')

def main():
    markdown_file = './README.md'  # Nome del file Markdown di input
    output_dir = 'sections'   # Directory di output per i file LaTeX
    
    latex_content = markdown_to_sections(markdown_file)
    save_subsections_to_files(latex_content, output_dir)
    print('Conversione completata!')

if __name__ == '__main__':
    main()
