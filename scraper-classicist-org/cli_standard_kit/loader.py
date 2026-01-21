"""CLI loader utility for convenient CLI instantiation."""

from typing import Optional

from .cli_core import StandardCLI


def get_cli(
    prog: str,
    description: Optional[str] = None,
    epilog: Optional[str] = None,
) -> StandardCLI:
    """Create and return a StandardCLI instance.
    
    Convenience function for creating a CLI instance with common defaults.
    
    Args:
        prog: Program name
        description: Program description
        epilog: Text shown after help
        
    Returns:
        StandardCLI instance ready for command registration
        
    Example:
        cli = get_cli("mytool", "My awesome tool")
        cli.register(MyCommand())
        cli.run()
    """
    return StandardCLI(
        prog=prog,
        description=description,
        epilog=epilog,
    )

