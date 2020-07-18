from bs4 import BeautifulSoup
import requests
from tqdm import tqdm
import re
import matplotlib.pyplot as plt
import json, os

import datetime

def get_passages(url):
    """
    get passages by url
    :param url: the url to request a webpage
    :return: passages from the page
    """
    req = requests.get(url)
    soup = BeautifulSoup(req.content, 'html.parser')
    # filter passages with chars length > 10
    passages = [{"id": f"{url}_p{i}", "contents": passage.getText()} for i, passage in enumerate(soup.findAll('p')) if
                len(passage.getText()) > 10]

    return passages


def is_non_html(href):
    return re.search(r".png|.pdf|.txt|.img", href) != None


check_hrefs = []


def get_hrefs(url):
    """
    get in-site hrefs recursively, there is a room to make the method more efficient
    :param url: the root url of a website
    :return: all in-site hrefs
    """
    req = requests.get(url)
    soup = BeautifulSoup(req.content, 'html.parser')
    hrefs = []
    for atag in tqdm(soup.findAll('a'), desc="get in-site hrefs"):
        if atag.has_attr("href"):
            href = atag["href"]
            # we don't like any in-site non html pages
            if href not in check_hrefs and not href.startswith("http") and not is_non_html(href):
                check_hrefs.append(href)
                sub_hrefs = get_hrefs(url + href)
                check_hrefs.extend(sub_hrefs)
                hrefs.extend(sub_hrefs + [href])
    return hrefs


def parse_passages(url,st=None):
    """
    parse passages by first obtaining all in-site hrefs of the url site and then get all passages in each of the hrefs pages
    :param url:
    :return:
    """
    # get passages in the root page
    passages = get_passages(url)
    # get hrefs recursively starting from the root page
    if st is not None:
        info1=st.info("Get hrefs recursively within the site %s..." % url)

    hrefs = get_hrefs(url)

    number_hrefs=len(hrefs)

    if st is None:
        print(f"The are {number_hrefs} hrefs in total obtained")
    else:
        info2=st.info(f"The are {number_hrefs} hrefs in total obtained")
        progress_bar = st.progress(0)

    progress=1
    for href in tqdm(hrefs, desc="get passages b url"):
        passages.extend(get_passages(url + href))
        if st is not None:
            info1.info("Requesting contents from the obtained hrefs")
            progress_bar.progress(min(progress / number_hrefs, 1.0))
        progress+=1

    # if st is not None:
    #     info1.empty()
    #     info2.empty()
    #     progress_bar.empty()
    return passages

def generate_wordcloud(passages, word_cloud_file="word_cloud.png"):
    """
    generate word cloud using mask image, code references:
    https://amueller.github.io/word_cloud/auto_examples/frequency.html#sphx-glr-auto-examples-frequency-py
    :param passages:
    :return:
    """
    text = " ".join(passages)
    from wordcloud import WordCloud, STOPWORDS
    if not os.path.isdir("wordcloud"):
        os.makedirs("wordcloud",exist_ok=True)
    # mask = np.array(Image.open("wordcloud/mask.png"))
    # contour_width = 3, contour_color = 'steelblue'
    wc = WordCloud(stopwords=STOPWORDS, margin=1, max_words=2000, background_color='white').generate(text)
    plt.axis("off")
    plt.figure(figsize=(12, 10))
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.savefig(f"wordcloud/{word_cloud_file}", format="png")
    # plt.show()

def anserini_index(index_name):
    if not os.path.isdir("indexes"):
        os.makedirs("indexes",exist_ok=True)

    os.system(f'sh anserini/target/appassembler/bin/IndexCollection -threads 9 -collection JsonCollection ' +
              f'-generator DefaultLuceneDocumentGenerator -input corpus/{index_name} ' +
              f'-index indexes/lucene-index-{index_name} -storePositions -storeDocvectors -storeRaw')

def write_to_jsonl(passages, path="./",filename=""):

    if not os.path.isdir(path):
        os.makedirs(path)

    with open(os.path.join(path, filename), "w+") as f:
        for each in passages:
            f.write(json.dumps(each) + "\n")

def read_from_jsonl(path="./",filename=""):
    passages = []
    with open(os.path.join(path, filename), "r") as f:
        for each in f:
            passages.append(json.loads(each.strip()))
    return passages

def parse_and_index(st,site_url):
    site_name = site_url.split("//")[1].strip("/")
    now = datetime.datetime.now()
    date=f"{now.year}_{now.month}_{now.day}"

    if os.path.isdir(os.path.join("indexes",f"lucene-index-{site_name}_{date}")):
        return "There exists pre-indexed for this site"
    else:
        passages = parse_passages(site_url,st=st)
        st.info(f"Write the obtained contents for indexing")
        write_to_jsonl(passages, path=os.path.join("corpus",site_name+f"_{date}"),filename=site_name+f"_{date}.jsonl")
        st.info(f"Generate a word cloud for the obtained contents")
        generate_wordcloud([each["contents"] for each in passages], word_cloud_file=site_name+f"_{date}_wc.png")
        st.info(f"Index by anserini...")
        anserini_index(site_name + f"_{date}")
    return "done"

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Generate corpus for indexing.')
    # wangcongcong123.github.io
    parser.add_argument('--blog_site', required=False, default='https://jiazhengli.com//',
                        help='the root url of blog site')

    parser.add_argument('--to_file', required=False, default='jiazhengli.com_2020_07_18.jsonl',
                        help='jsonl file to generate for anserini indexing')

    parser.add_argument('--word_cloud_file', required=False, default='jiazhengli.com_2020_07_18_wc.png',
                        help='the world cloud file to generate based on the corpus')

    args = parser.parse_args()
    passages = parse_passages(args.blog_site)
    write_to_jsonl(passages, path=os.path.join("corpus",args.blog_site.split("//")[1]),filename=args.to_file)
    # passages= read_from_jsonl(path=os.path.join("corpus",args.blog_site.split("//")[1]),filename=args.to_file)
    generate_wordcloud([each["contents"] for each in passages], word_cloud_file=args.word_cloud_file)
