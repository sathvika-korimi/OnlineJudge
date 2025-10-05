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
            return render(request, 'result.html', { 'submission': submission })

    else:
        form = CodeSubmissionForm()
        context = {
            'form': form,
        }
    return render(request, 'form.html', context)
    
def run_code(language, code, input_data):
    project_path = Path(settings.BASE_DIR)
    directories = ["codes", "inputs", "outputs"]
    # create these folders in the project to store inputs, outputs and code
    for directory in directories:
        dir_path = project_path / directory
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)

    codes_dir = project_path / directories[0]
    inputs_dir = project_path / directories[1]
    outputs_dir = project_path / directories[2]

    unique = str(uuid.uuid4())

    code_file_name = f"{unique}.{language}"
    input_file_name = f"{unique}.txt"
    output_file_name = f"{unique}.txt"

    code_file_path = codes_dir / code_file_name
    input_file_path = inputs_dir / input_file_name
    output_file_path = outputs_dir / output_file_name

    with open(code_file_path, "w") as code_file:
        code_file.write(code)
    
    with open(input_file_path, "w") as input_file:
        input_file.write(input_data)
    
    with open(output_file_path, "w") as output_file:
        pass

    if language == 'cpp':
        executable_path = codes_dir / unique
        compile_result = subprocess.run(
            ["clang++", str(code_file_path), "-o", str(executable_path)]
        )

        # Need to handle the errors and show to the users on the same page with user typed text in form
        if compile_result.returncode == 0:
            with open(input_file_path, "r") as input_file:
                with open(output_file_path, "w") as output_file:
                    subprocess.run(
                        [str(executable_path)],
                        stdin = input_file,
                        stdout = output_file,
                    )
        
    if language == 'py':
        with open(input_file_path, "r") as input_file:
            with open(output_file_path, "w") as output_file:
                subprocess.run(
                    ["python3", str(code_file_path)],
                    stdin = input_file,
                    stdout = output_file,
                )
    
    with open(output_file_path, "r") as output_file:
        output_data = output_file.read()
    
    return output_data




        