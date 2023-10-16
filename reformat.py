import re
import pinyin
import pinyin.cedict as cedict


INPUT_FILE  = 'Your text file here'
OUTPUT_FILE = 'A new HTML file will go here'
ENCODING = 'utf-8'
NEW_CHAPTER_PATTERN = None
NEW_PARAGRAPH_PATTERN = re.compile(r'(?<=\n\n)(.*?)\n\n', re.DOTALL)
# Use the following pattern to split the text into sentences
# NEW_PARAGRAPH_PATTERN = re.compile(r'(?<=\n\n)(.*?[。！？])(?=\n\n)', re.DOTALL)


# Customize the document style and formatting here
CSS_STYLE = '''
<style>

/* Import Google Fonts here if you desire */
@import url('https://fonts.googleapis.com/css?family=Ma+Shan+Zheng&display=swap');
@import url('https://fonts.googleapis.com/css?family=Noto+Sans+SC&display=swap');
@import url('https://fonts.googleapis.com/css?family=Poppins&display=swap');

table {
    align: center;
    width: 100%;
}

.th, .td {
    border: 0px transparent;
    padding: 0px;
}

/* Dictionary: Chinese entries */
td.zh {
    color: black;
    font-family: "Noto Sans SC", sans-serif;
    width: 60px;
    font-size: 12px;
}

/* Dictionary: PinYin entries */
td.py {
    color: red;
    width: 80px;
    font-family: "Poppins", sans-serif;
    font-size: 8px;
}

/* Dictionary: English entries */
td.en {
    color: blue;
    font-family: "Poppins", sans-serif;
    font-size: 8px;
}

/* Original paragraph texts */
h3 {
    font-size: 24px;
    font-family: "Ma Shan Zheng", sans-serif;
}

/* Chapter numbers */
h1 {
    font-size: 24px;
    font-family: "Ma Shan Zheng", sans-serif;
}
            
.entry_table{
    width: 100%;
    -moz-column-width:4em;
    column-width:4em;
    -moz-column-gap:0;
    column-gap:0;
    -moz-column-rule:solid 1px;
    column-rule:solid 1px;
}
.container {
    display: flex; /* or inline-flex */
    width: 100%;
    flex-wrap: wrap;
    align-items: stretch;
            
}
.entry{
    display: flex;
            width: 50%;
    flex: 1;
}

/* Format in two columns for printing */
@media print
{
    table { page-break-after:auto; page-break-before:auto; }
    tr    { page-break-after:auto; page-break-before:auto; }
    td    { page-break-after:auto; page-break-before:auto; }
    div   { page-break-after:auto; page-break-before:auto; }
    thead { display:table-header-group }
    tfoot { display:table-footer-group }
    body{
        column-count: 2;
        -webkit-column-count: 2;
        -moz-column-count: 2;
    }
}

</style>
'''


def translate_paragraph(paragraph):
    words = []
    current_word = ""
    current_translation = None

    for char in paragraph:
        new_word = current_word + char
        new_translation = cedict.translate_word(new_word)

        if new_translation is None:
            if current_translation is not None:
                word_entry = {
                    'characters': current_word,
                    'pinyin': pinyin.get(current_word),
                    'english_approximations': current_translation
                }
                words.append(word_entry)

            # end of if current_translation is not None:
            new_word = char
            new_translation = cedict.translate_word(new_word)

            if new_translation is None:
                new_word = ""
                new_translation = None

            # end of if new_translation is None:

        # end of if new_translation is None:
        current_translation = new_translation
        current_word = new_word

    # end of for char in paragraph:

    if current_translation is not None:
        word_entry = {
            'characters': current_word,
            'pinyin': pinyin.get(current_word),
            'english_approximations': current_translation
        }
        words.append(word_entry)

    # end of if current_translation is not None:
    return words

# end of translate_paragraph(paragraph):

def convert_paragraph_to_dict(paragraph):
    return {
        'text': paragraph,
        'words': translate_paragraph(paragraph)
    }

