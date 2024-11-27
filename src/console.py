from rich.console import Console
from rich.theme import Theme
import logging
from rich.logging import RichHandler

# Define log colors and theme
log_colors = Theme({
    'logging.level.debug': 'bold blue',
    'logging.level.info': 'green',
    'logging.level.warning': 'bold yellow',
    'logging.level.error': 'red',
    'logging.level.critical': 'bold red',
})

# Initialize the console with the logging theme
console = Console(theme=log_colors)

# Set up logging with RichHandler
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, show_time=False, markup=True, console=console)]  
)

# Get a logger instance
log = logging.getLogger(__name__)

def set_log_level(debug=False):
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)
