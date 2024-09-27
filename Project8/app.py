import pandas as pd
from flask import Flask, render_template, jsonify, request, redirect
import csv

app = Flask(__name__)

def read_csv(file_path):
    return pd.read_csv(file_path)

@app.route('/')
def index():
    titles_df = read_csv('data.csv')
    titles = titles_df.to_dict(orient='records')

    # Read vocab from vocab.csv to count entries per title_id
    vocab_df = read_csv('vocab.csv')

    # Count the number of vocabs per title_id
    vocab_count = vocab_df.groupby('ID').size().reset_index(name='count')

    # Convert the result to a dictionary for easy access in the template
    vocab_count_dict = vocab_count.set_index('ID')['count'].to_dict()

    return render_template('index.html', titles=titles,
                           vocab_count=vocab_count_dict)

@app.route('/vocab/<int:title_id>', methods=['GET','POST'])  # Allow both GET and POST methods
def vocab(title_id):
    # Handle form submission
    if request.method == 'POST':
        kanji = request.form['kanji'].strip()
        hiragana = request.form['hiragana'].strip()
        meaning = request.form['meaning'].strip()

        # Append the new vocabulary to the CSV file
        with open('vocab.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([kanji if kanji else '', hiragana, meaning, title_id])

        # Redirect back to the vocabulary page after adding
        return redirect('/vocab/{}'.format(title_id))

    # Rest of the existing code for GET request
    vocab_df = read_csv('vocab.csv')
    title_df = read_csv('data.csv')

    # Filter vocab by title_id
    filtered_vocab = vocab_df[vocab_df['ID'] == title_id].to_dict(orient='records')

    # Get the title
    title = title_df[title_df['ID'] == title_id]['Title'].values[0] if not \
        title_df[title_df['ID'] == title_id].empty else "Missing Title"

    return render_template('vocab.html', title=title,
                           vocab_list=filtered_vocab, title_id=title_id) # undefined title_id issue resolved!


@app.route('/get_meaning/<int:vocab_id>')
def get_meaning(vocab_id):
    vocab_df = read_csv('vocab.csv')
    meaning = vocab_df.loc[vocab_df.index == vocab_id, 'Meaning'].values[0]
    return jsonify({'meaning': meaning})

if __name__ == '__main__':
    app.run(debug=True)