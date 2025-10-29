from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import *

def base(request):
    return render(request,'base.html')


def dashboard(request):
    return render(request,'dashboard.html')

def home(request):
    return render(request,'home.html')


# CRUD 
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

from .models import Students
from .forms import StudentsForm


def studentRead(request):
    search_query = request.GET.get("search", "").strip()

    students = Students.objects.all().order_by("firstname", "lastname")

    if search_query:
        q = Q(firstname__icontains=search_query) | Q(lastname__icontains=search_query)
        # phone is an IntegerField, so we only match if the search is digits
        if search_query.isdigit():
            try:
                q |= Q(phone=int(search_query))
            except ValueError:
                pass
        students = students.filter(q)

    return render(request, "CRUD/read.html", {
        "students": students,
        "search_query": search_query,
    })


def studentCreate(request):
    if request.method == "POST":
        form = StudentsForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("studentRead")
    else:
        form = StudentsForm()
    return render(request, "CRUD/CreateUpdate.html", {"form": form, "title": "Add Student"})


def studentUpdate(request, pk):
    studentU = get_object_or_404(Students, pk=pk)
    if request.method == "POST":
        form = StudentsForm(request.POST, instance=studentU)
        if form.is_valid():
            form.save()
            return redirect("studentRead")
    else:
        form = StudentsForm(instance=studentU)
    return render(request, "CRUD/CreateUpdate.html", {"form": form, "title": "Edit Student"})


def studentDelete(request, pk):
    studentD = get_object_or_404(Students, pk=pk)
    if request.method == "POST":
        studentD.delete()
        return redirect("studentRead")
    return render(request, "CRUD/delete.html", {"student": studentD})
