import string
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
import requests
import matplotlib.pyplot as plt

def get_text(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching the text from {url}: {e}")
        return None

def remove_punctuation(text):
    return text.translate(str.maketrans('', '', string.punctuation))

def map_function(word):
    return word, 1

def shuffle_function(mapped_values):
    shuffled = defaultdict(list)
    for key, value in mapped_values:
        shuffled[key].append(value)
    return shuffled.items()

def reduce_function(key_values):
    key, values = key_values
    return key, sum(values)

def map_reduce(text):
    text = remove_punctuation(text).lower()

    articles = {'the', 'a', 'an', 'of', 'to', 'and', 'in', 'it', 'that', 'not', 'as', 'is', 'at', 'for', 'but', 'on', 'or', 'by', 'from'}
    words = [word for word in text.split() if word not in articles]

    with ThreadPoolExecutor() as executor:
        mapped_values = list(executor.map(map_function, words))

    shuffled_values = shuffle_function(mapped_values)

    with ThreadPoolExecutor() as executor:
        reduced_values = list(executor.map(reduce_function, shuffled_values))

    return dict(reduced_values)

def visualize_top_words(result, top_n=10):
    sorted_words = sorted(result.items(), key=lambda item: item[1], reverse=True)[:top_n]
    words, frequencies = zip(*sorted_words)

    plt.figure(figsize=(10, 8))
    bars = plt.barh(words, frequencies, color='skyblue')
    plt.xlabel('Frequency')
    plt.ylabel('Words')
    plt.title(f'Top {top_n} Most Frequent Words')

    for bar in bars:
        plt.text(bar.get_width(), bar.get_y() + bar.get_height() / 2, str(int(bar.get_width())), 
                 va='center', ha='left', color='black', fontsize=12)
    plt.gca().invert_yaxis()  
    plt.show()

if __name__ == "__main__":
    url = "https://gutenberg.net.au/ebooks01/0100021.txt"
    text = get_text(url)
    if text:
        result = map_reduce(text)

        visualize_top_words(result, top_n=10)
    else:
        print("Error: Failed to fetch text.")
