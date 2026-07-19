from dataclasses import dataclass
from typing import Optional
import random
import sys

@dataclass
class Student:
    Tutorial_Group: str
    Student_ID: str
    School: str
    Name: str
    Gender: str
    CGPA: float
    Subgroup: Optional[int] = None

@dataclass
class TutorialGroup:
    Group_name: str
    Student: list[Student]

def retrieve_data():
    try:
        print("Drawing data...")
        with open("records.csv", "r") as file:
            lines = file.readlines()
        # Save header of output
        header = lines[0]
    except FileNotFoundError:
        print("Error: File not found")
        exit()

    # Create dictionary named records
    records = {}
    sorted_records = {}

    # Save records with missing info
    missing_data = False
    missing_list = []
    index = 1

    print("Grouping Tutoral Groups...")
    # Looping through each data (skipping the title) to strip and split newline by tab or comma
    for line in lines[1:]:
        checked = False

        parts = line.strip().split("\t")
        parts = line.strip().split(",")

        # Check if there is missing column
        if len(parts) < 6:
            checked = True
            missing_list.append(f"{index},{line}")
            continue

        # Group each parts to the key variables
        tutorial_group = parts[0].strip()
        student_id = parts[1].strip()
        school = parts[2].strip()
        name = parts[3].strip()
        gender = parts[4].strip()
        gpa = parts[5].strip()

        # create new tuotorial group list
        if tutorial_group not in records:
            records[tutorial_group] = []

        # store each student in class
        student_record = Student(tutorial_group, student_id, school, name, gender, gpa)

        # check if record is empty
        if check_exist(student_record) and not checked:
            missing_data = True
            missing_list.append(f"{index},{line}")
        else:
            # If data is missing, gpa might not be able to convert to float
            student_record.CGPA = float(gpa)

        # If there is missing data, don't waste resources
        if not missing_list:
            records[tutorial_group].append(student_record)
            # merge store the keys (G-1,G-2,G-3) etc
            sorted_group_keys = merge_sort(list(records.keys()), extract_group_num)
            for g in sorted_group_keys:
                sorted_records[g] = records[g]

        index += 1

    if missing_data:
        print("Output missing data")
        output_error(header, missing_list)

    print("Sorting GPA...")
    return header, sort_group_CGPA_desc(sorted_records)

def check_exist(record):
    if not record.Tutorial_Group:
        return True
    elif not record.Student_ID:
        return True
    elif not record.School:
        return True
    elif not record.Name:
        return True
    elif not record.Gender:
        return True
    elif not record.CGPA:
        return True
    else:
        return False

def output_error(header, missing_list):
    md_header = "Line," + header

        # Record the items with error to file
    with open("errors.csv", "w") as file:
        file.write(md_header)
        for i in missing_list:
            file.write(i)
    exit()

def extract_group_num(key):
    return int(key.split('-')[1])

def extract_cgpa(student):
    return float(student.CGPA)

def merge_sort(data, func_name, ascending=True):
    try:
        list_length = len(data)
        # Base case: if list has 1 or 0 elements, it's already sorted
        if list_length <= 1:
            return data

        # Split into two halves
        mid = list_length // 2
        left_half = merge_sort(data[:mid], func_name,ascending)
        right_half = merge_sort(data[mid:], func_name,ascending)

        return merge(left_half, right_half, func_name, ascending)

    except TypeError as e:
        print(f"TypeError: {e} - invalid data or func_name")
    except AttributeError as e:
        print(f"AttributeError: {e} - func_name accessing missing attribute")
    except Exception as e:
        print(f"Error in merge_sort: {e}")

def merge(left_half, right_half, func_name, ascending):
    merged = []
    length_left_half = len(left_half)
    length_right_half = len(right_half)
    i = j = 0

    # Compare elements from both halves
    while i < length_left_half and j < length_right_half:
        left_key = func_name(left_half[i])
        right_key = func_name(right_half[j])

        # Check the order of sorting
        # Ascending order
        if ascending:
            if left_key <= right_key:
                merged.append(left_half[i])
                i += 1
            else:
                merged.append(right_half[j])
                j += 1

        # Descending order
        else:
            if left_key >= right_key:
                merged.append(left_half[i])
                i += 1
            else:
                merged.append(right_half[j])
                j += 1

    # Add any leftover elements
    merged.extend(left_half[i:])
    merged.extend(right_half[j:])

    return merged

