# Install in terminal one by one
# pip install flask-bootstrap
# pip install flask
# pip install spacy
# pip install PyPDF2

from flask import Flask, request, render_template
import PyPDF2
from PyPDF2 import PdfReader,PdfWriter


# Create the app
app = Flask(__name__)


@app.route('/',methods=['POST','GET'])
def index():
    
    if request.method == 'POST':
        
        text = ''
        
        # Check if files were uploaded
        if 'files[]' in request.files:
            files = request.files.getlist('files[]')
            for file in files:
                # Process PDF Files
                if file.filename.endswith('pdf'):
                    text += process_pdf(file)
                # Process Txt Files
                else:
                    text += file.read().decode('utf-8')
        
        # Get the selected number of questions from the dropdown menu
        num_questions = int(request.form['num_questions'])

    return render_template('index.html')


def process_pdf(file):
    text = ''
    pdf_reader = PdfReader(file)
    for page_number in range(len(pdf_reader.pages)):
        page_text = pdf_reader.pages[page_number].extract_text()
        text += page_text
    return text

# Run the app
if __name__ == '__main__':
    app.run(debug=True)