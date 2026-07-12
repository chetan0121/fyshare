"""
FyShare : Secure one-time file sharing server
"""
from pathlib import Path
import sys
from core import server, credentials
from core import load_config, backup_config
from core.state import FileState, ServerState, StateError
from core.utils import logger, helper, runtime_info

def get_app_root() -> Path:
    """Get the root directory of the application
    
    Returns the executable directory if frozen, otherwise the script directory
    """
    if runtime_info.ran_as_compiled_bin():
        return Path(sys.executable).parent
    else:
        return Path(__file__).resolve().parent

def main() -> None:
    # True if run is from github CI
    FileState.ci_mod = runtime_info.testing_in_ci()

    # Get current folder path
    FileState.base_dir = get_app_root()
    this_dir = str(FileState.base_dir)

    # Setup logger
    logger.set_logger(f"{this_dir}/logs/server.log")

    # Load configuration
    FileState.config_path = helper.refine_path(f"{this_dir}/config.json", False)
    FileState.CONFIG = load_config(FileState.config_path)

    # Request for backup if config is invalid or not found
    if not FileState.CONFIG:
        if not backup_config("config_example.json"):
            return
        FileState.CONFIG = load_config(FileState.config_path)
    
    # Setup root, templates and static
    try:
        FileState.set_root_path()
        FileState.set_templates(f"{this_dir}/templates")
        FileState.setup_static_dir(f"{this_dir}/static")
    except (StateError, helper.UtilityError) as e:
        logger.print_error(f"Directory setup failed: {e}", prefix="\n\n", end="\n")
        return
    except KeyboardInterrupt:
        logger.print_info("Operation cancelled by user", prefix="\n\n", end="\n")
        return

    # Initialize core components for server
    try:
        ServerState.init_server_state()
        server.init_server()
    except (ValueError, RuntimeError) as e:
        logger.emit_error(str(e))  
        return  

    # First-time startup banner
    logger.log_info(
        f"Server started → {ServerState.server_url}",
        f"Root Dir: '{FileState.ROOT_DIR}'",
        prefix=f"{'='*100}\n"
    )

    # Generate and print credentials
    credentials.generate_credentials("New server started")

    # Start the server loop
    try:
        server.run_server()
    except KeyboardInterrupt:
        server.shutdown_server("Server stopped manually")
    except Exception as e:
        logger.emit_error(f"Server error: {e}")
        server.shutdown_server(f"Server terminated due to error")


# Entry point
if __name__ == "__main__":
    main()
    
    # If compiled and not run from a terminal keep window open
    if runtime_info.ran_as_compiled_bin() and runtime_info.is_interactive_terminal():
        input("\nPress Enter to exit...")
