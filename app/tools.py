from typing import List


def split_text_tool(text: str, chunk_size: int = 200) -> List[str]:
    """
    Splits a long text into chunks of fixed size (by word count).
    Example: if chunk_size=200, every chunk has up to 200 words.
    """
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunks.append(" ".join(words[i:i + chunk_size]))
    return chunks


def summarize_chunk_tool(chunk: str, max_words: int = 50) -> str:
    """
    Naive summary: take the first N words of each chunk.
    Works reliably for rule-based summarization.
    """
    words = chunk.split()
    return " ".join(words[:max_words])


def merge_summaries_tool(summaries: List[str]) -> str:
    """
    Combine all chunk summaries into one giant summary.
    """
    return " ".join(summaries)


def refine_summary_tool(summary: str, max_words: int) -> str:
    """
    Refines the summary by trimming it to max_words.
    Later, you can add smarter rules if desired.
    """
    words = summary.split()
    if len(words) <= max_words:
        return summary
    return " ".join(words[:max_words])


TOOL_REGISTRY = {
    "split_text": split_text_tool,
    "summarize_chunk": summarize_chunk_tool,
    "merge_summaries": merge_summaries_tool,
    "refine_summary": refine_summary_tool,
}
