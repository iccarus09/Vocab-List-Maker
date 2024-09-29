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
            # Adding new vocab
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
                'Memorized': [False]  # Default = False
            })
            vocab_df = pd.concat([vocab_df, new_row], ignore_index=True)

        else:  # Update the 'Memorized' column based on checkbox selection
            memorized_ids = request.form.getlist('memorized_ids')
            vocab_df.loc[vocab_df['Content_ID'] == title_id, 'Memorized'] = \
                vocab_df.loc[vocab_df['Content_ID'] == title_id, 'ID'].astype(str).isin(memorized_ids)

        write_csv('vocab.csv', vocab_df)
        return redirect(url_for('vocab', title_id=title_id))

    # For GET requests: Read vocab and content data
    title = contents_df[contents_df['ID'] == title_id]['Title'].values[0] if not \
        contents_df[contents_df['ID'] == title_id].empty else "Missing Title"

    # (1) Filter vocab_df based on title_id
    vocab_list = vocab_df[vocab_df['Content_ID'] == title_id]

    # Convert filtered DataFrame to a list of dictionaries for rendering
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
    vocab_count = len(vocab_df)
    mylists = vocab_df.to_dict(orient='records')
    return render_template('mylist.html', mylists=mylists, vocab_count=vocab_count)

@app.route('/edit-contents', methods=['GET','POST','DELETE'])
def edit_contentlist():
    contents_df = read_csv('data.csv')
    vocab_df = read_csv('vocab.csv')

    # level rule
    def determine_level(count):
        if count > 20:
            return "Hard"
        elif 11 <= count <= 20:
            return "Moderate"
        else:
            return "Easy"

    # Calculate vocab count and level for each content
    # Calculate vocab count for each content
    vocab_count = vocab_df.groupby('Content_ID').size().reset_index(name='Vocab_Cal')

    # Rename in vocab_count DF
    vocab_count = vocab_count.rename(columns={'Vocab_Count': 'Vocab_Cal'})

    # Merge vocab_count DF with contents DF
    merged_df = contents_df.merge(vocab_count, left_on='ID',
                                  right_on='Content_ID', how='left')

    # Update 'Vocab_Count' column in contents DF with values from 'Vocab_Cal' in vocab_count DF
    merged_df['Vocab_Count'] = merged_df['Vocab_Cal']

    # Drop unnecessary columns
    final_df = merged_df.drop(['Content_ID', 'Vocab_Cal'], axis=1)

    # Apply the level rule
    final_df['Level'] = final_df['Vocab_Count'].apply(determine_level)

    # Fill NaN values with 0 and convert to int
    final_df['Vocab_Count'] = final_df['Vocab_Count'].fillna(0).astype(int)

    # Select relevant columns for final output
    final_df = final_df[['ID', 'Title', 'Link', 'Level', 'Vocab_Count']]

    # Debugging: realized the column name somehow changed from 'Vocab_Count' to 'Vocab_Count_y'
    print("Contents DataFrame after merging:")
    print(final_df.head())
    print(final_df.columns.tolist())

    write_csv('data.csv', final_df[['ID', 'Title', 'Link', 'Level', 'Vocab_Count']])

    # Handle form submission
    if request.method == 'POST':
        # Adding new content
        title = request.form['title'].strip()
        youtube = request.form['youtube'].strip()
        new_id = contents_df['ID'].max() + 1 if not contents_df.empty else 1
        new_row = pd.DataFrame({
            'ID': [new_id],
            'Title': [title],
            'Link': [youtube],
            'Level': ['Easy'],
            'Vocab_Count': [0]
        })
        contents_df = pd.concat([contents_df, new_row], ignore_index=True)
        write_csv('data.csv', contents_df[['ID', 'Title', 'Link', 'Level', 'Vocab_Count']])
        return jsonify(new_row.to_dict(orient='records')[0])

    elif request.method == 'DELETE':
        content_id = request.form.get('id')
        contents_df = contents_df[contents_df['ID'] != int(content_id)]
        write_csv('data.csv', contents_df[['ID', 'Title', 'Link']])
        return jsonify({"status": "success"})

    contents = final_df.to_dict(orient='records')
    return render_template('edit-contents.html', contents=contents)


if __name__ == '__main__':
    app.run(debug=True)