def sort_group_CGPA_desc(records):
    desc_list = {}
    # loop through each tut group and sort by descending order and assigning to desc list the current group that is being iterated
    for group, students in records.items():
        desc_list[group] = merge_sort(students, extract_cgpa,True)

    return desc_list

def calculate_num_subgroups(records, tut_group, subgroup_size):
    try:
        # checks whether the selected tutorial group exists in the records
        students = records[tut_group]
    except KeyError:
        print(f"Error: '{tut_group}' does not exist in the records.")
        return None

    for group_name, student in records.items():
        # Run only if tutorial group exist in records
        if tut_group == group_name:
            # find total of students in the selected tutorial group
            total = len(student)
            # Ensure that there are students in the tutorial group
            if total == 0:
                return [0]
            # Ensure that there are more students than one subgroup size.
            # If not there is no point in creating more than one subgroup
            if total < subgroup_size:
                return [total]
            else:
                number_of_subgroups = total // subgroup_size
                remainder = total % subgroup_size
                # (Student left >= 75% of a subgroup size, create an addition subgroup)
                # EG: [5,5,5] 19/5 = 3 subgroups Remainder 4
                # 4 is 80% of 5, so [5,5,5,4]
                threshold = 0.75

                # Prevent Zero Division Error
                if number_of_subgroups == 0:
                    num_subgroups = 1
                else:
                    if (remainder / float(subgroup_size)) >= threshold:
                        num_subgroups = number_of_subgroups + 1
                    else:
                        num_subgroups = number_of_subgroups

                # find the new number of subgroups and remainder after applying the 75%
                number_of_subgroups = total // num_subgroups
                remainder = total % num_subgroups
                i = 0
                # For each subgroup, it will append it into the list
                subgroup_sizes = []
                while i < num_subgroups:
                    size_per_subgroup = number_of_subgroups
                    # If we still have remaining students, +1 student to each subgroup depending on the remainder
                    if i < remainder:
                        size_per_subgroup += 1
                    subgroup_sizes.append(size_per_subgroup)
                    i += 1
                return subgroup_sizes

def weighted_allocation(student, subgroup, SG_data, school_count, gender_count, gpa_sum, tut_avg_gpa, target_size):

    chosen_index = None
    lowest_score = None
    gpa = student.CGPA

    # for each subgroup, check if it's score is the best
    for index in range(len(target_size)):
        if SG_data[index] <= 0:
            continue

        # ensure no division by 0 / -ve
        if target_size[index] > 0:
            target = target_size[index]
        else:
            target = 1

        # soft penalties to avoid clustering of specific variable
        same_school = school_count[index][student.School] + 1 # current count w student
        same_gender = gender_count[index][student.Gender] + 1 # current count w student
        current_size = len(subgroup[index]) + 1 # current count w student

        # GPA Priority
        current_mean = (gpa_sum[index] + gpa) / (current_size) # average of current subgroup
        gpa_gap = abs(tut_avg_gpa - current_mean)

        #divide by target to treat each weight fairly
        current_score = gpa_gap * 4 + same_school/target * 3 + same_gender/target * 2 + current_size/target

        # Compare lowest score to choose subgroup
        if lowest_score is None or current_score < lowest_score:
            lowest_score = current_score
            chosen_index = index

    return chosen_index

