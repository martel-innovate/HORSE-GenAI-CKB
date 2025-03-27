import re
from scrape_attacks import search_for_attacks
from mitigation_generator import generate_mitigations

def main():
    # Your main logic here
    capec_attacks_url = "https://capec.mitre.org/data/definitions/3000.html"
    attacks_mitigations = search_for_attacks(capec_attacks_url, n_attacks_to_search=82, only_new_attacks=True)

    # enhance the database with generative AI
    generate_mitigations(attacks_mitigations)

if __name__ == "__main__":
    main()