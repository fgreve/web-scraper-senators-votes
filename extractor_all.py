import os
import pandas as pd
import io


def make_ses_all():
    def append_new_line(file_name, text_to_append):
        """Append given text as a new line at the end of file"""
        # Open the file in append & read mode ('a+')
        with open(file_name, "a+") as file_object:
            # Move read cursor to the start of file.
            file_object.seek(0)
            # If file is not empty then append '\n'
            data = file_object.read(100)
            if len(data) > 0:
                file_object.write("\n")
            # Append text at the end of file
            file_object.write(text_to_append)

    path = "../data/"
    file = "ses-votes.csv"
    path_file = os.path.join(path, file)
    ses_votes = pd.read_csv(path_file)

    votes = ses_votes["vote_id"].values

    for vote in votes:
        print(vote)

        path = "../data/votes-folders/" + "vote-" + str(vote) + "/"
        file = "ses.txt"
        path_file = os.path.join(path, file)

        with io.open(path_file, 'rt') as my_file:
            ses_text = my_file.read()

        tem = str(vote) + " || " + ses_text
        print(tem)

        path = "../data/"
        file = "ses.txt"
        path_file = os.path.join(path, file)

        append_new_line(path_file, tem)


def make_tem_all():
    def append_new_line(file_name, text_to_append):
        """Append given text as a new line at the end of file"""
        # Open the file in append & read mode ('a+')
        with open(file_name, "a+") as file_object:
            # Move read cursor to the start of file.
            file_object.seek(0)
            # If file is not empty then append '\n'
            data = file_object.read(100)
            if len(data) > 0:
                file_object.write("\n")
            # Append text at the end of file
            file_object.write(text_to_append)

    path = "../data/"
    file = "ses-votes.csv"
    path_file = os.path.join(path, file)
    ses_votes = pd.read_csv(path_file)

    votes = ses_votes["vote_id"].values

    for vote in votes:
        print(vote)

        path = "../data/votes-folders/" + "vote-" + str(vote) + "/"
        file = "tem.txt"
        path_file = os.path.join(path, file)

        with io.open(path_file, 'rt') as my_file:
            tem_text = my_file.read()

        tem = str(vote) + " || " + tem_text
        print(tem)

        path = "../data/"
        file = "tem.txt"
        path_file = os.path.join(path, file)

        append_new_line(path_file, tem)

