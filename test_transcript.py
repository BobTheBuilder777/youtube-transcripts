from transcript import calculate_stats
from transcript import save_transcript
from transcript import clean_filename

import tempfile
import os


def test_calculate_stats_normal():
    text = "word " * 200
    word_count, reading_time = calculate_stats(text)
    assert word_count == 200
    assert reading_time == 1

def test_calculate_stats_empty():
    text = ""
    word_count, reading_time = calculate_stats(text)
    assert word_count == 0
    assert reading_time == 0

def test_calculate_stats_one_word():
    text = "Bob"
    word_count, reading_time = calculate_stats(text)
    assert word_count == 1
    assert reading_time == 0

def test_clean_filename_normal():
    title = clean_filename("Learning python")
    assert title == "Learning_python"

def test_clean_filename_special_characters():
    title = clean_filename("Python: A Beginner's Guide!")
    assert title == "Python__A_Beginner_s_Guide_"

def test_clean_filename_already_clean():
    title = clean_filename("A_Beginner_s_guide_to_Python")
    assert title == "A_Beginner_s_guide_to_Python"

def test_save_transcript():
    temp_dir = tempfile.gettempdir()
    temp_filename = os.path.join(temp_dir, "test_transcript.md") # create temporary directory

    save_transcript("test_content", temp_filename) # use the save_transcript() function to write "test_content" to the temp file

    with open(temp_filename, "r") as f:            # open temp file and assign text to variable
        content = f.read()

    assert os.path.exists(temp_filename) 
    assert content == "test_content"  

    os.remove(temp_filename)