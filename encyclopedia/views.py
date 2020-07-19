from django import forms
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from random import choice
import markdown2

from . import util

class NewEntryForm(forms.Form):
    title = forms.CharField(label="Title", error_messages={"required": "Please enter the Title"})
    content = forms.CharField(label="Description", widget=forms.Textarea, error_messages={"required": "Please enter the Description"})

    def clean(self):
        cd = self.cleaned_data
        #if not self.edit_mode:
        if cd.get('title') is None: cd['title'] = "" 
        if cd.get('title').lower() in (entry.lower() for entry in util.list_entries()):
            self.add_error('title', "This entry already exists")
        return cd 

class EditEntryForm(forms.Form):
    title = forms.CharField(label="Title", disabled=True)
    content = forms.CharField(label="Description", widget=forms.Textarea, error_messages={"required": "Please enter the Description"})

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title):
    return render(request, "encyclopedia/entry.html", {
        "exists": util.get_entry(title) is not None,
        "title": title.capitalize(),
        "entry": markdown2.markdown(util.get_entry(title))
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
        form = NewEntryForm(request.POST)
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
        "form": NewEntryForm()
    })

def edit(request, title):
    if request.method == "POST":
        form = EditEntryForm(request.POST, initial={"title": title})
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            util.save_entry(title, content)
            return HttpResponseRedirect(reverse("entry", args=[title]))
        else:
            return render(request, "encyclopedia/edit.html", {
                "form": form,
                "title": title
            })

    return render(request, "encyclopedia/edit.html", {
        "form": EditEntryForm(initial={"title": title, "content": util.get_entry(title)}),
        "title": title
    })

def random(request):
    title = choice(util.list_entries())
    return HttpResponseRedirect(reverse("entry", args=[title]))