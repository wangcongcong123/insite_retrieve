# InsiteRetriever: A web app for retrieving contents within a site. 


### Motivation

This app is inspired by the fact that many bloggers who are skilled in one field/domain or another maintain blogging sites to share their knowledge but there are usually no searching boxes provided on their sites. However, more broadly, it is not limited in blogging sites but can be applied to any other type of sites.
 
 Due to the lack of resources in comparison to big search engines like Google, this functions only for in-site searching while at paragraph level. Hopefully this helps information seekers to get domain-specific knowledge efficiently from an expert's (e.g., the bloggers) site or any other type sites.
 
### Demo ([Notebook](insite_retrieve.ipynb)) 
![demo](demo.gif)

### Features
- Using [Anserini tool](https://github.com/castorini/anserini) for efficient indexing and querying.
- Recursively scrape the contents of a site to make comprehensive.
- Designed flexiblely to query contents from a site at paragraph level, namely the `<p>` tag of a HTML page.
- To query some pre-built indexes or parse, index and query a site from scratch simply given its http URL. Once done, no need to prase and index the same site again. 
- The sites that have been pre-indexed as of 2020-07-18, available in this repository and can be directly queried are:
    - http://colah.github.io
    - http://jalammar.github.io
    - http://karpathy.github.io
    - http://ruder.io
    - http://wangcongcong123.github.io mine :)

### Quick Start
```
git clone https://github.com/wangcongcong123/insite_retrieve.git
cd insite_retrieve
pip install -r requirements.txt


apt-get install maven -qq
git clone https://github.com/castorini/anserini.git
cd anserini
mvn clean package appassembler:assemble -DskipTests -Dmaven.javadoc.skip=true
cd ..

streamlit run app.py
```
### Todo ideas
Let me know if any questions, feedback is welcome. Contributions or pull requests are highly encouraged. Below gives some Todo ideas.

- Now the system only works using sparse retrieval-based BM25 model, so more work can go to extend the system to support dense retrieval-based techniques such as the recent advance: [RetriBERT](https://yjernite.github.io/lfqa.html).
- Now the system only includes a word cloud image indicating what the topics of a site are generally about, so more work can go to add more features such as topic modelling on the site's contents.
- More work can go to the presentation of retrived results, such as presenting them with more supplementary data (title, paragraph original location), highlighting exactly-matched words, better rendering etc.
- Now the contents from each site are coarsely extracted, more filtering strategies are expected for improving the quality of the extracted contents.
