#----------------------------------------------------
# Mini BearTracks
# Purpose of program: Manage student timetables by enrolling in or dropping courses, and displaying the current timetable.
#
# Author: Hasan Khan
# Collaborators/references: https://www.w3schools.com/python/ref_string_ljust.asp
#----------------------------------------------------
from io import StringIO
import sys
import streamlit as st
import pandas as pd
import random

def welcome_to_beartracks():
    """
    Print a welcome message for Mini-BearTracks.
    
    Inputs: None
    
    Returns: None
    """
    print("==========================")
    print("Welcome to Mini-BearTracks")
    print("==========================")    

def getAction():
    """
    Prompt the user with possible actions and obtain their choice.
    
    Returns: 
        str: The user's selected action ('1', '2', '3', or '4') or invalid entry.
    """
    return st.sidebar.selectbox("Choose an action", 
                                ["Print Timetable", "Enroll in Course", "Drop Course", "Quit"])

def format_course(course_string):
    """Formats the course abbreviation code."""
    course_name, course_number = course_string.split()
    if len(course_name) > 4:
        formatted_name = course_name[:3] + "*"
    else:
        formatted_name = course_name
    return f"{formatted_name} {course_number}"

def generate_timetable(student_id):
    """
    Generates the timetable for the inputted student (doesnt print).
    
    Inputs: student_id (str): ID of the student.
    
    Returns: dict: Timetable dictionary made for the inputted student.
    """
    # Store courses in a dictionary with course name as key and its details as values
    courses_data = {}
    with open("courses.txt", "r") as f:
        for line in f:
            course_name, timeslot, max_students, lecturer = map(str.strip, line.split(';'))
            courses_data[course_name] = {"timeslot": timeslot, "max_students": int(max_students), "lecturer": lecturer}

    # Initialize enrolled_courses as an empty list
    enrolled_courses = []

    # Check which courses the student is enrolled in
    with open("enrollment.txt", "r") as f:
        for line in f:
            if ':' in line:  # Only proceed if colon exists in the line
                course_name, enrolled_student_id = map(str.strip, line.split(':'))
                if enrolled_student_id == student_id:
                    enrolled_courses.append(course_name)

    # Construct a timetable
    timetable = {}
    for course in enrolled_courses:
        if course not in courses_data:
            print(f"Warning: Course {course} not found in courses.txt. Skipping...")
            continue
        day_time = courses_data[course]["timeslot"].split()
        day = 'MWF' if 'MWF' in day_time[0] else 'TR' 
        time = day_time[1]    

        # Calculates seat count for the specified course
        seat_count = sum(1 for line in open("enrollment.txt") if course + ':' in line)

        # Calculates the number of open seats for the current course
        open_seats = courses_data[course]["max_students"] - seat_count

        if day not in timetable:
            timetable[day] = {}
        timetable[day][time] = {"course": course, "room": open_seats}  # Use open_seats instead of max_students

    return timetable

