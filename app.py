import streamlit as st
from pyserini.search import pysearch
from PIL import Image
import os
from corpus import parse_and_index
import validators

def load_mappings():
    d = 'indexes'
    SITE2INDEX, SITE2WC = {}, {}
    for o in os.listdir(d):
        if os.path.isdir(os.path.join(d, o)):
            site_name = o.split("_")[0].split("-")[-1]
            SITE2INDEX[site_name] = os.path.join(d, o)
            date = "_".join(o.split("_")[1:])
            SITE2WC[site_name] = os.path.join("wordcloud", f"{site_name}_{date}_wc.png")
    return SITE2INDEX, SITE2WC

if __name__ == '__main__':
    st.title('Retriever for contents within a site')
    st.subheader("Enter a site URL to parse, index and query")
    url = st.text_input("")
    new_added=""
    if url.strip() != "":
        if not validators.url(url):
            st.error("The input is not a url, enter again")
        elif not url.startswith("http"):
            st.error("You may miss https://")
        else:
            st.info(parse_and_index(st, url))
            url_name = url.split("//")[1].strip("/")
            st.markdown(f"<small> You selected: [{url_name}]({url}). </small>",
                        unsafe_allow_html=True)
            new_added= url_name

    SITE2INDEX, SITE2WC = load_mappings()
    st.subheader("Or select a pre-indexed example below")

    if new_added=="":
        option = st.selectbox("Whose blog site you want to query?", tuple(SITE2INDEX.keys()))
    else:
        option = st.selectbox("Whose blog site you want to query?", tuple(SITE2INDEX.keys()),tuple(SITE2INDEX.keys()).index(new_added))

    st.markdown(f"You selected site: http://{option}.")
    searcher = pysearch.SimpleSearcher(SITE2INDEX[option])

    query = st.text_input("Enter query here to search the site at paragraph level (Anserini BM25)")
    if query != "":
        hits = searcher.search(query, 1000)
        offset = st.number_input(f"Display number of results (offset, total={len(hits)})?", value=0,
                                 step=min(10, len(hits) - 1), min_value=0,
                                 max_value=len(hits) - 1)

        for idx, hit in enumerate(hits[offset:offset+min(20,len(hits)-1)]):
            st.markdown(f"> {hit.raw} Source: {hit.docid.split('_')[0]}", unsafe_allow_html=True)

    image = Image.open(SITE2WC[option])
    st.image(image, caption=f'Word Cloud of {option}', use_column_width=True)
    # streamlit run app.py
