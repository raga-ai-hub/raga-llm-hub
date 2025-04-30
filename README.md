🤝 Contributing + 🎉 Usage

def load_huggingface_model(model_name):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)
    return tokenizer, model

💡 Example + 🔍 Functions
import os
from dotenv import load_dotenv
import chromadb
from openai import OpenAI
from chromadb.utils import embedding_functions

# Load environment variables from .env file
load_dotenv()

openai_key = os.getenv("OPENAI_API_KEY")

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=openai_key, model_name="text-embedding-3-small"
)
# Initialize the Chroma client with persistence
chroma_client = chromadb.PersistentClient(path="chroma_persistent_storage")
collection_name = "document_qa_collection"
collection = chroma_client.get_or_create_collection(
    name=collection_name, embedding_function=openai_ef
)


client = OpenAI(api_key=openai_key)

# resp = client.chat.completions.create(
#     model="gpt-3.5-turbo",
#     messages=[
#         {"role": "system", "content": "You are a helpful assistant."},
#         {
#             "role": "user",
#             "content": "What is human life expectancy in the United States?",
#         },
#     ],
# )


# Function to load documents from a directory
def load_documents_from_directory(directory_path):
    print("==== Loading documents from directory ====")
    documents = []
    for filename in os.listdir(directory_path):
        if filename.endswith(".txt"):
            with open(
                os.path.join(directory_path, filename), "r", encoding="utf-8"
            ) as file:
                documents.append({"id": filename, "text": file.read()})
    return documents


# Function to split text into chunks
def split_text(text, chunk_size=1000, chunk_overlap=20):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - chunk_overlap
    return chunks


# Load documents from the directory
directory_path = "./news_articles"
documents = load_documents_from_directory(directory_path)

print(f"Loaded {len(documents)} documents")
# Split documents into chunks
chunked_documents = []
for doc in documents:
    chunks = split_text(doc["text"])
    print("==== Splitting docs into chunks ====")
    for i, chunk in enumerate(chunks):
        chunked_documents.append({"id": f"{doc['id']}_chunk{i+1}", "text": chunk})

# print(f"Split documents into {len(chunked_documents)} chunks")


# Function to generate embeddings using OpenAI API
def get_openai_embedding(text):
    response = client.embeddings.create(input=text, model="text-embedding-3-small")
    embedding = response.data[0].embedding
    print("==== Generating embeddings... ====")
    return embedding


# Generate embeddings for the document chunks
for doc in chunked_documents:
    print("==== Generating embeddings... ====")
    doc["embedding"] = get_openai_embedding(doc["text"])

# print(doc["embedding"])

# Upsert documents with embeddings into Chroma
for doc in chunked_documents:
    print("==== Inserting chunks into db;;; ====")
    collection.upsert(
        ids=[doc["id"]], documents=[doc["text"]], embeddings=[doc["embedding"]]
    )


# Function to query documents
def query_documents(question, n_results=2):
    # query_embedding = get_openai_embedding(question)
    results = collection.query(query_texts=question, n_results=n_results)

    # Extract the relevant chunks
    relevant_chunks = [doc for sublist in results["documents"] for doc in sublist]
    print("==== Returning relevant chunks ====")
    return relevant_chunks
    # for idx, document in enumerate(results["documents"][0]):
    #     doc_id = results["ids"][0][idx]
    #     distance = results["distances"][0][idx]
    #     print(f"Found document chunk: {document} (ID: {doc_id}, Distance: {distance})")


# Function to generate a response from OpenAI
def generate_response(question, relevant_chunks):
    context = "\n\n".join(relevant_chunks)
    prompt = (
        "You are an assistant for question-answering tasks. Use the following pieces of "
        "retrieved context to answer the question. If you don't know the answer, say that you "
        "don't know. Use three sentences maximum and keep the answer concise."
        "\n\nContext:\n" + context + "\n\nQuestion:\n" + question
    )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": prompt,
            },
            {
                "role": "user",
                "content": question,
            },
        ],
    )

    answer = response.choices[0].message
    return answer


# Example query
# query_documents("tell me about AI replacing TV writers strike.")
# Example query and response generation
question = "tell me about databricks"
relevant_chunks = query_documents(question)
answer = generate_response(question, relevant_chunks)

print(answer)




# 🌟 Document QA System 🌟

Welcome to the **Document Question-Answering (QA) System**! This innovative project harnesses the power of OpenAI's API and ChromaDB to create a seamless experience for retrieving information from text documents. Whether you're a researcher, student, or just curious, this system is designed to help you find answers quickly and efficiently!

## 🚀 Features
- Effortless Document Loading: Simply drop your text files into the designated folder, and let the system do the rest!
- smart Chunking: Documents are intelligently split into manageable chunks, ensuring that no detail is overlooked.
- Powerful Embeddings: Leverage OpenAI's cutting-edge technology to generate meaningful embeddings for each document chunk.
- Fast Retrieval: Store and retrieve document chunks with lightning speed using ChromaDB.
- Interactive Querying: Ask questions and receive concise, relevant answers based on the content of your documents.

## 🛠️ Requirements
To get started, you'll need:
- Python 3.7 or higher
- Essential libraries:
  - `os`
  - `dotenv`
  - `chromadb`
  - `openai`
  - `transformers` (for Hugging Face models)
  - `datasets` (for Hugging Face datasets)

## 📥 Installation
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/document-qa-system.git
   cd document-qa-system
   ```

2. **Install Required Packages**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Environment Variables**:
   - Create a `.env` file in the root directory and add your OpenAI API key:
     ```
     OPENAI_API_KEY=your_openai_api_key
     ```

## 🎉 Usage
1. **Load Your Documents**: Place your text documents in the `./news_articles` directory.
2. **Run the Application**:
   ```bash
   python app.py
   ```

3. **Ask Your Questions**: Modify the `question` variable in `app.py` to ask anything you want:
   ```python
   question = "Your question here"
   ```

4. **Get Answers**: Sit back and watch as the system provides you with insightful responses!

## 🔍 Functions
- **`load_documents_from_directory(directory_path)`**: Effortlessly loads text documents from your specified directory.
- **`split_text(text, chunk_size=1000, chunk_overlap=20)`**: Splits text into digestible chunks with a smart overlap.
- **`get_openai_embedding(text)`**: Generates powerful embeddings for your text using OpenAI's API.
- **`query_documents(question, n_results=2)`**: Retrieves relevant document chunks based on your query.
- **`generate_response(question, relevant_chunks)`**: Crafts a concise answer using the retrieved chunks.

## 💡 Example
To see the magic in action, set the `question` variable in `app.py`:
```python
question = "Tell me about Databricks"
```
Run the application, and prepare to be amazed by the response!

## 🤝 Contributing
We welcome contributions from everyone! If you have ideas for improvements or new features, please open an issue or submit a pull request. Let's make this project even better together!

## 📜 License
This project is licensed under the MIT License. Check out the MIT file for more details.

## 🙏 Acknowledgments
- A huge thank you to **OpenAI** for providing the API that powers our embeddings and chat capabilities.
- Special thanks to **ChromaDB** for enabling efficient document storage and retrieval.


Feel free to customize this README further to match your project's personality and style! Happy coding! 🎉

    
