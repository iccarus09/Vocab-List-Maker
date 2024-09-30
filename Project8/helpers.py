import pandas as pd

# Helper functions
def read_csv(file_path):
    return pd.read_csv(file_path)

def write_csv(file_path, data):
    data.to_csv(file_path, index=False)

def determine_level(count):
    if count > 20:
        return "Hard"
    elif 11 <= count <= 20:
        return "Moderate"
    else:
        return "Easy"

def get_vocab_count_and_level():
    contents_df = read_csv('data.csv')

    vocab_df = read_csv('vocab.csv')
    # Create a copy of the DataFrame to avoid SettingWithCopyWarning
    new_vocab_df = vocab_df.copy()

    # Group by Content_ID and count occurrences
    vocab_count = new_vocab_df.groupby('Content_ID').size().reset_index(
        name='Vocab_Cal')

    # Debugging: Print out vocab_count
    print("Vocab Count:\n", vocab_count)

    merged_df = contents_df.merge(vocab_count, left_on='ID',
                                  right_on='Content_ID', how='left')

    # # Debugging: Print out merged DataFrame
    # print("Merged DataFrame:\n", merged_df)

    # Use .loc[] to fill NaN values and convert to int
    merged_df.loc[:, 'Vocab_Cal'] = merged_df['Vocab_Cal'].fillna(0).astype(int)
    merged_df.loc[:, 'Level'] = merged_df['Vocab_Cal'].apply(determine_level)

    final_df = merged_df[['ID', 'Title', 'Link', 'Level', 'Vocab_Cal']].copy()

    # Rename Vocab_Cal to Vocab_Count before saving DF to data.csv
    final_df.rename(columns={'Vocab_Cal': 'Vocab_Count'}, inplace=True)
    final_df.to_csv('data.csv', index=False)

    return final_df