import os
from django.shortcuts import render, redirect
from myapp.forms import DocumentForm, SearchForm, QuestionForm
from myapp.models import Document
from whoosh import index
from whoosh.fields import Schema, TEXT
from whoosh.qparser import QueryParser
import spacy

# Load the SpaCy model
nlp = spacy.load("en_core_web_sm")

def index_documents(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data['content']
            document = Document(content=content)
            document.save()
            schema = Schema(content=TEXT(stored=True))
            if not index.exists_in("indexdir"):
                os.makedirs("indexdir")
                ix = index.create_in("indexdir", schema)
            else:
                ix = index.open_dir("indexdir")
            writer = ix.writer()
            writer.add_document(content=content)
            writer.commit()
            return redirect('index_documents')
    else:
        form = DocumentForm()
    return render(request, 'index.html', {'form': form})


def search(request):
    if request.method == 'POST':
        query = request.POST.get('query')
        ix = index.open_dir("indexdir")
        with ix.searcher() as searcher:
            query = QueryParser("content", ix.schema).parse(query)
            results = searcher.search(query)
            highlighted_results = [x.highlights("content") for x in results]
            return render(request, 'search_results.html', {'results': highlighted_results})
    else:
        form = SearchForm()
    return render(request, 'search.html', {'form': form})


def extract_entities(question, doc):
    doc = nlp(doc)
    ents = [ent.text for ent in doc.ents]
    ans_type = None
    for sent in doc.sents:
        if any(word.text.lower() in question for word in sent):
            sent_ents = [ent.label_ for ent in sent.ents]
            if "PERSON" in sent_ents:
                ans_type = "PERSON"
            elif "ORG" in sent_ents:
                ans_type = "ORG"
            elif "GPE" in sent_ents:
                ans_type = "GPE"
            else:
                ans_type = "OTHER"
    return ents, ans_type


def question(request):
    if request.method == 'POST':
        question = request.POST.get('question')
        ix = index.open_dir("indexdir")
        with ix.searcher() as searcher:
            query = QueryParser("content", ix.schema).parse(question)
            results = searcher.search(query)
            if results:
                answer = results[0].get("content")
                ents, ans_type = extract_entities(question, answer)
                if ans_type in ("PERSON", "ORG", "GPE"):
                    answer = ents[0]
            else:
                answer = "Sorry, I could not find an answer to your question."
            return render(request, 'question.html', {'answer': answer})
    else:
        form = QuestionForm()
    return render(request, 'question.html', {'form': form, 'answer': ''})