def print_timetable(courses):
    """
    Print the timetable in a structured format using Streamlit.
    
    Inputs: courses (dict): Dictionary of the courses.
    
    Returns: None
    """
    headers = ['Mon', 'Tues', 'Wed', 'Thurs', 'Fri']
    day_codes = ['MWF', 'TR', 'MWF', 'TR', 'MWF']
    times = ['8:00', '8:30', '9:00', '9:30', '10:00', '10:30', '11:00', '11:30', 
             '12:00', '12:30', '13:00', '13:30', '14:00', '14:30', '15:00', '15:30', '16:00', '16:30']

    # Define colors for each course
    course_colors = {}
    for day_code in day_codes:
        for time in times:
            if courses.get(day_code, {}).get(time):
                course = format_course(courses[day_code][time]['course'])
                if course not in course_colors:
                    # Store the color with the formatted course name as the key
                    course_colors[course] = f"background-color: #{random.randint(0, 0xFFFFFF):06x};"

    span_map = {'MWF': 2, 'TR': 3}
    # Create the timetable using Streamlit
    timetable_html = '<table style="width: 100%; border-collapse: collapse;">'
    timetable_html += '<tr><th></th>'
    for day in headers:
        timetable_html += f'<th style="text-align: center;">{day}</th>'
    timetable_html += '</tr>'

    for time_index, time in enumerate(times):
        # Only create a time label if there is a course starting at this time
        timetable_html += f'<tr><td style="text-align: right;">{time}</td>'
        for day_index, day in enumerate(headers):
            day_code = day_codes[day_index]
            if courses.get(day_code, {}).get(time):
                course = format_course(courses[day_code][time]['course'])
                room = str(courses[day_code][time]['room'])
                color = course_colors[course]
                rowspan = span_map.get(day_code, 1)
                timetable_html += f'<td rowspan="{rowspan}" style="{color} border: 1px solid black; text-align: center; vertical-align: top;">{course}<br>{room}</td>'
            else:
                # Skip cells that are covered by a rowspan from a previous row
                if any(courses.get(day_code, {}).get(times[prev_time_index]) for prev_time_index in range(max(0, time_index - rowspan + 1), time_index)):
                    continue
                else:
                    timetable_html += '<td style="border: 1px solid black;"></td>'
        timetable_html += '</tr>'
    timetable_html += '</table>'

    st.write(timetable_html, unsafe_allow_html=True)
            

def get_valid_student(student_id_input):
    with open("students.txt", "r") as f:
        for line in f:
            parts = line.strip().split(',')
            if len(parts) >= 3:
                student_id = parts[0].strip()
                faculty = parts[1].strip()
                student_name = ','.join(parts[2:]).strip()
                if student_id_input == student_id:
                    return student_id, student_name
            
    st.error("Invalid student ID. Cannot continue with course enrollment.")
    return None, None

def get_valid_course(student_timetable, course_name_input):
    """
    Validates the course name and returns the course name and details if valid.
    """
    course_details = {}
    with open("courses.txt", "r") as f:
        for line in f:
            course_name, timeslot, max_students, lecturer = map(str.strip, line.split(';'))
            if course_name_input.upper() == course_name:
                course_details = {
                    "timeslot": timeslot,
                    "max_students": int(max_students),
                    "lecturer": lecturer
                }

    if not course_details:
        return None

    day_time = course_details["timeslot"].split()
    day_format = 'MWF' if 'MWF' in day_time[0] else 'TR'
    time = day_time[1]

    for existing_day, existing_courses in student_timetable.items():
        if day_format == existing_day:
            if time in existing_courses:
                st.warning(f"Schedule conflict: already registered for course on {day_format} {time}.")
                return None

    seat_count = sum(1 for line in open("enrollment.txt", "r") if course_name_input + ':' in line)
    if seat_count >= course_details["max_students"]:
        st.warning(f"Cannot enroll. {course_name_input} is already at capacity.")
        return None

    return course_name_input, course_details


def enroll_student_in_course(student_id, student_name, course_name, course_details):
    """
    Enroll a student in a course and update the file.
    
    Inputs: student_id (str): ID of the student.
            student_name (str): Name of the student.
            course_name (str): Name of the course.
            course_details (dict): Details of the course.
    
    Returns:
        None
    """    
    with open("enrollment.txt", "a") as f:
        f.write(f"\n{course_name}: {student_id}")
    day_time = course_details["timeslot"].split()
    day = 'MWF' if 'MWF' in day_time[0] else 'TR'
    time = day_time[1]    
    
    print(f"{student_name} has successfully been enrolled in {course_name}, on {day} {time}")
    
def is_student_already_enrolled(student_id, course_name):
    """
    Checks if a student is already enrolled in a particular course.
    
    Inputs: student_id (str): ID of the student
    course_name (str): Course name.
    
    Returns: bool: True if the student is already enrolled, False otherwise.
    """
    with open("enrollment.txt", "r") as f:
        for line in f:
            if ':' in line:
                course_name_in_file, student_id_in_file = map(str.strip, line.split(':'))
                if course_name_in_file == course_name and student_id_in_file == student_id:
                    return True
    return False

    
