# Location: flashscore.py

import argparse
import concurrent.futures
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from tqdm import tqdm

from browsers.browser_factory import BrowserFactory, BrowserType
from browsers.edge_browser import EdgeOptionArguments
from logging_config import get_logger
from models.config import Config
from models.fixture_match import FixtureMatch
from services.data_extraction_coordinator import DataExtractionCoordinator
from services.factories.fixtures_url_factory import FixturesURLFactory
from services.json_serialization_service import JsonSerializationService

logger = get_logger(__name__)


def get_leagues_mapping() -> Optional[Dict[str, Dict[str, str]]]:
    """Load and return the league URL mapping from JSON file."""
    mapping_filepath = os.path.join(
        os.path.dirname(__file__), "mappings", "leagues_url_mapping.json"
    )
    try:
        with open(mapping_filepath, "r", encoding="utf-8") as fin:
            return json.load(fin)
    except FileNotFoundError:
        logger.error(f"File not found: {mapping_filepath}")
    except json.JSONDecodeError:
        logger.error(f"Error decoding JSON file: {mapping_filepath}")
    except Exception as e:
        logger.error(f"Error loading leagues mapping: {str(e)}")
    return None


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Retrieve football data from Flashscore for specific country and league"
    )
    parser.add_argument(
        "-c",
        "--country",
        type=str,
        required=True,
        help="Country name for which to retrieve data",
    )
    parser.add_argument(
        "-l",
        "--league",
        type=str,
        required=True,
        help="League name for which to retrieve data",
    )
    parser.add_argument(
        "-r",
        "--rounds",
        type=int,
        default=1,
        help="Number of rounds for which to retrieve data (default: 1)",
    )
    parser.add_argument(
        "-w",
        "--workers",
        type=int,
        default=4,
        help="Number of worker processes (default: 4)",
    )
    return parser.parse_args()


def validate_arguments(
    args: argparse.Namespace, leagues_mapping: Dict
) -> Optional[Config]:
    """Validate command line arguments against available leagues mapping."""
    if not leagues_mapping:
        logger.error("Could not load leagues mapping data")
        return None

    if args.country not in leagues_mapping:
        logger.error(f"Country '{args.country}' not found in available countries")
        logger.info("Available countries: " + ", ".join(sorted(leagues_mapping.keys())))
        return None

    country_leagues = leagues_mapping[args.country]
    if args.league not in country_leagues:
        logger.error(f"League '{args.league}' not found for country '{args.country}'")
        logger.info(
            f"Available leagues for {args.country}: "
            + ", ".join(sorted(country_leagues.keys()))
        )
        return None

    if args.rounds < 1:
        logger.error("Number of rounds must be greater than 0")
        return None

    if args.workers < 1:
        logger.error("Number of workers must be greater than 0")
        return None

    return Config(country=args.country, league=args.league, rounds=args.rounds)


def process_fixture_worker(fixture_url: str, config: Config) -> Optional[FixtureMatch]:
    """Worker function to process a single fixture URL."""
    logger = get_logger(__name__)
    browser = None
    try:
        # Create a new browser instance for this process
        browser = BrowserFactory().create_browser(
            browser_type=BrowserType.EDGE,
            options_args=[
                EdgeOptionArguments.DISABLE_LOGGING,
                EdgeOptionArguments.DISABLE_NOTIFICATIONS,
                EdgeOptionArguments.DISABLE_INFOBARS,
            ],
        )

        # Create a new coordinator for this process
        coordinator = DataExtractionCoordinator(browser, config)

        # Process the fixture with timeout handling
        fixture = coordinator.create_fixture_match(fixture_url)
        return fixture

    except Exception as e:
        logger.error(f"Error processing fixture {fixture_url}: {str(e)}")
        return None
    finally:
        # Ensure browser cleanup happens even if an error occurs
        if browser:
            try:
                browser.quit()
            except Exception as e:
                # Use debug level to avoid disrupting progress bar
                logger.debug(f"Error closing browser: {str(e)}")
                # Force close in case of failure
                try:
                    browser.driver.quit()
                except:
                    pass


def process_fixtures_parallel(
    fixture_urls: List[str], config: Config, num_workers: int
) -> Tuple[List[FixtureMatch], Dict[str, List[str]]]:
    """Process fixture URLs in parallel using multiprocessing."""
    fixtures = []
    errors = {"fixture_urls": [], "fixture_matches": []}

    # Create a ProcessPoolExecutor with the specified number of workers
    with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
        # Create futures for each fixture URL
        future_to_url = {
            executor.submit(process_fixture_worker, url, config): url
            for url in fixture_urls
        }

        # Process results as they complete with progress bar
        with tqdm(
            total=len(fixture_urls),
            desc="Processing fixtures",
            unit="fixture",
            ncols=200,
        ) as pbar:
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    fixture = future.result()
                    if fixture:
                        fixtures.append(fixture)
                    else:
                        errors["fixture_matches"].append(
                            f"Failed to extract fixture from {url}"
                        )
                except Exception as e:
                    errors["fixture_matches"].append(
                        f"Error processing {url}: {str(e)}"
                    )
                finally:
                    pbar.update(1)
                    pbar.set_postfix({"successful": len(fixtures)})

    return fixtures, errors


def main():
    """Main function to coordinate the data extraction process."""
    # Parse and validate arguments
    args = parse_arguments()
    leagues_data = get_leagues_mapping()
    config = validate_arguments(args, leagues_data)

    if config is None:
        logger.error("Invalid arguments. Exiting...")
        return

    logger.info(f"Starting extraction with config: {config}")

    try:
        # Create initial browser for getting fixture URLs
        browser = BrowserFactory().create_browser(
            browser_type=BrowserType.EDGE,
            # Uncomment to run headless
            # options_args=[EdgeOptionArguments.HEADLESS]
        )

        try:
            # Get fixture URLs
            url_factory = FixturesURLFactory(browser, config)
            fixture_urls = url_factory.get_fixtures_urls()

            if not fixture_urls:
                logger.error("No fixture URLs found")
                return

            logger.info(f"Found {len(fixture_urls)} fixtures to process")

            # Process fixtures in parallel
            fixtures, errors = process_fixtures_parallel(
                fixture_urls=fixture_urls, config=config, num_workers=args.workers
            )

            # Serialize results
            serializer = JsonSerializationService(Path("output"))
            logger.info(
                f"Successfully extracted {len(fixtures)} out of {len(fixture_urls)} fixtures"
            )
            serializer.serialize_fixtures_data(fixtures, errors)

        finally:
            browser.quit()

    except Exception as e:
        logger.error(f"Error during execution: {str(e)}")


if __name__ == "__main__":
    main()
