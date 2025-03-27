from urllib.request import urlopen
import re

def scrape_from_attack_page(url):
    page = urlopen(url)
    html_bytes = page.read()
    html = html_bytes.decode("utf-8")
    string = html

    mitigation_list = []

    # search if Mitigations are defined in this attack page
    pattern = re.compile(r'</span>Mitigations</div>(.*?)</table></div>', re.DOTALL)
    match = pattern.search(string)

    if match:
        mitigation_table = match.group(1).strip()

        # in the mitigation table, find all the mitigations and put them in a list as separate elements
        pattern = re.compile(r'<tr><td valign="top">(.*?)</td></tr>')
        matches = pattern.findall(mitigation_table)

        if matches:
            for mitigation in matches:
                mitigation_list.append(mitigation)
    return mitigation_list