def categorize_records(records,subgroup_size):
    # list of all subgroups in records, regardless of tutorial group
    all_tut_subgroups = []

    # loop through every tutorial group in records
    for tut_group, students in records.items():

        SG_data = calculate_num_subgroups(records, tut_group,subgroup_size) # list of subgroup sizes that will be updated
        fixed_SG_data = calculate_num_subgroups(records, tut_group,subgroup_size) # list of subgroup size that will be fixed
        no_of_SG = len(SG_data) #no. of subgroups in current tutorial group
        subgroup = [[] for i in range(no_of_SG)] #empty list of x no. of empty list where x is no. of subgroups
        school_count = [defaultdict(int) for i in range(no_of_SG)] # returns default value of 0 for key NOT in the list
        gender_count = [defaultdict(int) for i in range(no_of_SG)] # same as above, shorter than using if else statements

        # to help calculate average gpa
        total = 0
        for student in students:
            total += student.CGPA

        tut_avg_gpa = total / len(students)
        # running sum of GPA per subgroup (keeps current_size)
        gpa_sum = [0.0 for gpa in range(no_of_SG)]

        #4 loop through each student in the tutorial group
        for student in students:

            idx = weighted_allocation(student, subgroup, SG_data, school_count, gender_count, gpa_sum, tut_avg_gpa, fixed_SG_data)  # gets next index
            if idx is None:
                continue

            # update all progress trackers to use in weighted_allocation
            student.Subgroup = idx + 1
            subgroup[idx].append(student)
            school_count[idx][student.School] += 1
            gender_count[idx][student.Gender] += 1
            gpa_sum[idx] += student.CGPA
            SG_data[idx] -= 1

            #to visually show where each student goes in each iteration (presentation)
            #print(f"SG_data for ", {tut_group}, SG_data)

        all_tut_subgroups.extend(subgroup)

    return records, all_tut_subgroups


def cgpa_diversity(group):
    n = len(group)
    total_cgpa = 0
    square_difference = 0

    # Calculate the total sum of CGPAs, and obtain the average CGPA
    for student in group:
        total_cgpa += student.CGPA

    average_cgpa = total_cgpa / n

    # Calculate the square difference
    for student in group:
        square_difference += (student.CGPA - average_cgpa) ** 2

    # Calculate the standard deviation, then the diversity score for that group
    sigma = ((1.0 / n) * square_difference) ** (1/2)
    score = max(0, 10 * (1 - sigma))

    return score

import math

def gender_diversity(group):
    n = len(group)
    male_count = 0

    # Calculating the male ratio
    for student in group:
        if student.Gender == "Male":
            male_count += 1

    male_ratio = male_count / n

    # Calculating the ideal ratio
    ideal_ratio = math.ceil(n / 2) / n

    # Return the score
    if (male_ratio >= 0.5):
        score = 10 * (1 - abs(male_ratio - ideal_ratio) / ideal_ratio)
    else:
        female_ratio = 1 - male_ratio
        score = 10 * (1 - abs(female_ratio - ideal_ratio) / ideal_ratio)
    return score

from collections import defaultdict

def school_diversity(group):
    n = len(group)
    max_count = -1 # M

    school_freq = defaultdict(int)

    # Finding the maximum number of student from one school
    for student in group:
        school_freq[student.School] += 1
        max_count = max(max_count, school_freq[student.School])

    # Return the score
    score = 10 * (1 - (max_count - 1) / (n - 1))
    return score

def overall_diversity(group):
    c = cgpa_diversity(group)
    g = gender_diversity(group)
    s = school_diversity(group)

    score = 0.45 * c + 0.3 * s + 0.25 * g
    return score

import matplotlib.pyplot as plt

def extract_score_list(subgroup_list):
    cgpa_score_list = []
    gender_score_list = []
    school_score_list = []
    overall_score_list = []

    for team in subgroup_list:
        cgpa_score_list.append(cgpa_diversity(team))
        gender_score_list.append(gender_diversity(team))
        school_score_list.append(school_diversity(team))
        overall_score_list.append(overall_diversity(team))

    return cgpa_score_list, gender_score_list, school_score_list, overall_score_list

