import os
from collections import Counter

txt_folder = "author"
txt_files = [os.path.join(txt_folder, filename) for filename in os.listdir(txt_folder) if filename.endswith(".txt")]

word_dict = Counter()

for txt_file in txt_files:
    with open(txt_file, "r", encoding="utf-8") as f:
        words = f.read().split()
        word_dict.update(words)

user_input = input("please input your text:")

user_words = user_input.split()
user_word_count = Counter(user_words)

similarities = {}
for txt_file in txt_files:
    with open(txt_file, "r", encoding="utf-8") as f:
        txt_words = f.read().split()
        txt_word_count = Counter(txt_words)
        similarity = sum((user_word_count & txt_word_count).values()) / (sum(user_word_count.values()) + sum(txt_word_count.values()))
        similarities[txt_file] = similarity

most_similar_txt = max(similarities, key=similarities.get)

print(f"the most similar author is: {os.path.basename(most_similar_txt)}")
print(f"at: {similarities[most_similar_txt]:.2f}")

os.system("pause")