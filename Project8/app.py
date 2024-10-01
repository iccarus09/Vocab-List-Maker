import pandas as pd
from flask import Flask, render_template, jsonify, request, redirect, url_for, make_response, json
import helpers
import logging

app = Flask(__name__)

# Routes
@app.route('/')
def index():
    contents_df = helpers.get_vocab_count_and_level()
    contents = contents_df.to_dict(orient='records')
    vocab_count_dict = contents_df.set_index('ID')['Vocab_Count'].to_dict()
    return render_template('index.html', contents=contents,
                           vocab_count=vocab_count_dict)

@app.route('/edit-vocab/<int:title_id>', methods=['GET', 'POST', 'DELETE'])
def edit_vocablist(title_id):
    vocab_df = helpers.read_csv('vocab.csv')
    contents_df = helpers.get_vocab_count_and_level()
    logging.debug(
        f"Received {request.method} request for title_id: {title_id}")

    # Handle form submission

    if request.method == 'DELETE':
        data = json.loads(request.data)
        item_id = data.get('id')
        print(f"Attempting to delete item with ID: {item_id}")

        if item_id is None:
            return jsonify(
                {"status": "error", "message": "No item ID provided"}), 400

        try:
            vocab_df = helpers.read_csv('vocab.csv')
            vocab_df = vocab_df[vocab_df['ID'] != int(item_id)]
            helpers.write_csv('vocab.csv', vocab_df)
            print(f"Successfully deleted item with ID: {item_id}")
            return jsonify({"status": "success"}), 200
        except Exception as e:
            print(f"Error deleting item: {str(e)}")
            return jsonify({"status": "error", "message": str(e)}), 500


    # 2ND TRY
    # if request.method == 'DELETE':
    #     item_id = request.form.get('id')
    #     logging.debug(f"Attempting to delete item with ID: {item_id}")
    #
    #     if item_id is None:
    #         logging.error("No item ID provided in DELETE request")
    #         return jsonify(
    #             {"status": "error", "message": "No item ID provided"}), 400
    #
    #     try:
    #         vocab_df = helpers.read_csv('vocab.csv')
    #         logging.debug(f"Current vocab_df shape: {vocab_df.shape}")
    #
    #         vocab_df = vocab_df[vocab_df['ID'] != int(item_id)]
    #         logging.debug(f"vocab_df shape after deletion: {vocab_df.shape}")
    #
    #         helpers.write_csv('vocab.csv', vocab_df)
    #         logging.info(f"Successfully deleted item with ID: {item_id}")
    #         return jsonify({"status": "success"})
    #     except Exception as e:
    #         logging.exception(f"Error deleting item: {str(e)}")
    #         return jsonify({"status": "error", "message": str(e)}), 500




        # helpers.write_csv('vocab.csv', vocab_df[['Kanji', 'Hiragana', 'Meaning']])
        # print(f"vocab after delete: {vocab_df}")
        # vocabs = vocab_df[vocab_df['Content_ID'] == title_id].to_dict(
        #     orient='records')
        # title = contents_df[contents_df['ID'] == title_id]['Title'].values[0]
        # print("Delete pressed")
        # return render_template('vocab.html', vocabs=vocabs, title_id=title_id,
        #                        title=title)

    elif request.method == 'POST':
        # Adding new content
        kanji = request.form['kanji'].strip()
        hiragana = request.form['hiragana'].strip()
        meaning = request.form['meaning'].strip()
        new_id = vocab_df['ID'].max() + 1 if not vocab_df.empty else 1
        new_row = pd.DataFrame({
            'ID': [new_id],
            'Kanji': [kanji if kanji else 'No Kanji'], # empty didnt work
            'Hiragana': [hiragana],
            'Meaning': [meaning],
            'Content_ID': [title_id],
            'Memorized': [False]  # Default = False
        })
        vocab_df = pd.concat([vocab_df, new_row], ignore_index=True)
        helpers.write_csv('vocab.csv', vocab_df)
        vocabs = vocab_df[vocab_df['Content_ID'] == title_id].to_dict(
            orient='records')
        title = contents_df[contents_df['ID'] == title_id]['Title'].values[0]
        print(f"vocabs after add: {vocab_df.iloc[-1]}")
        return render_template('vocab.html', vocabs=vocabs, title_id=title_id,
                               title=title)



    vocab_df = helpers.read_csv('vocab.csv')
    contents_df = helpers.get_vocab_count_and_level()
    vocabs = vocab_df[vocab_df['Content_ID'] == title_id].to_dict(orient='records')
    title = contents_df[contents_df['ID'] == title_id]['Title'].values[0]
    print(f"vocabs final: {vocabs}") # Showed me the list
    return render_template('vocab.html', vocabs=vocabs, title_id=title_id, title=title)

@app.route('/mylist', methods=['GET','POST'])
def get_mylist():
    # Handle deletion
    if request.method == 'POST':
        id_to_delete = request.form.get('id')

        if id_to_delete:
            vocab_df = helpers.read_csv('vocab.csv')
            # Remove the item with this ID
            vocab_df = vocab_df[vocab_df['ID'] != int(id_to_delete)]
            helpers.write_csv('vocab.csv', vocab_df)

        # Redirect after deletion
        return redirect(url_for('get_mylist'))

    # Handle GET request
    vocab_df = helpers.read_csv('vocab.csv')
    vocab_count = len(vocab_df)
    mylists = vocab_df.to_dict(orient='records')
    return render_template('mylist.html', mylists=mylists, vocab_count=vocab_count)

@app.route('/edit-contents', methods=['GET','POST','DELETE'])
def edit_contentlist():
    contents_df = helpers.get_vocab_count_and_level()
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
        contents_df = pd.concat([contents_df, new_row], ignore_index=True) # Combine initial table and new entry
        helpers.write_csv('data.csv', contents_df[['ID', 'Title', 'Link', 'Level', 'Vocab_Count']])
        print(f"contents after add: {contents_df}")
        return jsonify(new_row.to_dict(orient='records')[0]) # new_row convert to dict & convert to json object for sending back to the client

    elif request.method == 'DELETE':
        content_id = request.form.get('id')
        contents_df = contents_df[contents_df['ID'] != int(content_id)]
        helpers.write_csv('data.csv', contents_df[['ID', 'Title', 'Link']])
        print(f"contents after delete: {contents_df}")
        return jsonify({"status": "success"})

    contents_df = helpers.get_vocab_count_and_level()
    contents = contents_df.to_dict(orient='records')
    print(f"contents final: {contents_df}")
    return render_template('edit-contents.html', contents=contents)


if __name__ == '__main__':
    app.run(debug=True)