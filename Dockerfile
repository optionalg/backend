FROM python:3.5
ADD . /code
WORKDIR /code
RUN pip3 install --upgrade pip
RUN pip3 install --upgrade -r requirements.txt
RUN python -m nltk.downloader vader_lexicon
RUN python -m nltk.downloader stopwords
CMD python3 main.py