def plot_histogram_score(cgpa_score_list, gender_score_list, school_score_list, overall_score_list):
    ## Calculating the average scores
    cgpa_score_average = sum(cgpa_score_list) / len(cgpa_score_list)
    gender_score_average = sum(gender_score_list) / len(gender_score_list)
    school_score_average = sum(school_score_list) / len(school_score_list)
    overall_score_average = sum(overall_score_list) / len(overall_score_list)


    plt.figure()

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize = (15, 10))

    ## Plotting the histogram

    # CGPA
    ax1.hist(cgpa_score_list, bins = [i * 0.2 for i in range(51)], color = '#56B4E9', edgecolor = 'black')
    ax1.set_title("CGPA Diversity Analysis")
    ax1.set_xlabel("CGPA Diversity Score")
    ax1.set_ylabel("Number of Teams")
    ax1.axvline(cgpa_score_average, color = 'red', linewidth = 1.5, linestyle = '--', label = f'Average = {cgpa_score_average:.2f}')
    ax1.legend()

    # Gender
    ax2.hist(gender_score_list, bins = [i for i in range(11)], color = '#CC79A7', edgecolor = 'black')
    ax2.set_title("Gender Diversity Analysis")
    ax2.set_xlabel("Gender Diversity Score")
    ax2.axvline(gender_score_average, color = 'red', linewidth = 1.5, linestyle = '--', label = f'Average = {gender_score_average:.2f}')
    ax2.legend()

    # School
    ax3.hist(school_score_list, bins = [i for i in range(11)], color = '#009E73', edgecolor = 'black')
    ax3.set_title("School Diversity Analysis")
    ax3.set_xlabel("School Diversity Score")
    ax3.set_ylabel("Number of Teams")
    ax3.axvline(school_score_average, color = 'red', linewidth = 1.5, linestyle = '--', label = f'Average = {school_score_average:.2f}')
    ax3.legend()

    # Overall
    ax4.hist(overall_score_list, bins = [i * 0.2 for i in range(51)], color = '#E69F00', edgecolor = 'black')
    ax4.set_title("Overall Diversity Analysis")
    ax4.set_xlabel("Overall Diversity Score")
    ax4.axvline(overall_score_average, color = 'red', linewidth = 1.5, linestyle = '--', label = f'Average = {overall_score_average:.2f}')
    ax4.legend()

    plt.show()

def evaluate_score(cgpa_score_list, gender_score_list, school_score_list, overall_score_list):
    print("DIVERSITY EVALUATION\n")

    print(f"Total Teams: {len(overall_score_list)}")

    # CGPA Diversity
    print("\nCGPA Diversity: ")
    acceptable_cgpa = 0

    for i in cgpa_score_list:
        if (i >= 8.0):
            acceptable_cgpa += 1

    print(f"- Acceptable Teams: {acceptable_cgpa}")
    print(f"- % of Acceptable Teams: {(acceptable_cgpa * 100 / len(cgpa_score_list)):.2f}%")

    # Gender Diversity
    print("\nGender Diversity: ")
    acceptable_gender = 0

    for i in gender_score_list:
        if (i >= 8.0):
            acceptable_gender += 1

    print(f"- Acceptable Teams: {acceptable_gender}")
    print(f"- % of Acceptable Teams: {(acceptable_gender * 100 / len(gender_score_list)):.2f}%")

    # School Diversity
    print("\nSchool Diversity: ")
    acceptable_school = 0

    for i in school_score_list:
        if (i >= 8.0):
            acceptable_school += 1

    print(f"- Acceptable Teams: {acceptable_school}")
    print(f"- % of Acceptable Teams: {(acceptable_school * 100 / len(school_score_list)):.2f}%")

    # Overall Diversity
    print("\nOverall Diversity: ")
    acceptable_overall = 0

    for i in cgpa_score_list:
        if (i >= 8.0):
            acceptable_overall += 1

    print(f"- Acceptable Teams: {acceptable_overall}")
    print(f"- % of Acceptable Teams: {(acceptable_overall * 100 / len(overall_score_list)):.2f}%")

#sort highest to lowest and then rank the teams
#highest score gets rank 1
def prepare_rank(scores):
    if not scores:
        return [], []
    sorted_scores = sorted(scores, reverse=True)
    ranks = [i + 1 for i in range(len(sorted_scores))]
    return ranks, sorted_scores

import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

