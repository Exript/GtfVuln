#!/usr/bin/env python
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def print_header():
    ascii_art = '''
    ___________              .__        __    
    \_   _____/__  __________|__|______/  |_  
     |    __)_\  \/  /\_  __ \  \____ \   __\ 
     |        \>    <  |  | \/  |  |_> >  |   
    /_______  /__/\_ \ |__|  |__|   __/|__|   
            \/      \/          |__|          
    '''
    print(ascii_art)

def get_soup(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.content, 'lxml')
    except requests.RequestException as e:
        print(f"Error while getting soup: {e}")
        return None

def get_links_from_table(url, table):
    rows = table.find_all('tr')
    results = []

    for row in rows:
        columns = row.find_all('td')

        if columns:
            first_column = columns[0]
            link = first_column.find('a')

            if link:
                link_text = link['href'].strip('/')
                full_url = urljoin(url, link['href'].lstrip('/'))
                result = f"{link_text.split('/')[-1]}={full_url}"

                # Additional check: Only links on the page containing #+suid
                if '#+suid' in full_url:
                    results.append(result)

    return results

def scrape_bin_table(url):
    full_url = url + '#+suid'
    soup = get_soup(full_url)

    if not soup:
        return None

    bin_table = soup.find('table', {'id': 'bin-table'})

    if bin_table:
        results = get_links_from_table(full_url, bin_table)
        return results
    else:
        print(f"Error: Table with id 'bin-table' not found on {full_url}")
        return None

def find_setuid_setgid_files():
    try:
        files = []
        for root, dirs, file_list in os.walk('/'):
            for file_name in file_list:
                file_path = os.path.join(root, file_name)
                if os.path.isfile(file_path) and (os.stat(file_path).st_mode & 0o6000):
                    files.append(file_path)

        return files
    except Exception as e:
        print(f"Error while finding setuid and setgid files: {e}")
        return None

def main():
    print_header()

    url = "https://gtfobins.github.io/"
    bin_links = scrape_bin_table(url)

    if bin_links is not None and bin_links:  
        setuid_setgid_files = find_setuid_setgid_files()

        if setuid_setgid_files:
            matches = []
            max_bin_length = max(len(link_info.split('=')[0]) for link_info in bin_links)

            for file_path in setuid_setgid_files:
                for link_info in bin_links:
                    bin_name, bin_url = link_info.split('=')
                    # Exact match check
                    if bin_name == os.path.basename(file_path):
                        matches.append((bin_name, bin_url))

            if matches:
                print("\nGotchu SUID\n-----------------")
                for bin_name, bin_url in matches:
                    print(f"{bin_name.ljust(max_bin_length)} -------> {bin_url}")
                print("\nHappy Hack Day ^-^")
            else:
                print("\n---------------------------------------------\nThere is nothing here :(")
        else:
            print("\n---------------------------------------------\nThere is nothing here :(")
    else:
        print("\n---------------------------------------------\nThere is nothing here :(")

if __name__ == "__main__":
    main()
