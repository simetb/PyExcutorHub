"""Log formatting utilities"""


def format_logs(log_content: str) -> str:
    """Format log content to display properly with line breaks"""
    if not log_content:
        return ""
    
    # Replace literal \n with actual line breaks
    # Also handle other common escape sequences
    formatted = log_content.replace('\\n', '\n')
    formatted = formatted.replace('\\t', '\t')
    formatted = formatted.replace('\\r', '\r')
    
    # Remove any trailing whitespace and normalize line endings
    formatted = formatted.rstrip()
    
    return formatted

