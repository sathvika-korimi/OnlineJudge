from django.shortcuts import render
from submit.forms import CodeSubmissionForm
from pathlib import Path
from django.conf import settings
import uuid
import subprocess

# Create your views here.
def submit(request):
    if request.method == 'POST':
        form = CodeSubmissionForm(request.POST)
        if form.is_valid():
            submission = form.save()
            print(submission)
            output = run_code(
                submission.language, submission.code, submission.input_data
            )
            submission.output_data = output
            # submission.save() Do we need this?
            return render(request, 'form.html', { 'submission': submission, 'form': form })
    else:
        form = CodeSubmissionForm()
        context = {
            'form': form,
        }
    return render(request, 'form.html', context)
    
def run_code(language, code, input_data):

    
    project_path = Path(settings.BASE_DIR)
    # create these folders in the project to store inputs, outputs and code
    dir_path = project_path / "codes"
    if not dir_path.exists():
        dir_path.mkdir(parents = True, exist_ok = True)

    codes_dir = project_path / "codes"

    unique = str(uuid.uuid4())

    code_file_name = f"{unique}.{language}"

    code_file_path = codes_dir / code_file_name

    def compileAndRun(forLang):
        with open(code_file_path, "w") as code_file:
            code_file.write(code)

        executable_path = codes_dir / unique
        compile_result = subprocess.run(
            [forLang, str(code_file_path), "-o", str(executable_path)],
            capture_output = True,
            text = True
        )

        # Need to handle the errors and show to the users on the same page with user typed text in form
        if compile_result.returncode == 0:
            process = subprocess.run(
                [str(executable_path)],
                input = input_data,
                capture_output = True,
                text = True
            )
            if process.returncode == 0:
                return process.stdout
            return getError(str(process.stderr).strip(), str(code_file_path))
        return getError(str(compile_result.stderr).strip(), str(code_file_path))

    if language == 'c':
        return compileAndRun('gcc')
    
    if language == 'cpp':
        return compileAndRun('clang++')
        
    if language == 'py':
        with open(code_file_path, "w") as code_file:
            code_file.write(code)
        process = subprocess.run(
            ["python3", str(code_file_path)],
            input = input_data,
            capture_output = True,
            text = True
        )
        
        if process.returncode == 1:
            return getError(process.stderr, str(code_file_path))
        return process.stdout
        

def getError(error_string, code_file_path):
    newString = error_string.replace(str(code_file_path), "Sumbission file ")
    return newString






        