Build and activate a virtual environment for the project (optional):

    python3 -m venv venv

    venv/scripts/activate

Install requirements:

    pip install -r requirements.txt

Install the SpaCy english model:

    python3 -m spacy download en_core_web_sm


Make sure to have [PostgreSQL](https://www.postgresql.org/download/) installed and running, and set the details on the DATABASES section of the `indexengine/indexengine/settings.py` file.

In the file `websites_to_crawl.txt` there are a list of urls, that will be scraped and extracted content from them for indexation, at application startup.

Run the application:

    python3 manage.py runserver

There are 3 main url paths:

 - `/search`: Allows to search for indexed documents.
 - `/index_documents`: Allows to index new documents manually.
 - `/question`: Allows to make questions to the system.
