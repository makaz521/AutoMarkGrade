from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CustomUser, MarkingTask , Report 
import docx
import PyPDF2
import os

from django.http import HttpResponseForbidden, HttpResponseServerError
from django.http import HttpResponse

from .forms import MarkingTaskForm

# views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import CustomUser, MarkingTask, Report  


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'You have been successfully logged in.')
            return redirect('index')  # Redirect to home page after successful login
        else:
            messages.error(request, 'Invalid username or password. Please try again.')
    return render(request, 'autograder/login.html')

@login_required
def upload(request):
    if request.method == 'POST':
        form = MarkingTaskForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the form data
            form_instance = form.save(commit=False)

            # Associate the uploaded_by field with the logged-in user
            form_instance.uploaded_by = request.user

            # Save marking scheme file to marking_schemes folder
            marking_scheme_file = form.cleaned_data['marking_scheme']
            if marking_scheme_file:
                form_instance.marking_scheme = marking_scheme_file

            # Save assignment files to marking_tasks folder
            assignment_files = request.FILES.getlist('files')
            for assignment_file in assignment_files:
                form_instance.files = assignment_file
                form_instance.save()

            # Redirect to a success page or render a success message
            return redirect('mark')
    else:
        form = MarkingTaskForm()
    return render(request, 'autograder/upload.html', {'form': form})

def index(request):
    return render(request, 'autograder/index.html')

@login_required
def results(request):
    marked_papers = []

        # Directory where marked papers are saved
    directory = 'C:/Users/User/Desktop/AutoMarkGrade/marking_tasks'

        # Iterate over files in the directory
    for filename in os.listdir(directory):
            if filename.startswith('marked_'):
                # Extract title and grade from the file names
                title = filename.replace('marked_', '').replace('.txt', '')
                new_title = f"marked_{title}"
                marked_paper_file_path = os.path.join(directory, filename)

                # Find the corresponding grade file
                grade_file_name = f"grade_{title}.txt"
                grade_file_path = os.path.join(directory, grade_file_name)

                # Read the grade from the grade file
                if os.path.exists(grade_file_path):
                    with open(grade_file_path, 'r') as grade_file:
                        grade = float(grade_file.readline())
                else:
                    grade = None

                # Add the paper details to the list
                marked_papers.append({'new_title': new_title, 'grade': grade, 'file_path': marked_paper_file_path})
    return render(request, 'autograder/results.html', {'marked_papers': marked_papers})



@login_required
def reports(request):
    return render(request, 'autograder/reports.html')


def user_logout(request):
    logout(request)
    return redirect('index')

@login_required
def lecturer(request):
    if request.user.role != CustomUser.LECTURER:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('error')
    marking_tasks = MarkingTask.objects.all()  # Retrieve all marking tasks
    marking_task_id = None
    if marking_tasks:
        marking_task_id = marking_tasks.first().id  # Get the ID of the first marking task
    context = {'marking_task_id': marking_task_id}
    return render(request, 'autograder/lecturer.html', context)


@login_required
def auditor(request):
    if request.user.role != CustomUser.AUDITOR:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('error')
    # Your auditor logic here
    return render(request, 'autograder/auditor.html')

def aud_lec(request):
    return render(request, 'autograder/error.html')


def scan_paper(marking_scheme_path, student_paper_path):
    # Check if files exist
    if not os.path.exists(marking_scheme_path) or not os.path.exists(student_paper_path):
        raise FileNotFoundError("One or both of the files does not exist.")

    # Load marking scheme and student paper files
    marking_scheme_text = load_text_file(marking_scheme_path)
    student_paper_text = load_text_file(student_paper_path)

    # Perform text comparison and generate marked paper
    marked_paper_text = generate_marked_paper(marking_scheme_text, student_paper_text)

    return marking_scheme_text, marked_paper_text

def load_text_file(file_path):
    _, file_extension = os.path.splitext(file_path)
    if file_extension.lower() == '.docx':
        doc = docx.Document(file_path)
        return '\n'.join([paragraph.text for paragraph in doc.paragraphs])
    elif file_extension.lower() == '.pdf':
        pdf_reader = PyPDF2.PdfReader(open(file_path, 'rb'))
        return '\n'.join([page.extract_text() for page in pdf_reader.pages])
    else:
        raise ValueError("Unsupported file format. Only DOCX and PDF files are supported.")

