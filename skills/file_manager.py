"""
JARVIS Built-in Skill — File Manager
Organize, list, and manage files in directories
"""

import os
import shutil
from collections import defaultdict

SKILL_NAME = "file_manager"
SKILL_DESCRIPTION = "Organize, list, move, and manage files in directories"
SKILL_TRIGGERS = ["organize", "files", "downloads", "sort files", "clean up", "file manager"]


# File type categories
FILE_CATEGORIES = {
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".md", ".odt", ".rtf", ".tex", ".csv", ".xlsx", ".xls", ".pptx"},
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico", ".tiff"},
    "Videos": {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm"},
    "Audio": {".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma"},
    "Archives": {".zip", ".tar", ".gz", ".bz2", ".7z", ".rar", ".xz"},
    "Code": {".py", ".js", ".ts", ".html", ".css", ".java", ".cpp", ".c", ".go", ".rs", ".sh", ".json", ".yaml", ".yml"},
    "Installers": {".deb", ".rpm", ".AppImage", ".snap", ".flatpak", ".exe", ".msi"},
}


def run(user_input: str, context: dict) -> str:
    """Execute the file manager skill."""
    input_lower = user_input.lower()

    if "organize" in input_lower or "sort" in input_lower or "clean" in input_lower:
        # Determine target directory
        target = _extract_path(user_input)
        return organize_directory(target)

    elif "list" in input_lower or "show" in input_lower:
        target = _extract_path(user_input)
        return list_directory(target)

    else:
        return (
            "📁 File Manager commands:\n"
            "• 'Organize my Downloads' — sort files by type\n"
            "• 'List files in ~/Documents' — show directory contents\n"
            "• 'Clean up Desktop' — organize Desktop folder"
        )


def organize_directory(directory: str) -> str:
    """Sort files into categorized subfolders."""
    directory = os.path.expanduser(directory)

    if not os.path.isdir(directory):
        return f"❌ Directory not found: {directory}"

    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

    if not files:
        return f"📁 No files to organize in {directory}"

    moved = defaultdict(list)

    for filename in files:
        ext = os.path.splitext(filename)[1].lower()
        category = _get_category(ext)

        if category:
            dest_dir = os.path.join(directory, category)
            os.makedirs(dest_dir, exist_ok=True)

            src = os.path.join(directory, filename)
            dst = os.path.join(dest_dir, filename)

            # Don't overwrite existing files
            if not os.path.exists(dst):
                shutil.move(src, dst)
                moved[category].append(filename)

    if not moved:
        return "📁 All files are already organized."

    summary = f"✅ Organized {sum(len(v) for v in moved.values())} files:\n"
    for category, files in sorted(moved.items()):
        summary += f"  → {category}/: {len(files)} files\n"

    return summary


def list_directory(directory: str) -> str:
    """List contents of a directory with details."""
    directory = os.path.expanduser(directory)

    if not os.path.isdir(directory):
        return f"❌ Directory not found: {directory}"

    entries = os.listdir(directory)
    if not entries:
        return f"📁 {directory} is empty."

    dirs = []
    files = []

    for entry in sorted(entries):
        full_path = os.path.join(directory, entry)
        if os.path.isdir(full_path):
            count = len(os.listdir(full_path))
            dirs.append(f"  📁 {entry}/ ({count} items)")
        else:
            size = os.path.getsize(full_path)
            files.append(f"  📄 {entry} ({_format_size(size)})")

    result = f"📁 {directory} — {len(dirs)} folders, {len(files)} files\n"
    result += "\n".join(dirs[:20])
    if dirs:
        result += "\n"
    result += "\n".join(files[:30])

    if len(dirs) > 20 or len(files) > 30:
        result += f"\n  ... and {len(dirs) + len(files) - 50} more"

    return result


def _get_category(ext: str) -> str | None:
    """Get the category for a file extension."""
    for category, extensions in FILE_CATEGORIES.items():
        if ext in extensions:
            return category
    return None


def _extract_path(user_input: str) -> str:
    """Try to extract a directory path from user input."""
    # Look for common directory references
    input_lower = user_input.lower()

    if "download" in input_lower:
        return "~/Downloads"
    elif "desktop" in input_lower:
        return "~/Desktop"
    elif "document" in input_lower:
        return "~/Documents"
    elif "~/" in user_input or "/" in user_input:
        # Try to find a path in the input
        for word in user_input.split():
            if "/" in word:
                return word
    return "~/Downloads"  # default


def _format_size(size_bytes: int) -> str:
    """Format file size in human-readable form."""
    for unit in ("B", "KB", "MB", "GB"):
        if size_bytes < 1024:
            return f"{size_bytes:.1f}{unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f}TB"