def find_unique_words(book):
    '''
    Create a set to store unique Chinese characters within each paragraph
    Iterate through book_data and remove repeating words based on Chinese characters
    '''
    seen_chars = set()  # Set to track seen Chinese characters
    for chapter in book:
        seen_chars.clear()  # Set to track seen Chinese characters
        for paragraph in chapter['paragraphs']:
            unique_words = []  # List to store unique words in each paragraph
            for word in paragraph['words']:
                chinese_chars = word['characters']
                if chinese_chars not in seen_chars:
                    unique_words.append(word)
                    seen_chars.add(chinese_chars)

                # end of for word in paragraph['words']:

            # end of for word in paragraph['words']:
            paragraph['unique_words'] = unique_words

        # end of for paragraph in chapter['paragraphs']:

    # end of for chapter in book:
    return book

# end of find_unique_words(book):


def generate_html(chapters):
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as html_file:
        html_file.write(f'''
        <!DOCTYPE HTML PUBLIC '-//W3C//DTD HTML 4.01 Transitional//EN' 'http://www.w3.org/TR/html4/loose.dtd'>
        <html>
        {CSS_STYLE}
        <head>
            <title>Colored Text Table</title>
            <meta http-equiv='Content-Type' content='text/html; charset=utf-8'/>
        </head>
        <body>
        ''')

        for chapter in chapters:
            chapter_name = chapter['name']
            chapter_number = chapter['number']
            if NEW_CHAPTER_PATTERN is not None:
                html_file.write(f'<h1>Chapter {chapter_number}: {chapter_name}</h1>')

            for word in convert_paragraph_to_dict(chapter_name)['words']:
                chinese_chars = word['characters']
                py = word['pinyin']
                english_approximations = ' | '.join(word['english_approximations'])
                html_file.write(f"<table><tr><td class='zh'>{chinese_chars}</td><td class='py'>{py}</td><td class='en'>{english_approximations}</td></tr></table>")

            for paragraph in chapter['paragraphs']:
                chinese_chars_combined = paragraph['text']
                html_file.write(f"<div class='paragraph'><h3>{chinese_chars_combined}</h3>")

                for word in paragraph['unique_words']:
                    chinese_chars = word['characters']
                    py = word['pinyin']
                    english_approximations = ' | '.join(word['english_approximations'])
                    html_file.write(f"<table><tr><td class='zh'>{chinese_chars}</td><td class='py'>{py}</td><td class='en'>{english_approximations}</td></tr></table>")
                
                # end of for word in paragraph['unique_words']:
                html_file.write("</div>")

            # end of for paragraph in chapter['paragraphs']:

        # end of for chapter in chapters:
        html_file.write("</body></html>")

    # end of with open('santi-short.html', 'w', encoding='utf-8') as html_file:
    print(f"HTML document '{OUTPUT_FILE}' has been created.")

# end of generate_html(chapters):

def main():
    # Read the text document
    with open(INPUT_FILE, 'r', encoding=ENCODING) as file:
        text = file.read()

    # Define regular expressions to match chapters and paragraphs
    chapter_pattern = NEW_CHAPTER_PATTERN
    paragraph_pattern = NEW_PARAGRAPH_PATTERN

    # Initialize data structures to store the book's content
    book = []
    current_chapter = None

    # Split the text into chapters using regular expressions
    if NEW_CHAPTER_PATTERN is None:
        chapters = (1, 1, "The Whole Text", text)
    else:
        chapters = chapter_pattern.split(text)

    # Iterate through the chapters and extract paragraphs
    for i in range(1, len(chapters), 3):
        chapter_number = int(chapters[i])
        chapter_name = chapters[i + 1].strip()
        chapter_text = chapters[i + 2].strip()

        paragraphs = paragraph_pattern.findall(chapter_text)

        current_chapter = {
            'number': chapter_number,
            'name': chapter_name,
            'paragraphs': [convert_paragraph_to_dict(paragraph) for paragraph in paragraphs]
        }

        book.append(current_chapter)

    # end of for i in range(1, len(chapters), 3):
    book = find_unique_words(book)

    # Process and generate HTML
    generate_html(book)

# end of main():

if __name__ == "__main__":
    main()
