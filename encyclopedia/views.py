from django import forms
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse

from . import util

class EntryForm(forms.Form):
    title = forms.CharField(label="Title", error_messages={"required": "Please enter the Title"})
    content = forms.CharField(label="Description", widget=forms.Textarea, error_messages={"required": "Please enter the Title"})
    
    def clean(self):
        cd = self.cleaned_data
        if cd.get('title').lower() in (entry.lower() for entry in util.list_entries()):
            self.add_error('title', "This entry already exists")
        return cd 

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title):
    return render(request, "encyclopedia/entry.html", {
        "exists": util.get_entry(title) is not None,
        "title": title.capitalize(),
        "entry": util.get_entry(title)
    })

def search(request):
    key = request.GET["q"]
    #entry(request, title=title)
    if util.get_entry(key) is not None:
        return HttpResponseRedirect(reverse("entry", args=[key]))
    else:
        search_results = []
        for entry in util.list_entries():
            if key.lower() in entry.lower():
                search_results.append(entry)

        return render(request, "encyclopedia/search.html", {
            "exists": len(search_results) > 0,
            "key": key,
            "entries": search_results
        })

def create(request):
    if request.method == "POST":
        form = EntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            util.save_entry(title, content)
            return HttpResponseRedirect(reverse("entry", args=[title]))
        else:
            return render(request, "encyclopedia/create.html", {
                "form": form
            })

    return render(request, "encyclopedia/create.html", {
        "form": EntryForm()
    })

def edit(request, title):
    if request.method == "POST":
        form = EntryForm(request.POST)
        if form.is_valid():
            