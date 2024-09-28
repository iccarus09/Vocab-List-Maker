import pandas as pd
from flask import Flask, render_template, jsonify, request, redirect, url_for
import csv

app = Flask(__name__)

def read_csv(file_path):
    return pd.read_csv(file_path)

def write_csv(file_path, data):
    data.to_csv(file_path, index=False)

@app.route('/')
def index():
    contents_df = read_csv('data.csv')
    contents = contents_df.to_dict(orient='records')

    # Read vocab from vocab.csv to count entries per title_id
    vocab_df = read_csv('vocab.csv')

    # Count the number of vocabs per title_id
    vocab_count = vocab_df.groupby('Content_ID').size().reset_index(name='count')

    # Convert the result to a dictionary for easy access in the template
    vocab_count_dict = vocab_count.set_index('Content_ID')['count'].to_dict()

    return render_template('index.html', contents=contents,
                           vocab_count=vocab_count_dict)

@app.route('/vocab/<int:title_id>', methods=['GET','POST'])  # Allow both GET and POST methods
def vocab(title_id):
    vocab_df = read_csv('vocab.csv')
    contents_df = read_csv('data.csv')

    # Handle form submission
    if request.method == 'POST':
        # Adding new vocab
        if 'kanji' in request.form:
            kanji = request.form['kanji'].strip()
            hiragana = request.form['hiragana'].strip()
            meaning = request.form['meaning'].strip()

            new_id = vocab_df['ID'].max() + 1 if not vocab_df.empty else 1
            new_row = pd.DataFrame({
                'ID': [new_id],
                'Kanji': [kanji if kanji else '(empty)'],
                'Hiragana': [hiragana],
                'Meaning': [meaning],
                'Content_ID': [title_id],
                'Memorized': [False] # Default = False
            })
            vocab_df = pd.concat([vocab_df, new_row], ignore_index=True)
        else:  # Update the 'Memorized' column based on checkbox selection
            memorized_ids = request.form.getlist('memorized_ids')
            vocab_df['Memorized'] = vocab_df['ID'].astype(str).isin(
            memorized_ids)

        write_csv('vocab.csv', vocab_df)
        return redirect(url_for('vocab', title_id=title_id))

    # For GET requests: Read vocab and content data
    title = contents_df[contents_df['ID'] == title_id]['Title'].values[0] if not \
        contents_df[contents_df['ID'] == title_id].empty else "Missing Title"

    # (1) Filter vocab_df based on title_id
    vocab_list = vocab_df[vocab_df['Content_ID'] == title_id]

    # (2) Convert filtered DataFrame to a list of dictionaries for rendering
    vocab_list = vocab_list.to_dict(orient='records')

    return render_template('vocab.html', title=title,
                           title_id=title_id, vocab_list=vocab_list)

@app.route('/mylist', methods=['GET','POST'])
def get_mylist():
    # Handle deletion
    if request.method == 'POST':
        id_to_delete = request.form.get('id')

        if id_to_delete:
            vocab_df = read_csv('vocab.csv')
            # Remove the item with this ID
            vocab_df = vocab_df[vocab_df['ID'] != int(id_to_delete)]
            write_csv('vocab.csv', vocab_df)

        # Redirect after deletion
        return redirect(url_for('get_mylist'))

    # Handle GET request
    vocab_df = read_csv('vocab.csv')
    mylists = vocab_df.to_dict(orient='records')
    return render_template('mylist.html', mylists=mylists)

if __name__ == '__main__':
    app.run(debug=True)