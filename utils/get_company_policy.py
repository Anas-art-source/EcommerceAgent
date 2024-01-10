from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings.openai import OpenAIEmbeddings


def get_company_policy(query_string: str):
    """"
    Use this tool to answer user question related to company policy, such as refund policy and company details
    """
    faiss_index = FAISS.load_local(folder_path='/home/khudi/Desktop/EcommerceAgentProject/faiss_index', embeddings=OpenAIEmbeddings())
    docs = faiss_index.similarity_search(query_string, k=1)
    output = ""
    for doc in docs:
        output += " ".join(doc.page_content.split('\n'))
    return output

    # for doc in docs:
    #     print(str(doc.metadata["page"]) + ":", doc.page_content[:300])
        
