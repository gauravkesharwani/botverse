import os
import pinecone
from llama_index import download_loader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
from pprint import pprint
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
import requests
from bs4 import BeautifulSoup
import bs4
from langchain.docstore.document import Document
from dotenv import load_dotenv

load_dotenv()

PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_ENV = os.getenv('PINECONE_ENV')
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
DIRECTORY_PATH = os.getenv('DIRECTORY_PATH')
PINECONE_INDEX = os.getenv('PINECONE_INDEX')

pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)
index = pinecone.Index(PINECONE_INDEX)
embeddings = OpenAIEmbeddings()
vectorstore = Pinecone(index, embeddings.embed_query, "text")

prompt_template = """Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.

{context}

Question: {question}
Answer:"""
PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
)


def get_doc_metadata(filepath):
    filename = os.path.basename(filepath)

    metadata = {
        "source": filename

    }
    return metadata


def add_documents(documents, namespace):
    text_splitter = CharacterTextSplitter(separator="\n", chunk_size=1000, chunk_overlap=0)
    docs = text_splitter.split_documents(documents)
    pprint(docs)
    print(f"adding documents to vectorestore in {namespace}")
    # vectorstore.add_documents(documents=docs, namespace=namespace)

    for doc in docs:
        print(doc.metadata)
        vectorstore.add_documents(documents=[doc], namespace=namespace)
    print("documents added to vectorestore")


def add_document(document, namespace):
    vectorstore.add_documents(documents=[document], namespace=namespace)


def load_documents(upload_directory):
    print(f"Loading documets from : {upload_directory}")
    SimpleDirectoryReader = download_loader("SimpleDirectoryReader")
    loader = SimpleDirectoryReader(upload_directory, recursive=True, exclude_hidden=True,
                                   file_metadata=get_doc_metadata)
    docs = loader.load_langchain_documents()
    return docs


def load_website(url):
    print(f"Loading website data for: {url}")

    headers = {
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/34.0.1847.131 Safari/537.36"}
    reqs = requests.get(url=url, headers=headers, allow_redirects=True)
    print(reqs.status_code)

    soup = BeautifulSoup(reqs.text, 'html.parser')
    urls = []
    for link in soup.find_all('a'):
        pagelink = link.get('href')

        if pagelink.startswith('/'):
            full_link = url + pagelink
            urls.append(full_link)
        else:
            urls.append(pagelink)

    urls = [*set(urls)]
    pprint(urls)
    UnstructuredURLLoader = download_loader("UnstructuredURLLoader")
    loader = UnstructuredURLLoader(urls=urls, continue_on_failure=True, headers=headers)
    documents = loader.load()
    langchain_documents = []
    for doc in documents:
        new_doc = Document(page_content=doc.text, metadata=doc.extra_info)
        langchain_documents.append(new_doc)
    text_splitter = CharacterTextSplitter(separator="\n", chunk_size=1000, chunk_overlap=0)
    docs = text_splitter.split_documents(langchain_documents)
    return docs


def load_notion(url, token):
    print(f"Loading notion data for: {url}")
    NotionPageReader = download_loader('NotionPageReader')
    page_ids = ["5ba7041f646b454b8356cb610bfe5d48"]
    reader = NotionPageReader(integration_token=token)
    documents = reader.load_data(page_ids=page_ids)
    langchain_documents = []
    for doc in documents:
        new_doc = Document(page_content=doc.text, metadata=doc.extra_info)
        langchain_documents.append(new_doc)
    return langchain_documents


def load_youtube(url):
    print(f"Loading youtube data for: {url}")
    from langchain.document_loaders import YoutubeLoader
    loader = YoutubeLoader.from_youtube_url(url, add_video_info=True)
    documents = loader.load()
    langchain_documents = []
    for doc in documents:
        new_doc = Document(page_content=doc.page_content,
                           metadata={'source': url})
        langchain_documents.append(new_doc)
    return langchain_documents


class KnowledgeBaseQA:
    def __init__(self, namespace):
        self.data = []
        self.namespace = namespace
        self.docsearch = Pinecone.from_existing_index(PINECONE_INDEX, embeddings, namespace=self.namespace)
        self.qa = RetrievalQA.from_chain_type(llm=OpenAI(), chain_type="stuff",
                                              retriever=self.docsearch.as_retriever(search_kwargs={"k": 3}),
                                              chain_type_kwargs={"prompt": PROMPT},
                                              return_source_documents=True)

    def query(self, query_string):
        result = self.qa({"query": query_string})
        return result
