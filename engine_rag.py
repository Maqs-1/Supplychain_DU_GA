import os
import shutil
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv

load_dotenv()

# L'initialisation est désormais sécurisée dans une fonction
def get_embeddings():
    return GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

def build_vectorstore():
    print("--- DÉMARRAGE DE L'INGESTION ---")

    print("1. Lecture des documents dans le dossier 'data'...")
    loader = PyPDFDirectoryLoader("./data")
    docs = loader.load()

    if not docs:
        print("ERREUR : Aucun document trouvé dans le dossier './data'.")
        return None

    print(f"2. Découpage en cours ({len(docs)} pages détectées)...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    splits = text_splitter.split_documents(docs)

    print(f"3. Génération des embeddings pour {len(splits)} morceaux...")

    if os.path.exists("./vectorstore"):
        shutil.rmtree("./vectorstore")
        print("   -> Nettoyage de la base précédente.")

    batch_size = 100
    vectorstore = None
    embeddings_model = get_embeddings()

    for i in range(0, len(splits), batch_size):
        batch = splits[i: i + batch_size]
        print(f"   -> Traitement du lot : {min(i + batch_size, len(splits))}/{len(splits)}...")

        if vectorstore is None:
            vectorstore = Chroma.from_documents(
                documents=batch,
                embedding=embeddings_model,
                persist_directory="./vectorstore"
            )
        else:
            vectorstore.add_documents(batch)

    print("\nSUCCÈS : Base de données vectorielle prête.")
    return vectorstore

def query_documents(question: str) -> str:
    if not os.path.exists("./vectorstore"):
        return "Erreur : La base de données documentaire n'a pas encore été créée. Lance d'abord engine_rag.py."

    embeddings_model = get_embeddings()
    vectorstore = Chroma(persist_directory="./vectorstore", embedding_function=embeddings_model)

    docs = vectorstore.similarity_search(question, k=5)

    formatted_results = []
    for doc in docs:
        source_path = doc.metadata.get("source", "Document inconnu")
        filename = os.path.basename(source_path)
        formatted_results.append(f"SOURCE : {filename}\nCONTENU : {doc.page_content}")

    return "\n\n---\n\n".join(formatted_results)

if __name__ == "__main__":
    build_vectorstore()