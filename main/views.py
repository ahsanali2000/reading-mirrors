import os

from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from utils.code import main


def index(request):
    if request.method == 'POST' and request.FILES['myfile']:
        my_file = request.FILES['myfile']
        fs = FileSystemStorage()
        if ".pdf" not in my_file.name:
            return render(request, 'main.html', {"error": "Please upload a pdf File."})
        file1 = open("uploaded/" + my_file.name, "wb+")
        file1.write(my_file.read())
        file1.close()
        results = main("uploaded/" + my_file.name, "utils/common_occupations.txt")
        try:
            for root, dirs, files in os.walk("uploaded", topdown=False):
                for name in files:
                    try:
                        fs.delete(os.path.join("uploaded", name))
                    except Exception as e:
                        print(e)
        except Exception as e:
            print(e)

        return render(request, 'main.html', {"data": results})

    return render(request, 'main.html')#, {"data": {"men": 50, "women": 50, "men_occ": 50, "women_occ": 50}})
