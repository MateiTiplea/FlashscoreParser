import concurrent.futures
import logging
import multiprocessing
from logging.handlers import QueueHandler, QueueListener
from multiprocessing import Manager
from typing import Optional

from selenium.common.exceptions import SessionNotCreatedException, WebDriverException
from tqdm import tqdm

from browsers.browser_factory import BrowserFactory, BrowserType
from browsers.edge_browser import EdgeOptionArguments
from logging_config import get_logger, setup_logging
from models.played_match import PlayedMatch
from services.factories.played_match_factory import PlayedMatchFactory
from services.factories.team_factory import TeamFactory
from services.shared_team_cache import SharedTeamCache


class NonDisruptiveTqdmLoggingHandler(logging.Handler):
    def __init__(self, tqdm_instance):
        super().__init__()
        self.tqdm_instance = tqdm_instance

    def emit(self, record):
        try:
            msg = self.format(record)
            # Save current position of progress bar
            # current_pos = self.tqdm_instance.n
            # Clear the progress bar
            self.tqdm_instance.clear()
            # Write the log message
            tqdm.write(msg)
            # Redraw the progress bar with original position
            self.tqdm_instance.refresh()
        except (AttributeError, IOError, ValueError):
            self.handleError(record)


def setup_process_logging(queue: multiprocessing.Queue) -> None:
    """
    Set up logging for a child process to send logs to the main process.
    """
    root = logging.getLogger()
    root.handlers = []
    queue_handler = QueueHandler(queue)
    root.addHandler(queue_handler)
    root.setLevel(logging.DEBUG)


def process_match(args) -> Optional[PlayedMatch]:
    """
    Process a single match URL in a separate process.
    """
    match_url, log_queue, team_cache = args

    setup_process_logging(log_queue)
    logger = logging.getLogger(__name__)

    browser = None
    try:
        browser = BrowserFactory().create_browser(
            browser_type=BrowserType.EDGE,
            options_args=[
                EdgeOptionArguments.DISABLE_INFOBARS,
                EdgeOptionArguments.DISABLE_GPU,
                EdgeOptionArguments.START_MAXIMIZED,
            ],
        )
    except (WebDriverException, SessionNotCreatedException) as e:
        logger.error("Error creating browser: %s", str(e))
        return None

    if not browser:
        return None

    try:
        team_factory = TeamFactory(browser=browser, cache=team_cache)
        played_match_factory = PlayedMatchFactory(
            browser=browser, team_factory=team_factory
        )
        played_match = played_match_factory.create_played_match(match_url)
        browser.quit()
        logger.error("Successfully processed match: %s", match_url)
        return played_match
    except (WebDriverException, ValueError, TypeError) as e:
        logger.error("Error processing match %s: %s", match_url, str(e))
        if browser:
            browser.quit()
        return None


def main():
    # Set up logging with the existing configuration
    setup_logging()
    logger = get_logger(__name__)
    logger.info("Starting main function")

    # Create a manager for sharing the queue
    manager = Manager()
    log_queue = manager.Queue()

    played_match_urls = [
        "https://www.flashscore.com/match/Ofaf72wq/#/match-summary/match-summary",
        "https://www.flashscore.com/match/nR9dC9S9/#/match-summary/match-summary",
        "https://www.flashscore.com/match/Ik6f5qoA/#/match-summary/match-summary",
        "https://www.flashscore.com/match/O6Rja2XN/#/match-summary/match-summary",
    ]

    results = []
    shared_cache = SharedTeamCache()
    process_args = [(url, log_queue, shared_cache) for url in played_match_urls]

    # Create progress bar
    pbar = tqdm(
        total=len(played_match_urls),
        desc="Processing matches",
        unit="match",
        ncols=200,
    )

    # Get the root logger and its existing handlers
    root_logger = logging.getLogger()
    existing_handlers = root_logger.handlers[:]

    # Initialize our handlers list with file handlers
    handlers = []
    tqdm_handler = None

    # Process and categorize existing handlers
    for handler in existing_handlers:
        if isinstance(handler, logging.StreamHandler) and not isinstance(
            handler, logging.FileHandler
        ):
            # Found console handler, replace it with tqdm handler
            root_logger.removeHandler(handler)
            tqdm_handler = NonDisruptiveTqdmLoggingHandler(pbar)
            tqdm_handler.setLevel(handler.level)  # Preserve original level
            tqdm_handler.setFormatter(handler.formatter)  # Preserve original formatter
            root_logger.addHandler(tqdm_handler)
        else:
            # Keep all other handlers (like file handlers)
            handlers.append(handler)

    # Add tqdm handler to handlers list if it was created
    if tqdm_handler:
        handlers.append(tqdm_handler)
    queue_listener = QueueListener(log_queue, *handlers, respect_handler_level=True)
    queue_listener.start()

    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(process_match, args) for args in process_args]

        for future in concurrent.futures.as_completed(futures):
            try:
                played_match = future.result()
                if played_match:
                    results.append(played_match)
                pbar.update(1)
            except (WebDriverException, ValueError, TypeError) as e:
                logger.error("Error processing future: %s", str(e))
                pbar.update(1)

    pbar.close()
    queue_listener.stop()
    manager.shutdown()

    # Restore original handlers
    if tqdm_handler:
        root_logger.removeHandler(tqdm_handler)
        # Re-add original console handler if we found it earlier
        for handler in existing_handlers:
            if isinstance(handler, logging.StreamHandler) and not isinstance(
                handler, logging.FileHandler
            ):
                root_logger.addHandler(handler)
                break

    logger.info("Successfully processed %d matches", len(results))
    logger.info("Finished main function")


if __name__ == "__main__":
    main()
