import os
import re
import numpy as np
import time

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


txt_folder = "author"
txt_files = [os.path.join(txt_folder, filename) for filename in os.listdir(txt_folder) if filename.endswith(".txt")]

txt_contents = []
for txt_file in txt_files:
    with open(txt_file, "r", encoding="utf-8") as f:
        txt_contents.append(f.read())

vectorizer = CountVectorizer().fit(txt_contents)

user_input = input("please input your text:")

user_vector = vectorizer.transform([user_input])

similarities = cosine_similarity(user_vector, vectorizer.transform(txt_contents))

most_similar_index = np.argmax(similarities)
most_similar_txt = os.path.basename(txt_files[most_similar_index])

print(f"the most similar author is: {most_similar_txt}")
print(f"at: {similarities[0, most_similar_index]:.2f}")

os.system("pause")