def option1():
    student_id_input = st.text_input("Student ID:")
    if student_id_input:
        student_id, student_name = get_valid_student(student_id_input)
        if student_id and student_name:
            st.write(f"Timetable for {student_name.upper()}")
            courses = generate_timetable(student_id)
            print_timetable(courses)
        else:
            st.error("Invalid student ID. Cannot print timetable.")

def option2():
    """Enrolls a student in a course."""
    st.subheader("Enroll in Course")
    
    student_id_input = st.text_input("Student ID")
    if student_id_input:
        student_id, student_name = get_valid_student(student_id_input)
        if student_id:
            st.success(f"Valid student ID for {student_name}")
            
            course_name_input = st.text_input("Course Name")
            if course_name_input:
                course_name_input = course_name_input.upper()  # Convert course name to uppercase
                student_timetable = generate_timetable(student_id)
                result = get_valid_course(student_timetable, course_name_input)
                if result:
                    course_name, course_details = result
                    if is_student_already_enrolled(student_id, course_name):
                        st.warning(f"{student_name} is already enrolled in {course_name}.")
                    else:
                        if st.button("Enroll"):
                            enroll_student_in_course(student_id, student_name, course_name, course_details)
                            day_time = course_details["timeslot"].split()
                            day = 'MWF' if 'MWF' in day_time[0] else 'TR'
                            time = day_time[1]
                            st.success(f"{student_name} has successfully been enrolled in {course_name}, on {day} {time}")
                else:
                    st.error("Invalid course name or already enrolled.")
        else:
            st.error("Invalid student ID. Cannot continue with course enrollment.")
            
def option3():
    """
    Handles the option '3' to drop a course for a student.
    """    
    student_id_input = st.text_input("Enter student ID for dropping a course:")
    
    if student_id_input:
        student_info = get_valid_student(student_id_input)
        if student_info:
            student_id, student_name = student_info
            enrolled_courses = []
            with open("enrollment.txt", "r") as f:
                for line in f:
                    if ':' in line:
                        course_name, enrolled_student_id = map(str.strip, line.split(':'))
                        if enrolled_student_id == student_id:
                            enrolled_courses.append(course_name)

            if not enrolled_courses:
                st.write(f"{student_name} is not enrolled in any courses.")
                return

            course_to_drop = st.selectbox("Select course to drop:", enrolled_courses)
            
            if st.button("Drop Course"):
                # Update the enrollment file
                with open("enrollment.txt", "r") as f:
                    lines = f.readlines()

                with open("enrollment.txt", "w") as f:
                    for line in lines:
                        if ':' in line:
                            course_name, enrolled_student_id = map(str.strip, line.split(':'))
                            if not (course_name == course_to_drop and enrolled_student_id == student_id):
                                f.write(line)

                st.success(f"{student_name} has successfully dropped {course_to_drop}.")
        else:
            st.error("Invalid student ID.")
def option4():
    st.subheader("Add New Student")
    
    admin_password = st.text_input("Enter the admin password:", type="password")
    if admin_password == "password123":
        student_id_input = st.text_input("Enter a new student ID (6 digits):")
        if student_id_input:
            if len(student_id_input) != 6 or not student_id_input.isdigit():
                st.error("Invalid student ID. Please enter a 6-digit number.")
            else:
                existing_ids = set()
                with open("students.txt", "r") as f:
                    for line in f:
                        student_id = line.strip().split(",")[0]
                        existing_ids.add(student_id)
                
                if student_id_input in existing_ids:
                    st.error("Student ID already exists. Please enter a unique ID.")
                else:
                    faculty_options = ["BUS", "EDU", "ART", "SCI", "ENG", "NUR", "LAW", "KIN", ]
                    faculty_input = st.selectbox("Select the faculty:", faculty_options)
                    
                    full_name_input = st.text_input("Enter the full name:")
                    
                    if st.button("Add Student"):
                        with open("students.txt", "a") as f:
                            f.write(f"\n{student_id_input},{faculty_input},{full_name_input}")
                        st.success("Student added successfully.")
    else:
        st.error("Incorrect admin password. Access denied.")
