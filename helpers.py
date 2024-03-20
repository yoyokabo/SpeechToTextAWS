def count_word_occurrences(text, word):
    # split the text into words
    words = text.split()

    # Initialize a dictionary to store word counts
    word_counts = {}

    # Count occurrences of each word
    for w in words:
        # Convert word to lowercase for case-insensitive matching
        w = w.lower()
        # Remove punctuation
        w = w.strip('.,!?;:"\'()[]{}')
        w = w.strip(' ')
        # Update word count
        if w in word_counts:
            word_counts[w] += 1
        else:
            word_counts[w] = 1

    # Return the count of the specified word
    return word_counts.get(word.lower(), 0)


def count_words(text, words_to_count):
    words_to_count = words_to_count.split(",")
    reply = ""
    # Count occurrences of the word
    for word in words_to_count:
        count = count_word_occurrences(text, word)
        reply = reply + \
            f"The word '{word}' appears {count} times in the text.\n"
    return reply


def stoMSconverted(seconds):
    m = 0
    while seconds >= 60:
        m += 1
        seconds = seconds - 60
    seconds = int(seconds)
    return f'[00:{m}:{seconds}]'


def chunk_text_if_large(text, chunk_size=3000):
    if len(text) <= chunk_size:
        return [text]
    else:
        chunks = []
        for i in range(0, len(text), chunk_size):
            chunks.append(text[i:i + chunk_size])
        return chunks


def cleaner(ommit, text):
    lines = text.split('\n')
    filtered = [line for line in lines if ommit not in line]
    result = '\n'.join(filtered)
    return result
