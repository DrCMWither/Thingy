import os
import random
import numpy as np
from collections import Counter
from scipy.stats import spearmanr
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

txt_folder = "author"
txt_files = [os.path.join(txt_folder, filename) for filename in os.listdir(txt_folder) if filename.endswith(".txt")]

all_texts = []
for txt_file in txt_files:
    with open(txt_file, "r", encoding="utf-8") as f:
        text = f.read()
        for _ in range(100):
            start_index = random.randint(0, len(text) - 21)
            chunk = text[start_index:start_index + 20]
            all_texts.append(chunk)

with open("all_texts.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(all_texts))

# module one:
txt_contents_sinsim = []
for txt_file in txt_files:
    with open(txt_file, "r", encoding="utf-8") as f:
        txt_contents_sinsim.append(f.read())

vectorizer = CountVectorizer().fit(txt_contents_sinsim)

most_similar_index_table_sinsim = []
with open("all_texts.txt", "r", encoding="utf-8") as f:
    all_texts = f.readlines()

for line in all_texts:
    user_vector_sinsim = vectorizer.transform([line])
    similarities_sinsim = cosine_similarity(user_vector_sinsim, vectorizer.transform(txt_contents_sinsim))
    most_similar_index_sinsim = np.argmax(similarities_sinsim)
    most_similar_index_table_sinsim.append(most_similar_index_sinsim)

# module two:
word_dict = Counter()
for txt_file in txt_files:
    with open(txt_file, "r", encoding="utf-8") as f:
        words = f.read().split()
        word_dict.update(words)

most_similar_index_table_dict = []
with open("all_texts.txt", "r", encoding="utf-8") as f:
    all_texts = f.readlines()

for line in all_texts:
    user_words_dict = line.split()
    user_word_count_dict = Counter(user_words_dict)
    similarities_dict = {}

    for txt_file in txt_files:
        with open(txt_file, "r", encoding="utf-8") as f:
            txt_words = f.read().split()
            txt_word_count = Counter(txt_words)
            similarity_dict = sum((user_word_count_dict & txt_word_count).values()) / (sum(user_word_count_dict.values()) + sum(txt_word_count.values()))
            similarities_dict[txt_file] = similarity_dict

    most_similar_txt_dict = max(similarities_dict, key=similarities_dict.get)
    most_similar_index_table_dict.append(most_similar_txt_dict)


correlation, _ = spearmanr(most_similar_index_table_dict, most_similar_index_table_sinsim)
print(f"Spearman index: {correlation:.4f}")

if os.path.exists("all_texts.txt"):
    os.remove("all_texts.txt")
else:
    print("There's no need to remove cache.")

os.system("pause")