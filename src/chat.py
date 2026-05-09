import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_postgres import PGVector

from search import PROMPT_TEMPLATE

load_dotenv()

_REQUIRED = (
    "OPENAI_API_KEY",
    "OPENAI_EMBEDDING_MODEL",
    "OPENAI_MODEL",
    "DATABASE_URL",
    "PG_VECTOR_COLLECTION_NAME",
)

def _require_env() -> None:
    for k in _REQUIRED:
        if not os.getenv(k):
            raise RuntimeError(f"Environment variable {k} is not set")

def _context_from_results(results):
    return "\n\n".join(doc.page_content for doc, _score in results)

def main() -> None:
    _require_env()

    embeddings = OpenAIEmbeddings(model=os.getenv("OPENAI_EMBEDDING_MODEL"))
    store = PGVector(
        embeddings=embeddings,
        collection_name=os.getenv("PG_VECTOR_COLLECTION_NAME"),
        connection=os.getenv("DATABASE_URL"),
        use_jsonb=True,
    )

    query = input("Digite sua pergunta: ")
    results = store.similarity_search_with_score(query, k=10)
    contexto = _context_from_results(results)
    prompt = PROMPT_TEMPLATE.format(contexto=contexto, question=query)

    llm = ChatOpenAI(model=os.getenv("OPENAI_MODEL"))
    response = llm.invoke(prompt)
    print(response.content)


if __name__ == "__main__":
    main()
