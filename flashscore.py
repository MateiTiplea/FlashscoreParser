import argparse
import json
import os
from typing import Optional

from browsers.base_browser import BaseBrowser
from browsers.browser_factory import BrowserFactory, BrowserType
from browsers.edge_browser import EdgeOptionArguments
from models.config import Config
from services.factories.fixtures_url_factory import FixturesURLFactory
from services.factories.match_factory import MatchFactory
from services.factories.played_match_factory import PlayedMatchFactory
from services.factories.team_factory import TeamFactory
from services.head_to_head_service import HeadToHeadService


def get_leagues_mapping() -> Optional[dict[str, dict[str, str]]]:
    mapping = None
    mapping_filepath = os.path.join(
        os.path.dirname(__file__), "mappings", "leagues_url_mapping.json"
    )
    try:
        fin = open(mapping_filepath, "r", encoding="utf-8")
        mapping = json.load(fin)
        fin.close()
    except FileNotFoundError:
        print(f"File not found: {mapping_filepath}")
    except OSError:
        print(f"Error reading file: {mapping_filepath}")
    except json.JSONDecodeError:
        print(f"Error decoding JSON file: {mapping_filepath}")
    except Exception as e:
        print(f"Other Error while getting leagues mapping: {str(e)}")
    finally:
        return mapping


def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments.

    Returns:
        argparse.Namespace: Parsed command line arguments
    """
    parser = argparse.ArgumentParser(
        description="Retrieve football data from Flashscore for specific country and league"
    )

    # Add required arguments
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

    # Add optional argument
    parser.add_argument(
        "-r",
        "--rounds",
        type=int,
        default=1,
        help="Number of rounds for which to retrieve data (default: 1)",
    )

    return parser.parse_args()


def validate_arguments(
    args: argparse.Namespace, leagues_mapping: dict
) -> Optional[Config]:
    """
    Validate command line arguments against available leagues mapping.

    Args:
        args: Parsed command line arguments
        leagues_mapping: Dictionary containing country->league->url mapping

    Returns:
        Config object if validation successful, None otherwise
    """
    if leagues_mapping is None:
        print("Error: Could not load leagues mapping data")
        return None

    # Check if country exists
    if args.country not in leagues_mapping:
        print(f"Error: Country '{args.country}' not found in available countries")
        print("Available countries:", ", ".join(sorted(leagues_mapping.keys())))
        return None

    # Check if league exists for the country
    country_leagues = leagues_mapping[args.country]
    if args.league not in country_leagues:
        print(f"Error: League '{args.league}' not found for country '{args.country}'")
        print(
            f"Available leagues for {args.country}:",
            ", ".join(sorted(country_leagues.keys())),
        )
        return None

    # Validate rounds
    if args.rounds < 1:
        print("Error: Number of rounds must be greater than 0")
        return None

    # Create and return config object
    return Config(
        country=args.country,
        league=args.league,
        rounds=args.rounds,
    )


def main():
    args = parse_arguments()
    leagues_data = get_leagues_mapping()

    config = validate_arguments(args, leagues_data)
    print(f"Config: {config}")

    if config is None:
        print("Invalid arguments. Exiting...")
        return

    browser = BrowserFactory().create_browser(
        browser_type=BrowserType.EDGE,
        # options_args= [EdgeOptionArguments.HEADLESS]
    )

    # matches_url = FixturesURLFactory(browser, config).get_fixtures_urls()
    # print("Found a number of matches: ", len(matches_url))

    team_factory = TeamFactory(browser)
    match_instance = MatchFactory(browser, team_factory).create_match(
        "https://www.flashscore.com/match/82qTWLi3/#/h2h/overall"
    )
    played_match_factory = PlayedMatchFactory(browser, team_factory)
    h2h_service = HeadToHeadService(browser, played_match_factory)

    h2h = h2h_service.get_head_to_head(
        "https://www.flashscore.com/match/82qTWLi3/#/h2h/overall",
        match_instance.home_team,
        match_instance.away_team,
    )

    print(h2h.get_team_record(match_instance.home_team))
    print(h2h.get_team_record(match_instance.away_team))

    browser.quit()


if __name__ == "__main__":
    main()
