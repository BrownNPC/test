import os

import requests
from bs4 import BeautifulSoup
import hashlib
import os

def download_file(url, file_name):
    """
    Downloads a file from a given URL and saves it locally.
    """
    response = requests.get(url, stream=True)
    with open(file_name, 'wb') as file:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                file.write(chunk)

def get_md5(file_name):
    """
    Computes the MD5 checksum of a file.
    """
    md5_hash = hashlib.md5()
    with open(file_name, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            md5_hash.update(byte_block)
    return md5_hash.hexdigest()

def get_package(url):
    """
    Scrapes the given URL, downloads the file, and saves the MD5 checksum.
    Also downloads dependencies if any are found.

    Args:
    url (str): The URL of the page to scrape.

    Returns:
    str: The 'href' of the first "File" link found, or an empty string if none found.
    """
    print(f"Scraping package page: {url}")
    
    # Send a GET request to the page
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the page content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all 'dt' elements with the text "File:"
        dt_elements = soup.find_all('dt', string="File:")

        file_link = ''
        md5_checksum = ''
        
        # Loop through each 'dt' element
        for dt in dt_elements:
            # Find the next sibling 'dd' tag that contains the link
            dd = dt.find_next_sibling('dd')
            if dd:
                # Find the 'a' tag inside the 'dd' tag and extract the 'href'
                link = dd.find('a')
                if link and 'href' in link.attrs:
                    file_link = link['href']
                    
                    # Look for the md5 checksum two elements after the file link (below SHA256)
                    sha256_dt = dt.find_next_siblings('dt', string="SHA256:")
                    if sha256_dt:
                        md5_dd = sha256_dt[0].find_next_sibling('dd')
                        if md5_dd:
                            md5_checksum = md5_dd.get_text(strip=True)
                    break  # Break after finding the first valid link

        if file_link:
            file_name = file_link.split('/')[-1]

            # Check if file already exists
            if os.path.exists(file_name):
                print(f"{file_name} already exists, skipping download.")
            else:
                print(f"Downloading {file_name}...")
                download_file(file_link, file_name)
                print(f"{file_name} downloaded.")

            # Save MD5 checksum to a file
            md5_from_file = get_md5(file_name)
            with open(f"{file_name}.md5", "w") as md5_file:
                md5_file.write(f"MD5 ({file_name}) = {md5_from_file}\n")
                print(f"MD5 checksum saved: {md5_from_file}")

        # Find dependencies and download them
        dependencies_dt = soup.find('dt', string="Dependencies:")
        if dependencies_dt:
            dependency_list = dependencies_dt.find_next()
            if dependency_list:
                dependency_links = dependency_list.find_all('a')
                if dependency_links:
                    print(f"Found {len(dependency_links)} dependencies.")
                else:
                    print("No dependencies found.")
                for dep in dependency_links:
                    dep_url = dep['href']
                    print(f"Found dependency: {dep_url}")
                    get_package(dep_url)  # Recursively download the dependency
            else:
                print("No dependency list found.")
        else:
            print("No dependencies section found.")
        
        return file_link
    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return ''

deps = "build-essential git python3 python3-docutils liblua5.2-dev libass-dev libjpeg-dev \
libx264-dev libfdk-aac-dev libmpv-dev yasm libxcb-shm0-dev \
gcc g++ yasm git ninja-build autoconf \
libx11-dev libxext-dev libxv-dev libvdpau-dev libgl1-mesa-dev \
libasound2-dev libpulse-dev libfribidi-dev libfreetype6-dev \
libfontconfig1-dev libjpeg-dev libssl-dev libgnutls28-dev \
libx264-dev libmp3lame-dev libfdk-aac-dev make wget tar zstd gawk gpg \
binutils-mingw-w64 mingw-w64 "

os.system(f"sudo apt update && sudo apt install -y {deps}")

os.system("clear")
print("downloading deps")

try:
    os.mkdir("build_libs")
except:
    pass
os.chdir("build_libs")

url = "https://packages.msys2.org/packages/mingw-w64-x86_64-mpv"
get_package(url)

files = os.listdir()
for file in files:
    if file.endswith(".pkg.tar.zst"):
        print(f"\n\nextracting {file}\n--------------------------------------")
        os.system(f"tar -xvf {file}")
        


# os.system("export PKG_CONFIG_PATH=$(pwd)/mingw64/lib/pkgconfig:$PKG_CONFIG_PATH")

# os.system("export CC=x86_64-w64-mingw32-gcc")
# os.system("export CXX=x86_64-w64-mingw32-g++")
# os.system("export CGO_ENABLED=1")
# os.system("export GOOS=windows")
