"""Terminal color codes for consistent output formatting."""

class Colors:
    """ANSI terminal color codes and formatting."""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

class MessageFormatter:
    """Pre-formatted message templates for consistent output."""
    
    @staticmethod
    def success(message: str) -> str:
        return f"{Colors.GREEN}{Colors.BOLD}[SUCCESS]{Colors.END} {message}"
    
    @staticmethod
    def error(message: str) -> str:
        return f"{Colors.RED}{Colors.BOLD}[ERROR]{Colors.END} {message}"
    
    @staticmethod
    def warning(message: str) -> str:
        return f"{Colors.YELLOW}{Colors.BOLD}[WARNING]{Colors.END} {message}"
    
    @staticmethod
    def info(message: str) -> str:
        return f"{Colors.BLUE}{Colors.BOLD}[INFO]{Colors.END} {message}"
    
    @staticmethod
    def process(message: str) -> str:
        return f"{Colors.BLUE}{Colors.BOLD}[PROCESS]{Colors.END} {message}"
    
    @staticmethod
    def debug(message: str) -> str:
        return f"{Colors.CYAN}{Colors.BOLD}[DEBUG]{Colors.END} {message}"
    
    @staticmethod
    def dry_run(message: str) -> str:
        return f"{Colors.CYAN}{Colors.BOLD}[DRY-RUN]{Colors.END} {message}"
