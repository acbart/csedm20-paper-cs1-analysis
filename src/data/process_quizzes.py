import logging
import os
import json
import sqlite3
import pandas as pd
from src.data.quiz_question_types import QUESTION_TYPES, DefaultQuestionType

def clean_name(filename):
    return "".join([c for c in filename
                    if c.isalpha() or c.isdigit()
                       or c in (' ', '.')]).rstrip()

def process_quiz(quiz_csv_path, quiz_csv_fullpath, quiz_meta):
    logger = logging.getLogger(__name__)
    # Get ID of quiz
    quiz_id = quiz_csv_path.split("-")[0]
    if quiz_id not in quiz_meta:
        logger.error('Missing CSV file for quiz: {}'.format(quiz_id))
        return []
    quiz = quiz_meta[quiz_id]

    # Process CSV file
    df = pd.read_csv(quiz_csv_fullpath, dtype=str)
    anonymous = 'id' not in df.columns
    FIRST_COLUMN = 5 if anonymous else 8
    # Grab the header as a single row to extract point columns
    header = pd.read_csv(quiz_csv_fullpath, nrows=1, header=None)
    # Grab out the actual columns of data
    df_submissions_subtable = df.iloc[:, FIRST_COLUMN:-3]
    attempts = df.iloc[:, FIRST_COLUMN - 1].map(int)
    user_ids = None if anonymous else df.iloc[:, 1]
    overall_score = df.iloc[:, -1].map(float)
    # Question IDs are stored in alternating columns as "ID: Text"
    question_ids = [x.split(':')[0] for x in
                    df_submissions_subtable.columns[::2]]
    for i, question_id in enumerate(question_ids):
        # Actual student submission is in alternating columns
        submissions = df_submissions_subtable.iloc[:, i * 2]
        scores = df_submissions_subtable.iloc[:, 1 + i * 2].map(float)
        max_score = float(header.iloc[0, FIRST_COLUMN + 1 + i * 2])
        if question_id not in quiz['questions']:
            logger.error('Missing Question {} for quiz {}'.format(question_id,quiz_id))
            continue
        question = quiz['questions'][question_id]
        question_type = question['question_type']
        processor = QUESTION_TYPES.get(question_type, DefaultQuestionType)
        q = processor(question, submissions, attempts, user_ids,
                      scores, overall_score, {}, max_score,
                      anonymous, quiz_csv_path)
        q.analyze()
        for user, question, answer, attempt, score in q.to_answers():
            yield user, quiz['title'], question, answer, attempt, score

def process_quizzes(input_filepath, output_filepath):
    # Create database
    output_database = os.path.join(output_filepath, 'quizzes.db')
    connection = sqlite3.connect(output_database)
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS quiz_data (id INTEGER PRIMARY KEY, subject INTEGER)''')
    connection.commit()
    # Load in data file
    quiz_meta_path = os.path.join(input_filepath, 'all_quizzes.json')
    with open(quiz_meta_path) as quiz_meta_file:
        quiz_meta = json.load(quiz_meta_file)
    # Load in CSV files
    quiz_folder = os.path.join(input_filepath, 'quizzes')
    for quiz_csv_path in os.listdir(quiz_folder):
        quiz_csv_fullpath = os.path.join(quiz_folder, quiz_csv_path)
        quiz_data = process_quiz(quiz_csv_path, quiz_csv_fullpath, quiz_meta)
        # Transfer into database
        for quiz in quiz_data:
            #print(quiz)
            pass

