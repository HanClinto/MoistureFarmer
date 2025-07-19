import os
import sys

# Color codes that work cross-platform
class Colors:
    """Cross-platform color codes."""
    def __init__(self):
        self._init_colors()
        # Check if we should use colors
        self.use_colors = self._should_use_colors()
        
        if self.use_colors:
            self.BOLD = '\033[1m'
            self.RESET = '\033[0m'
            self.ITALIC = '\033[3m'
            self.PURPLE = '\033[1;35m'
            self.YELLOW = '\033[1;33m'
            self.GREEN = '\033[1;32m'
            self.RED = '\033[1;31m'
            self.BLUE = '\033[1;34m'
            self.CYAN = '\033[1;36m'
        else:
            # No colors - just use empty strings
            self.BOLD = ''
            self.RESET = ''
            self.ITALIC = ''
            self.PURPLE = ''
            self.YELLOW = ''
            self.GREEN = ''
            self.RED = ''
            self.BLUE = ''
            self.CYAN = ''
    
    def _init_colors(self):
        """Initialize ANSI color support for cross-platform compatibility."""
        if os.name == 'nt':  # Windows
            try:
                # Enable ANSI escape sequences in Windows Console
                import subprocess
                subprocess.run('', shell=True, check=True)
                # For older Windows versions, try colorama
                try:
                    import colorama
                    colorama.init()
                except ImportError:
                    # If colorama is not available, try enabling ANSI support directly
                    import ctypes
                    kernel32 = ctypes.windll.kernel32
                    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            except:
                pass

    def _should_use_colors(self):
        """Determine if we should use colors based on environment."""
        # Don't use colors if output is redirected
        if not sys.stdout.isatty():
            return False
            
        # Check environment variables
        if os.environ.get('NO_COLOR'):
            return False
            
        if os.environ.get('FORCE_COLOR'):
            return True
            
        # Check for common terminals that support colors
        term = os.environ.get('TERM', '').lower()
        if any(term_type in term for term_type in ['color', 'ansi', 'xterm', 'screen', 'tmux']):
            return True
            
        # On Windows, check if we're in a modern terminal
        if os.name == 'nt':
            # Check for Windows Terminal, VS Code terminal, or other modern terminals
            wt_session = os.environ.get('WT_SESSION')
            term_program = os.environ.get('TERM_PROGRAM', '').lower()
            if wt_session or 'vscode' in term_program:
                return True
                
        return True  # Default to using colors
