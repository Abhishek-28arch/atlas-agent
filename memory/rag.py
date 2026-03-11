"""
JARVIS — memory/rag.py
RAG memory — ChromaDB + LangChain for document storage and retrieval
"""

import os
import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from rich.console import Console

console = Console()


class RAGMemory:
    """Vector-based document memory using ChromaDB."""

    def __init__(self, db_path: str = "./data/rag_db", collection_name: str = "jarvis_memory",
                 chunk_size: int = 500, chunk_overlap: int = 50):
        """
        Initialize the RAG memory system.

        Args:
            db_path: Path to persist the ChromaDB database.
            collection_name: Name of the ChromaDB collection.
            chunk_size: Characters per text chunk.
            chunk_overlap: Overlap between consecutive chunks.
        """
        self.db_path = db_path
        os.makedirs(db_path, exist_ok=True)

        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

        console.print(
            f"[dim]RAG: Loaded collection '{collection_name}' "
            f"({self.collection.count()} documents)[/dim]"
        )

    def add_text(self, text: str, source: str = "unknown"):
        """
        Add raw text to the vector store.

        Args:
            text: The text content to store.
            source: Label for where the text came from.
        """
        chunks = self.splitter.split_text(text)

        if not chunks:
            console.print("[yellow]⚠ No text to add (empty content)[/yellow]")
            return

        ids = [f"{source}_{i}" for i in range(len(chunks))]
        metadatas = [{"source": source, "chunk": i} for i in range(len(chunks))]

        # Upsert to handle re-indexing the same source
        self.collection.upsert(
            ids=ids,
            documents=chunks,
            metadatas=metadatas,
        )

        console.print(
            f"[green]✓ Added {len(chunks)} chunks from '{source}'[/green]"
        )

    def add_document(self, file_path: str):
        """
        Load and add a document file to the vector store.

        Supports: .txt, .md, .pdf

        Args:
            file_path: Path to the document file.
        """
        file_path = os.path.expanduser(file_path)

        if not os.path.exists(file_path):
            console.print(f"[red]✗ File not found: {file_path}[/red]")
            return

        ext = os.path.splitext(file_path)[1].lower()
        filename = os.path.basename(file_path)

        try:
            if ext in (".txt", ".md"):
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()
            elif ext == ".pdf":
                text = self._load_pdf(file_path)
            else:
                console.print(f"[yellow]⚠ Unsupported file type: {ext}[/yellow]")
                return

            self.add_text(text, source=filename)

        except Exception as e:
            console.print(f"[red]✗ Error loading {filename}: {e}[/red]")

    def _load_pdf(self, file_path: str) -> str:
        """Extract text from a PDF file."""
        try:
            from pypdf import PdfReader
            reader = PdfReader(file_path)
            pages = [page.extract_text() or "" for page in reader.pages]
            return "\n\n".join(pages)
        except ImportError:
            console.print("[yellow]⚠ pypdf not installed. Run: pip install pypdf[/yellow]")
            return ""

    def query(self, question: str, top_k: int = 3) -> list[dict]:
        """
        Search for relevant document chunks.

        Args:
            question: The search query.
            top_k: Number of results to return.

        Returns:
            List of dicts with 'text', 'source', and 'distance' keys.
        """
        if self.collection.count() == 0:
            return []

        results = self.collection.query(
            query_texts=[question],
            n_results=min(top_k, self.collection.count()),
        )

        documents = []
        for i, doc in enumerate(results["documents"][0]):
            documents.append({
                "text": doc,
                "source": results["metadatas"][0][i].get("source", "unknown"),
                "distance": results["distances"][0][i] if results.get("distances") else None,
            })

        return documents

    def get_context(self, question: str, top_k: int = 3) -> str:
        """
        Get formatted context string for RAG augmentation.

        Args:
            question: The query to search for.
            top_k: Number of chunks to include.

        Returns:
            Formatted context string ready to inject into a prompt.
        """
        results = self.query(question, top_k)

        if not results:
            return ""

        context_parts = []
        for r in results:
            context_parts.append(f"[Source: {r['source']}]\n{r['text']}")

        return "\n\n---\n\n".join(context_parts)

    def count(self) -> int:
        """Return the number of documents in the store."""
        return self.collection.count()

    def clear(self):
        """Delete all documents from the collection."""
        self.client.delete_collection(self.collection.name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection.name,
            metadata={"hnsw:space": "cosine"},
        )
        console.print("[yellow]⚠ RAG memory cleared[/yellow]")
