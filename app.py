# Install in terminal one by one
# pip install flask-bootstrap
# pip install flask
# pip install spacy
# pip install PyPDF2

from flask import Flask, request, render_template
import PyPDF2
from PyPDF2 import PdfReader,PdfWriter
import spacy
from collections import Counter
import random
from flask_bootstrap import Bootstrap


# Create the app
app = Flask(__name__)
Bootstrap(app)

# Load English tokenizer, tagger, parser, NER, and word vectors
nlp = spacy.load("en_core_web_sm")


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

        # Generate the MCQs (Pass the selected number of questions)
        mcqs = generate_mcqs(text, num_questions=num_questions)
        
        # Ensure each MCQ is formatted correctly as (question_stem, answer_choices, correct_answer)
        mcqs_with_index = [(i + 1, mcq) for i, mcq in enumerate(mcqs)]
        
        return render_template('mcqs.html', mcqs=mcqs_with_index)

    return render_template('index.html')


def process_pdf(file):
    text = ''
    pdf_reader = PdfReader(file)
    for page_number in range(len(pdf_reader.pages)):
        page_text = pdf_reader.pages[page_number].extract_text()
        text += page_text
    return text

def generate_mcqs(input_text, num_questions = 5):

    if input_text is None:
        return []

    # Process the input text
    doc = nlp(input_text)

    # Extract the sentences
    sentences = [sentence.text for sentence in doc.sents]

    # Initialize the multiple choice questions tuples array
    mcqs = []

    # Choose random sentences for questions
    # The number of chosen sentences = num_questions
    selected_sentences = random.sample(sentences, (min(num_questions,len(sentences))))
    
    # Generate MCQs for each selected sentence
    for sentence in selected_sentences:
        
        # Convert the sentence to lower case
        sentence = sentence.lower()
        
        # Process the sentence with the spacy model to get a Doc object
        sentence_doc = nlp(sentence)
        
        # Extract nouns from the sentence
        nouns = [token.text for token in sentence_doc if token.pos_ == 'NOUN']
        
        # If there are fewer than 2 nouns, skip this sentence
        if len(nouns) < 2:
            continue
    
        # Count the frequency of each noun in the sentence
        noun_counts = Counter(nouns)
    
        # If there are any nouns counted
        if noun_counts:
            # Select the most common noun as the subject
            subject = noun_counts.most_common(1)[0][0]
            # Initialize the list of answer choices with the subject as the correct answer
            answer_choices = [subject]
            # Create the question stem by replacing the subject with a blank
            question_stem = sentence.replace(subject, "_____________")

            
            # Add distractors to the answer choices
            while len(answer_choices) < 4:
                distractor = random.choice(list(set(nouns) - set(answer_choices)))
                if distractor not in answer_choices:
                    answer_choices.append(distractor)
                
                # If we run out of unique nouns, add a random filler word
                if len(answer_choices) < 4 and len(set(nouns) - set(answer_choices)) == 0:
                    filler_word = random.choice(['apple', 'banana', 'car', 'dog'])
                    if filler_word not in answer_choices:
                        answer_choices.append(filler_word)
    
            # Shuffle the answer choices
            random.shuffle(answer_choices)
            # Determine the correct answer's position in the shuffled list
            correct_answer = chr(64 + answer_choices.index(subject) + 1)
            # Add the question, answer choices, and correct answer to the list of MCQs
            mcqs.append((question_stem, answer_choices, correct_answer))

    return mcqs

# Run the app
if __name__ == '__main__':
    app.run(debug=True)