def rank_score(cgpa_score_list, gender_score_list, school_score_list, overall_score_list,
    good_zone_min=7.5
):
    #averages
    cgpa_score_average = sum(cgpa_score_list) / len(cgpa_score_list)
    gender_score_average = sum(gender_score_list) / len(gender_score_list)
    school_score_average = sum(school_score_list) / len(school_score_list)
    overall_score_average = sum(overall_score_list) / len(overall_score_list)

    cgpa_rank, sorted_cgpa = prepare_rank(cgpa_score_list)
    gender_rank, sorted_gender = prepare_rank(gender_score_list)
    school_rank, sorted_school = prepare_rank(school_score_list)
    overall_rank, sorted_overall = prepare_rank(overall_score_list)

    sns.set_theme(style="whitegrid")

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))

    all_plots = [
        (ax1, cgpa_rank, sorted_cgpa, cgpa_score_average, "CGPA Diversity"),
        (ax2, gender_rank, sorted_gender, gender_score_average, "Gender Diversity"),
        (ax3, school_rank, sorted_school, school_score_average, "School Diversity"),
        (ax4, overall_rank, sorted_overall, overall_score_average, "Overall Diversity"),
    ]

    zone_color = "#90EE90"
    zone_alpha = 0.25

    #just drawing each plot
    for ax, ranks, scores, avg, title in all_plots:
        ax.set_title(title)
        ax.set_xlabel("Team Rank")
        ax.set_ylabel("Fairness Score")
        ax.set_ylim(0, 10)

        ax.axhspan(good_zone_min, 10, facecolor=zone_color, alpha=zone_alpha)

        #finally plot the data
        ax.plot(ranks, scores, color="blue", linewidth=2.3)
        ax.axhline(y=avg, color="gray", linestyle="--", linewidth=1.1,
                       label=f"Average={avg:.2f}")
        ax.legend()

    plt.show()

def editHeader(header, insertText="Team Assigned"):
    sHeader = [h.strip() for h in header.split(',')]
    if insertText not in sHeader:
        sHeader.append(insertText)
    return ','.join(sHeader) + "\n"


def saveToCSV(header, records):
    newHeader = editHeader(header)
    with open("FCSF_Team1_Sean.csv", "w") as file:
        # add header
        file.write(newHeader)

        # add student details
        for group_name, students in records.items():
            for student in students:
                line = f"{group_name},{student.Student_ID},{student.School},{student.Name},{student.Gender},{student.CGPA}, {student.Tutorial_Group}-{student.Subgroup}\n"
                file.write(line)

def main():
    group_options = {"1": 4, "2": 5, "3": 6, "4": 7, "5": 8, "6": 9, "7": 10}
    loop_menu = True
    group_size = 5
    while loop_menu:
        # Print Main Menu Option
        print("\nPlease select a group size:")
        for key, value in group_options.items():
            print(f"{key}. Groups of {value}")
        print("8. Quit")

        # Ask for user choice
        user_input = input(f"Enter your choice (1–8): ").strip()

        # Quits the programme
        if user_input == "8":
            print("Quitting Program...")
            sys.exit()

        elif user_input in group_options:
            # Assign group size based on user input
            group_size = group_options[user_input]

            # Confirm with user if this is his choice
            while True:
                confirmation_input = input(f"You selected groups of {group_size}. Confirm? (y/n): ").strip().lower()
                if confirmation_input == "y":
                    print(f"Group size: {group_size}")
                    loop_menu = False
                    break  # Exit confirmation loop
                elif confirmation_input == "n":
                    print("Returning to menu...")
                    break
                else:
                    print("Invalid input. Please enter 'y' or 'n'.")

        # if user_input enters invalid input
        else:
            print("Invalid input. Please enter a number from 1 to 8.")

    header, old_records = retrieve_data()

    records, all_tut_subgroups = categorize_records(old_records,group_size)

    print("Saving records to CSV file")
    saveToCSV(header, records)

    cgpa_score_list, gender_score_list, school_score_list, overall_score_list = extract_score_list(all_tut_subgroups)
    evaluate_score(cgpa_score_list, gender_score_list, school_score_list, overall_score_list)
    plot_histogram_score(cgpa_score_list, gender_score_list, school_score_list, overall_score_list)
    rank_score(cgpa_score_list, gender_score_list, school_score_list, overall_score_list)

if __name__ == "__main__":
  main()