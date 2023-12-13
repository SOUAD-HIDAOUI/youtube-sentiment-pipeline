import os
import pandas as pd
import time
import atexit
import tkinter.filedialog

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import tkinter as tk
from transformers import BertTokenizer, BertForSequenceClassification

from transformers import pipeline
atexit.register(lambda: driver.quit())

tokenizer = BertTokenizer.from_pretrained("nlptown/bert-base-multilingual-uncased-sentiment")
model = BertForSequenceClassification.from_pretrained("nlptown/bert-base-multilingual-uncased-sentiment")


# Create a BERT sentiment analysis pipeline
sentiment_analyzer = pipeline("sentiment-analysis")
chrome_options = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=chrome_options)
delay = 30
SCROLL_PAUSE_Time = 2

def analyze_sentiment(comment):
    inputs = tokenizer(comment, return_tensors="pt")
    outputs = model(**inputs)
    logits = outputs.logits
    predicted_class = logits.argmax().item()

    # Map the sentiment class to 'positive', 'negative', or 'neutral'
    if predicted_class == 2:
        return 'positive'
    elif predicted_class == 0:
        return 'negative'
    else:
        return 'neutral'
def scrape_loaded_comments():
    loaded_comments = []
    all_usernames = WebDriverWait(driver, delay).until(
        EC.presence_of_all_elements_located((By.XPATH, '//h3[@class="style-scope ytd-comment-renderer"]')))
    all_comments = WebDriverWait(driver, delay).until(
        EC.presence_of_all_elements_located((By.XPATH, '//yt-formatted-string[@id="content-text"]')))

    for (username, comment) in zip(all_usernames, all_comments):
        current_comment = {"username": username.text,
                           "comment": comment.text,
                           "sentiment": analyze_sentiment(comment.text)}
        print(f"Username: {username.text}\nComment: {comment.text}\nSentiment: {current_comment['sentiment']}")
        loaded_comments.append(current_comment)

    return loaded_comments


def on_analyze_button(sentiment_var, comment_text):
    global video_to_scrape
    video_to_scrape = url_entry.get()
    analyze_comments(sentiment_var, comment_text)

# ... (your existing code)

def analyze_comments(sentiment_var, comment_text):
    driver.get(video_to_scrape)
    all_comments_list = []

    # Limit the number of iterations to avoid infinite loop
    max_iterations = 10
    current_iteration = 0
    last_20_comments=[]
    while current_iteration < max_iterations:
        try:
            htmlelement = driver.find_element("tag name", "body")
            htmlelement.send_keys(Keys.END)

            # Wait for the new comments to load
            time.sleep(SCROLL_PAUSE_Time)

            last_20_comments = scrape_loaded_comments()

            # Filter comments based on selected sentiment
            filtered_comments = [comment for comment in last_20_comments if
                                 sentiment_var.get().lower() in comment['sentiment'].lower()]

            all_comments_list.extend(filtered_comments)

            # Update the comment text widget in the GUI
            comment_text.delete(1.0, tk.END)
            for comment in filtered_comments:
                comment_text.insert(tk.END,
                                    f"Username: {comment['username']}\nComment: {comment['comment']}\nSentiment: {comment['sentiment']}\n\n")

        except Exception as e:
            print(f"Error while trying to load comments: {e}")

        current_iteration += 1
        

        # Check if there are no more comments to load
        if not last_20_comments:
            break


    df = pd.DataFrame(all_comments_list)
    df.drop_duplicates(inplace=True)
    current_directory = os.getcwd()

    print("Current Working Directory:", current_directory)
    df.to_csv('comments_data.txt', sep='\t', index=False)

# ... (the rest of your existing code)


    df = pd.DataFrame(all_comments_list)
    df.drop_duplicates(inplace=True)
    current_directory = os.getcwd()

    print("Current Working Directory:", current_directory)
    df.to_csv('comments_data.txt', sep='\t', index=False)
def save():
    selected_comments = comment_text.get("1.0", tk.END).strip()
    file_path = r"C:\Users\user\Documents\Test\Test.txt"  # you can replace withyour desired directory where you want to save your comments, they are going to be stored a TextFile
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(selected_comments)
        print("File saved successfully!")
# Create a Tkinter window
root = tk.Tk()
root.title("YouTube Comment Sentiment Analysis")

# Create and pack the URL entry widget
url_entry = tk.Entry(root, width=50)
url_entry.pack(pady=10)

# Create a variable for sentiment selection
sentiments = ["positive", "negative", "neutral"]
sentiment_var = tk.StringVar(root)
sentiment_var.set(sentiments[0])

# Create and pack the sentiment choice box
sentiment_choice_box = tk.OptionMenu(root, sentiment_var, *sentiments)
sentiment_choice_box.pack(pady=10)

# Create and pack the Analyze button with the sentiment_var as an argument
comment_text = tk.Text(root, wrap=tk.WORD, width=80, height=20)
comment_text.pack(expand=True, fill='both')
comment_text.pack()

analyze_button = tk.Button(root, text="Analyze Comments", command=lambda: on_analyze_button(sentiment_var, comment_text))
analyze_button.pack(pady=10)

save_button = tk.Button(root, text="Save ", command=save)
save_button.pack()
# Start the Tkinter event loop
root.mainloop()