def option5():
    st.subheader("Drop Out")
    
    student_id_input = st.text_input("Enter the student ID (CCID) to drop out:")
    if student_id_input:
        found = False
        updated_lines = []
        with open("students.txt", "r") as f:
            for line in f:
                student_id = line.strip().split(",")[0]
                if student_id == student_id_input:
                    found = True
                else:
                    updated_lines.append(line)
        
        if found:
            with open("students.txt", "w") as f:
                f.writelines(updated_lines)
            st.success(f"Student with CCID {student_id_input} has been dropped out.")
        else:
            st.warning(f"Student with CCID {student_id_input} not found.")

def option6():
    st.subheader("New Course Offering")
    
    admin_password = st.text_input("Enter the admin password:", type="password")
    if admin_password == "password123":
        course_name_input = st.text_input("Enter the course name (e.g., CMPUT 101):")
        if course_name_input:
            course_name_parts = course_name_input.split()
            if len(course_name_parts) != 2:
                st.error("Invalid course name format. Please enter the course name as 'SUBJECT COURSENUMBER' (e.g., CMPUT 101).")
            else:
                day_options = ["MWF", "TR"]
                day_input = st.selectbox("Select the days:", day_options)
                
                times = ['8:00', '9:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00']
                selected_time = st.selectbox("Select the time:", times)
                
                instructor_name_input = st.text_input("Enter the instructor name:")
                
                max_students_input = st.text_input("Enter the maximum number of students:")
                
                if st.button("Add Course"):
                    if not instructor_name_input or not max_students_input:
                        st.error("Please fill in all the required fields.")
                    else:
                        try:
                            max_students = int(max_students_input)
                            with open("courses.txt", "a") as f:
                                f.write(f"\n{course_name_input}; {day_input} {selected_time}; {max_students}; {instructor_name_input}")
                            st.success("Course added successfully.")
                        except ValueError:
                            st.error("Invalid maximum number of students. Please enter a valid integer.")
    else:
        st.error("Incorrect admin password. Access denied.")

def option7():
    st.subheader("Remove Course")
    
    admin_password = st.text_input("Enter the admin password:", type="password")
    if admin_password == "password123":
        course_name_input = st.text_input("Enter the course name to remove (e.g., CMPUT 101):")
        if course_name_input:
            course_name_input = course_name_input.upper()
            course_found = False
            updated_lines = []
            with open("courses.txt", "r") as f:
                for line in f:
                    course_name = line.strip().split(";")[0]
                    if course_name == course_name_input:
                        course_found = True
                    else:
                        updated_lines.append(line)
            
            if course_found:
                with open("courses.txt", "w") as f:
                    f.writelines(updated_lines)
                st.success(f"Course {course_name_input} has been removed.")
            else:
                st.warning(f"Course {course_name_input} not found.")
    else:
        st.error("Incorrect admin password. Access denied.")

def main():
    st.title("Mini-BearTracks")
    st.header("Welcome to Mini-BearTracks")

    action = st.sidebar.selectbox("Choose an action", ["Print Timetable", "Enroll in Course", "Drop Course", "Add New Student", "Drop Out", "New Course Offering", "Remove Course", "Quit"])

    if action == "Print Timetable":
        option1()
    elif action == "Enroll in Course":
        option2()
    elif action == "Drop Course":
        option3()
    elif action == "Add New Student":
        option4()
    elif action == "Drop Out":
        option5()
    elif action == "New Course Offering":
        option6()
    elif action == "Remove Course":
        option7()
    elif action == "Quit":
        st.write("Goodbye")
        sys.exit()

if __name__ == "__main__":
    main()