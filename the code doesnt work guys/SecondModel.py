import csv
import random
import numpy as np

def read_csv_data():
    """Reads input data from CSV files."""
    tutors, courses, timeslots, max_hours, preferences = [], [], [], {}, {}
    
    # Read tutordata1.csv
    with open("tutordata1.csv", mode='r') as file:
        lines = file.readlines()
        
        # need tutors courses and timeslots
        tutors = eval(lines[8].split(':')[1].strip())
        courses = eval(lines[15].split(':')[1].strip())
        timeslots = eval(lines[22].split(':')[1].strip())
        
        max_hours = {tutor: 144 for tutor in tutors}  # Uh 

        # need prefrences:
        p_start = next(i for i, line in enumerate(lines) if line.startswith("p:")) + 1
        preferences = {}
        for i, tutor in enumerate(tutors):
            preferences[tutor] = {course: float(val) for course, val in zip(courses, lines[p_start + i].strip().split())}
    
    
    return tutors, courses, timeslots, max_hours, preferences
  

def read_assignments():
    """Reads existing assignments from tutor_assignments.csv."""
    assignments = {}
    
    with open("tutor_assignments.csv", mode='r') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            tutor, course, timeslot = row
            timeslot = int(timeslot)
            if tutor not in assignments:
                assignments[tutor] = []
            assignments[tutor].append((course, timeslot))
    
    return assignments


def read_availability():
    """Reads availability data from updated_availability.csv."""
    availability = {}
    
    with open("updated_availability.csv", mode='r') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            tutor = row[0]
            availability[tutor] = {i: int(row[i+1]) for i in range(len(row) - 1)}
    
    return availability


def find_replacement_tutor(exited_tutor, assignments, availability, max_hours, preferences):
    """Finds a replacement tutor for an exited tutor."""
    if exited_tutor not in assignments:
        return None
    
    for course, timeslot in assignments[exited_tutor]:
        available_tutors = [t for t in availability if availability[t][timeslot] == 1]
        suitable_tutors = [t for t in available_tutors if len(assignments.get(t, [])) < max_hours[t]]
        
        if suitable_tutors:
            best_tutor = max(suitable_tutors, key=lambda t: preferences[t][course])
            assignments.setdefault(best_tutor, []).append((course, timeslot))
            availability[best_tutor][timeslot] = 0  # Update availability matrix
            return best_tutor, course, timeslot
    
    return None

def update_availability_matrix(assignments, availability):
    """Updates the availability matrix based on new assignments and writes it to a CSV."""
    for tutor in assignments:
        for course, timeslot in assignments[tutor]:
            availability[tutor][timeslot] = 0  # Tutor is now occupied
    
    with open("updated_availability.csv", mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Tutor Name"] + list(range(len(next(iter(availability.values()))))))
        for tutor in availability:
            writer.writerow([tutor] + [availability[tutor][t] for t in range(len(availability[tutor]))])

def main():
    tutors, courses, timeslots, max_hours, preferences = read_csv_data()
    assignments = read_assignments()
    availability = read_availability()
    
    exited_tutor = random.choice(list(assignments.keys()))  # Simulating an exited tutor
    print(f"Tutor {exited_tutor} exited. Finding replacement...")
    
    replacement = find_replacement_tutor(exited_tutor, assignments, availability, max_hours, preferences)
    if replacement:
        print(f"Replacement found: {replacement}")
    else:
        print("No suitable replacement found.")
    
    update_availability_matrix(assignments, availability)
    
    create_csv("tutor_assignments.csv", [(t, c, t_s) for t in assignments for c, t_s in assignments[t]])

def create_csv(output_file, assigned_tutors):
    """Creates a CSV file with the output assignments."""
    with open(output_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Tutor Name", "Course Name", "Timeslot"])
        for tutor, course, timeslot in assigned_tutors:
            writer.writerow([tutor, course, timeslot])

if __name__ == "__main__":
    main()