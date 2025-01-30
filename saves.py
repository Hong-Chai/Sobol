FILE = "save.txt"

import csv
import os

def read_score_for_level(level, filename="scores.csv"):
    if not 1 <= level <= 4:
        print(f"Invalid level: {level}. Level must be between 1 and 4.")
        return None

    if not os.path.exists(filename):
        print(f"File not found: {filename}")
        return None

    try:
        with open(filename, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                try:  
                    scores = [int(score) for score in row]
                    if len(scores) >= level:  
                        return scores[level - 1] 
                    else:
                        print("Not enough scores in the CSV file for the requested level")
                        return None

                except ValueError: 
                    if len(row) >= level:
                       return row[level-1]
                    else:
                        print("Not enough scores in the CSV file for the requested level")
                        return None
            return None
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return None


def write_score_for_level(level, score, filename="scores.csv"):
    if not 1 <= level <= 4:
        print(f"Invalid level: {level}. Level must be between 1 and 4.")
        return

    try:       
        if os.path.exists(filename):
            with open(filename, 'r', newline='') as csvfile:
                reader = csv.reader(csvfile)
                rows = list(reader) 

            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                updated = False 

                for row in rows:
                    if len(row) >= level: 
                        row[level - 1] = score 
                        updated = True
                    writer.writerow(row)

                if not updated: 
                    new_row = ['' for _ in range(level-1)] + [score] 
                    writer.writerow(new_row)


        else:
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)

                new_row = ['' for _ in range(level-1)] + [score]
                writer.writerow(new_row)

    except Exception as e:
        print(f"An error occurred while writing to the file: {e}")


def get_save():
    try:
        save = open(FILE, "r")
    except FileNotFoundError:
        save = open(FILE, "w")
        save.write("1")
        save.close()
        save = open(FILE, "r")

    try:
        level = int(save.read())
        if level > 4:
            level = 4
    except BaseException:
        level = 1

    save.close()
    return level


def save(level):
    save = open(FILE, "w")
    save.write(str(level))
    save.close()
