"""
JARVIS — memory/indexer.py
File system indexer — bulk loads documents into RAG memory
"""

import os
from memory.rag import RAGMemory
from rich.console import Console

console = Console()

SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf"}


class FileIndexer:
    """Walks directories and indexes supported files into RAG memory."""

    def __init__(self, rag: RAGMemory):
        self.rag = rag

    def index_directory(self, directory: str) -> int:
        """
        Recursively index all supported files in a directory.

        Args:
            directory: Path to the directory to index.

        Returns:
            Number of files indexed.
        """
        directory = os.path.expanduser(directory)

        if not os.path.isdir(directory):
            console.print(f"[red]✗ Directory not found: {directory}[/red]")
            return 0

        indexed = 0
        for root, _, files in os.walk(directory):
            for filename in sorted(files):
                ext = os.path.splitext(filename)[1].lower()
                if ext in SUPPORTED_EXTENSIONS:
                    filepath = os.path.join(root, filename)
                    try:
                        self.rag.add_document(filepath)
                        indexed += 1
                    except Exception as e:
                        console.print(f"[red]✗ Failed to index {filename}: {e}[/red]")

        if indexed > 0:
            console.print(f"[green]✓ Indexed {indexed} files from {directory}[/green]")
        else:
            console.print(f"[dim]No supported files found in {directory}[/dim]")

        return indexed
