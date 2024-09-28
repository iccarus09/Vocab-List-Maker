import pandas as pd
from flask import Flask, render_template, jsonify, request, redirect
import csv

app = Flask(__name__)

def read_csv(file_path):
    return pd.read_csv(file_path)

@app.route('/')
def index():
    contents_df = read_csv('data.csv')
    contents = contents_df.to_dict(orient='records')

    # Read vocab from vocab.csv to count entries per title_id
    vocab_df = read_csv('vocab.csv')

    # Count the number of vocabs per title_id
    vocab_count = vocab_df.groupby('ID').size().reset_index(name='count')

    # Convert the result to a dictionary for easy access in the template
    vocab_count_dict = vocab_count.set_index('ID')['count'].to_dict()

    return render_template('index.html', contents=contents,
                           vocab_count=vocab_count_dict)

@app.route('/vocab/<int:title_id>', methods=['GET','POST'])  # Allow both GET and POST methods
def vocab(title_id):
    # Handle form submission
    if request.method == 'POST':
        kanji = request.form['kanji'].strip()
        hiragana = request.form['hiragana'].strip()
        meaning = request.form['meaning'].strip()
        title_id = request.form['title_id']
        memorized = False  # Set a default value or modify as needed

        # Auto-create vocab_id
        vocab_df = read_csv('vocab.csv')
        if not vocab_df.empty:
            max_id = vocab_df['ID'].max()
        else:
            max_id = 0
        new_id = max_id + 1

        # Append the new vocabulary to the CSV file, non-English available
        # by encoding
        with open('vocab.csv', 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([new_id, kanji if kanji else '(empty)', hiragana,
                             meaning,
                             title_id, memorized])

        # Redirect back to the vocabulary page after adding
        return redirect('/vocab/{}'.format(title_id))

        # Update the memorized status
        with open('vocab.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([memorized])

    # For GET requests: Read vocab and content data
    vocab_df = read_csv('vocab.csv')
    contents_df = read_csv('data.csv')

    # Get the contents using title_id
    title = contents_df[contents_df['ID'] == title_id]['Title'].values[0] if not \
        contents_df[contents_df['ID'] == title_id].empty else "Missing Title"

    # (1) Filter vocab_df based on title_id
    vocab_list = vocab_df[vocab_df['Content_ID'] == title_id]

    # (2) Convert filtered DataFrame to a list of dictionaries for rendering
    vocab_list = vocab_list.to_dict(orient='records')

    return render_template('vocab.html', title=title,
                           title_id=title_id, vocab_list=vocab_list)

# DONT NEED AT THE MOMENT
# @app.route('/get_meaning/<int:vocab_id>')
# def get_meaning(vocab_id):
#     vocab_df = read_csv('vocab.csv')
#     meaning = vocab_df.loc[vocab_df['ID'] == vocab_id, 'Meaning'].values[0]
#     return jsonify({'meaning': meaning})

if __name__ == '__main__':
    app.run(debug=True)