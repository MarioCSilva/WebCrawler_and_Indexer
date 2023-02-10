"""indexengine URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from myapp import views
from myapp.crawl_and_index import crawl_and_index_startup
from whoosh import index

if not index.exists_in("indexdir"):
    crawl_and_index_startup()

urlpatterns = [
    path("admin/", admin.site.urls),
    path('index_documents/', views.index_documents, name='index_documents'),
    path('search/', views.search, name='search'),
    path('question/', views.question, name='question'),
]
