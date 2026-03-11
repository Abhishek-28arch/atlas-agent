"""
JARVIS Built-in Skill — Web Search
Search the web using DuckDuckGo (no API key needed)
"""

SKILL_NAME = "web_search"
SKILL_DESCRIPTION = "Search the web using DuckDuckGo — no API key required"
SKILL_TRIGGERS = ["search", "google", "look up", "find online", "web search", "what is", "who is"]


def run(user_input: str, context: dict) -> str:
    """Execute a web search."""
    # Clean up the query
    query = user_input
    for prefix in ["search for", "search", "google", "look up", "find online", "web search"]:
        if query.lower().startswith(prefix):
            query = query[len(prefix):].strip()
            break

    if not query:
        return "🔍 What would you like me to search for?"

    try:
        from duckduckgo_search import DDGS

        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))

        if not results:
            return f"🔍 No results found for: {query}"

        response = f"🔍 Search results for: **{query}**\n\n"
        for i, r in enumerate(results, 1):
            title = r.get("title", "No title")
            body = r.get("body", "")[:150]
            href = r.get("href", "")
            response += f"{i}. **{title}**\n   {body}\n   {href}\n\n"

        return response

    except ImportError:
        return "❌ duckduckgo-search not installed. Run: pip install duckduckgo-search"
    except Exception as e:
        return f"❌ Search failed: {e}"