def generate_marked_paper(marking_scheme_text, student_paper_text):
    # Split the texts into lines
    marking_scheme_lines = marking_scheme_text.split('\n')
    student_paper_lines = student_paper_text.split('\n')

    marked_paper_lines = []

    # Iterate through the lines and compare
    for i, marking_scheme_line in enumerate(marking_scheme_lines):
        if i < len(student_paper_lines):
            student_line = student_paper_lines[i]
            if marking_scheme_line == student_line:
                marked_paper_lines.append(f"{marking_scheme_line} - Correct")
            else:
                marked_paper_lines.append(f"{marking_scheme_line} - Incorrect")
                marked_paper_lines.append(f"Student's answer: {student_line}")
        else:
            marked_paper_lines.append(f"{marking_scheme_line} - No answer from student")

    marked_paper_text = '\n'.join(marked_paper_lines)
    return marked_paper_text
from difflib import SequenceMatcher
from collections import Counter


from difflib import SequenceMatcher

def compare_texts(marking_scheme_text, student_paper_text):
    """
    Compare the marking scheme text and the student paper text,
    and return a similarity score as a percentage of 100.
    """
    # Calculate the similarity score using SequenceMatcher
    similarity = SequenceMatcher(None, marking_scheme_text, student_paper_text).ratio()

    # Convert similarity score to percentage
    similarity_percentage = similarity * 100

    # Round the similarity score to two decimal places
    similarity_percentage = round(similarity_percentage, 2)

    return similarity_percentage

# Example usage
marking_scheme_text = "This is the marking scheme."
student_paper_text = "This is the student's paper."
grade = compare_texts(marking_scheme_text, student_paper_text)

print("Grade:", grade)







 # Adjust this value based on your grading criteria...work on this code to make the grading to be very accurate
@login_required 
def mark_paper(request):
    if request.method == 'POST':
        marking_task_id = request.POST.get('marking_task')  # Retrieve the selected marking task ID
        marking_task = MarkingTask.objects.get(id=marking_task_id)
        new_title = marking_task.assign_title
        marking_scheme_path = marking_task.marking_scheme.path
        student_paper_path = marking_task.files.path

        # Scan the student paper and generate marked paper
        try:
            marking_scheme_text, marked_paper_text = scan_paper(marking_scheme_path, student_paper_path)
        except FileNotFoundError as e:
            return HttpResponseServerError(f"Error: {e}")

        # Perform marking and grading logic
        similarity_score = compare_texts(marking_scheme_text, marked_paper_text)  # Fix here
        grade = int(similarity_score * 1)

        # Save the marked paper text to a file in the student's directory
        marked_paper_dir = os.path.dirname(student_paper_path)
        marked_paper_filename = f"marked_{new_title}.txt"
        marked_paper_path = os.path.join(marked_paper_dir, marked_paper_filename)
        with open(marked_paper_path, 'w') as f:
            f.write(marked_paper_text)

        # Save the grade to a text file in the same directory
        grade_filename = f"grade_{new_title}.txt"
        grade_path = os.path.join(marked_paper_dir, grade_filename)
        with open(grade_path, 'w') as f:
            f.write(str(grade))

        return redirect('index')
    else:
        marking_tasks = MarkingTask.objects.all()  # Retrieve all marking tasks
        return render(request, 'autograder/select.html', {'marking_tasks': marking_tasks})

def write_report(request, marking_task_id):
    marking_task = get_object_or_404(MarkingTask, pk=marking_task_id)
    if request.method == 'POST':
        report_text = request.POST.get('report_text')
        lecturer = request.user  # Assuming lecturer is the currently logged-in user
        Report.objects.create(marking_task=marking_task, lecturer=lecturer, report_text=report_text)
        return redirect('lecturer')
    return render(request, 'autograder/write_report.html', {'marking_task': marking_task})

def view_reports(request):
    if request.user.role == CustomUser.AUDITOR:
        reports = Report.objects.all()  # Retrieve all reports
        return render(request, 'autograder/view_reports.html', {'reports': reports})
    else:
        # Handle unauthorized access
        return HttpResponseForbidden("You don't have permission to access this page.")
 
def create_report_for_auditor(request):
    marking_tasks = MarkingTask.objects.all()
    if request.method == 'POST':
        # Get the data from the form submission
        marking_task_id = request.POST.get('marking_task_id')  # Retrieve marking task ID
        report_text = request.POST.get('report_text')
        
        # Retrieve the marking task object
        marking_task = get_object_or_404(MarkingTask, pk=marking_task_id)
        
        # Create the report object and save it to the database
        auditor_user = request.user  # Assuming auditor is the currently logged-in user
        Report.objects.create(marking_task=marking_task, lecturer=auditor_user, report_text=report_text)
        
        # Redirect to a success page or any appropriate page
        return redirect('auditor')
    else:
        # Render the form for creating the report
        return render(request, 'autograder/create_report_for_auditor.html', {'marking_tasks': marking_tasks})


    lecture_report = get_object_or_404(Report, pk=pk)
    marked_papers = lecture_report.markedpaper_set.all()  # Fetch associated marked papers
    return render(request, 'papers/paper_detail.html', {'lecture_report': lecture_report, 'marked_papers': marked_papers})
