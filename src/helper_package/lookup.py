import json
import sys
from decimal import Decimal


def lookup_helper(alias, alias_set, lookup_file, dir_path):
    """
    Helper, where actual look up occurs.

    :param alias: Alias of party we are looking up.
    :param alias_set: Alias set in which party resides.
    :param lookup_file: File name of json (look up db).
    :param dir_path: Path to party file.
    :return: Party information
    """
    with open(dir_path) as file:
        file_content = json.load(file, parse_float=Decimal)

        if lookup_file == "Instrument.json":
            return file_content
        elif lookup_file == "PersonParty.json":
            person = list(
                filter(lambda payee: payee["FullName"] == alias, file_content[alias_set])
            )[0]
            # list(filter) returns list of one entry for person
            # with name 'alias', so we return elt @ index 0
            return person

        # here, we are either in Account, BankParty, or OrganizationParty lookup
        return file_content[alias_set][alias]

def lookup(alias, alias_set, lookup_file):
    """
    Performs a party look up by alias in alias_set.
    First checks where this function is being called in src, 
    sets up path to parties directory, then calls lookup_helper. 

    :param alias: Alias of party we are looking up.
    :param alias_set: Alias set in which party resides.
    :param lookup_file: File name of json (look up db)
    :return: Party information
    """
    if sys.executable == "/var/lang/bin/python3.8":  # if we are in aws
        dir_path = f"helper_package/parties/{lookup_file}"
    else:
        dir_path = f"../helper_package/parties/{lookup_file}"
    
    # handle if we are testing consumer or source adapters
    try:
        return lookup_helper(alias=alias, alias_set=alias_set, 
                               lookup_file=lookup_file, dir_path=dir_path)
    except FileNotFoundError:
        dir_path = f"../../helper_package/parties/{lookup_file}"
        return lookup_helper(alias=alias, alias_set=alias_set, 
                               lookup_file=lookup_file, dir_path=dir_path)

    
