#AUTHOR : IMAD BOUZKRAOUI

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
import requests
from bs4 import BeautifulSoup
import re
import json
import os
from urllib.parse import urlparse
import csv
import tkinter as tk

# Create the main window
root = tk.Tk()
root.title("Instagram Profile scraper")
root.geometry("600x500")
# Load the background image
background_image = tk.PhotoImage(file="F.png")

# Create a label with the background image
background_label = tk.Label(root, image=background_image)
background_label.place(x=0, y=0, relwidth=1, relheight=1)

def InstaScrap(username,password,url,download_dir):
    driver = webdriver.Chrome()
    driver.maximize_window()

    # Open instagram account
    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(5)
    
    # Locate the username and password fields
    username_field = driver.find_element(By.NAME, "username")
    password_field = driver.find_element(By.NAME, "password")
    
    # Enter the username and password
    username_field.send_keys(username.get())
    time.sleep(2)
    password_field.send_keys(password.get())
    
    # Click the login button
    login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
    time.sleep(2)
    login_button.click()
    time.sleep(2)
    
    # Open a new tab using JavaScript
    driver.execute_script("window.open()")
    
    # Switch to the new tab
    new_tab = driver.window_handles[-1]  # Get the handle of the last opened tab
    driver.switch_to.window(new_tab)
    time.sleep(6)
    
    # Navigate to the provided URL
    driver.get(url.get())
    
    # Rest of your code...# Get the initial page height
    initial_height = driver.execute_script("return document.body.scrollHeight")
    
    # Create a list to store htmls
    soups = []
    
    while True:
        # Scroll down to the bottom of the page
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
        # Wait for a moment to allow new content to load (adjust as needed)
        time.sleep(5)
        
        # Parse the HTML
        html = driver.page_source
        
        # Create a BeautifulSoup object from the scraped HTML
        soups.append(BeautifulSoup(html, 'html.parser'))
    
        # Get the current page height
        current_height = driver.execute_script("return document.body.scrollHeight")
    
        if current_height == initial_height:
            break  # Exit the loop when you can't scroll further
    
        initial_height = current_height  # Update the initial height for the next iteration
    

    # List to store the post image URLs
    post_urls = []
    
    for soup in soups:
        # Find all image elements that match the specific class in the current soup
        elements = soup.find_all('a',class_="x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz _a6hd")
    
        # Extract the href attributes and filter URLs that start with "/p/" or "/reel/"
        post_urls.extend([element['href'] for element in elements if element['href'].startswith(("/p/", "/reel/"))])
        
    # Convert the list to a set to remove duplicates
    unique_post_urls = list(set(post_urls))
    
    
    print(f"before: {len(post_urls)}, after:{len(unique_post_urls)}")
    
    
    print(unique_post_urls)
    
    json_list = []
    
    # Define the query parameters to add
    query_parameters = "__a=1&__d=dis"
    
    # go through all urls
    for url in unique_post_urls:
        try:
            # Get the current URL of the page
            current_url = driver.current_url
    
            # Append the query parameters to the current URL
            modified_url = "https://www.instagram.com/" + url + "?" + query_parameters
            # Get URL
            driver.get(modified_url)
            # Wait for a moment to allow new content to load (adjust as needed)
            time.sleep(5)
            
            # Find the <pre> tag containing the JSON data
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, '//pre'))
            )
            pre_tag = driver.find_element(By.XPATH,'//pre')
    
            # Extract the JSON data from the <pre> tag
            json_script = pre_tag.text
    
            # Parse the JSON data
            json_parsed = json.loads(json_script)
    
            # Add json to the list
            json_list.append(json_parsed)
        except (NoSuchElementException, TimeoutException, json.JSONDecodeError) as e:
            print(f"Error processing URL {url}: {e}")
    
    json_list
    
    # Lists to store URLs and corresponding dates
    all_urls = []
    all_dates = []
    
    # Iterate through each JSON data in the list
    for json_data in json_list:
        
        # Extract the list from the 'items' key
        item_list = json_data.get('items', [])
        
        # Iterate through each item in the 'items' list
        for item in item_list:
            
            # Extract the date the item was taken
            date_taken = item.get('taken_at')  # Move this line inside the loop
    
            # Check if 'carousel_media' is present
            carousel_media = item.get('carousel_media', [])
            
            # Iterate through each media in the 'carousel_media' list
            for media in carousel_media:
                
                # Extract the image URL from the media
                image_url = media.get('image_versions2', {}).get('candidates', [{}])[0].get('url')
                
                if image_url:
                    # Add the image URL and corresponding date to the lists
                    all_urls.append(image_url)
                    all_dates.append(date_taken)
                    print(f"carousel image added")
                    
                # Extract the video URL from the media
                video_versions = media.get('video_versions', [])
                if video_versions:
                    video_url = video_versions[0].get('url')
                    if video_url:
                        
                        # Add the video URL and corresponding date to the lists
                        all_urls.append(video_url)
                        all_dates.append(date_taken)
                        print(f"carousel video added")
    
            # Handle cases of unique image, instead of carousel
            image_url = item.get('image_versions2', {}).get('candidates', [{}])[0].get('url')
            if image_url:
                
                # Add the image URL and corresponding date to the lists
                all_urls.append(image_url)
                all_dates.append(date_taken)
                print(f"single image added")
    
            # Check if 'video_versions' key exists
            video_versions = item.get('video_versions', [])
            if video_versions:
                video_url = video_versions[0].get('url')
                if video_url:
                    all_urls.append(video_url)
                    all_dates.append(date_taken)
                    print(f"video added")
                    
    # Print or use all collected URLs as needed
    print(len(all_urls))
                    
    print(download_dir)
    # Create a directory to store downloaded files
    os.makedirs(download_dir, exist_ok=True)
    # Create subfolders for images and videos
    image_dir = os.path.join(download_dir, "images")
    video_dir = os.path.join(download_dir, "videos")
    os.makedirs(image_dir, exist_ok=True)
    os.makedirs(video_dir, exist_ok=True)
    
    # Initialize counters for images and videos
    image_counter = 1
    video_counter = 1
    
    # Iterate through URLs in the all_urls list and download media
    for index, url in enumerate(all_urls, 0):
        response = requests.get(url, stream=True)
    
        # Extract file extension from the URL
        url_path = urlparse(url).path
        file_extension = os.path.splitext(url_path)[1]
    
        # Determine the file name based on the URL
        if file_extension.lower() in {'.jpg', '.jpeg', '.png', '.gif','.webp'}:
            file_name = f"{all_dates[index]}-img-{image_counter}.png"
            destination_folder = image_dir
            image_counter += 1
        elif file_extension.lower() in {'.mp4', '.avi', '.mkv', '.mov'}:
            file_name = f"{all_dates[index]}-vid-{video_counter}.mp4"
            destination_folder = video_dir
            video_counter += 1
        else:
            # Default to the main download directory for other file types
            file_name = f"{all_dates[index]}{file_extension}"
            destination_folder = download_dir
    
        # Save the file to the appropriate folder
        file_path = os.path.join(destination_folder, file_name)
    
        # Write the content of the response to the file
        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
    
        print(f"Downloaded: {file_path}")
    
    # Print a message indicating the number of downloaded files and the download directory
    print(f"Downloaded {len(all_urls)} files to {download_dir}")
        

# Create labels
username_label = tk.Label(root, text="Insta username:", font=("Helvetica", 16), bg='pink')
me_label = tk.Label(root, text="By IMAD BOUZKRAOUI", font=("Helvetica", 13), bg='pink')
password_label = tk.Label(root, text="Password:", font=("Helvetica", 16), bg='pink')
url_label = tk.Label(root, text="Profile url:", font=("Helvetica", 16), bg='pink')
path_label = tk.Label(root, text="Path:", font=("Helvetica", 16), bg='pink')
# Create entry fields
username_entry = tk.Entry(root, font=("Helvetica", 16))
password_entry = tk.Entry(root, font=("Helvetica", 16), show="*")  # Password entry, characters will be hidden
url_entry = tk.Entry(root, font=("Helvetica", 16))
direc = tk.Entry(root, font=("Helvetica", 16))
# Position labels and entry fields using grid layout manager
username_label.grid(row=0, column=0, padx=(0,390), pady=10, sticky='e')
username_entry.grid(row=1, column=0, padx=(200,50), pady=10,sticky='nsew')
me_label.grid(row=0, column=0, padx=(250,1), pady=10, sticky='ne')
password_label.grid(row=2, column=0, padx=(0,390), pady=10, sticky='e')
password_entry.grid(row=3, column=0, padx=(200,50) ,pady=10,sticky='nsew')
url_label.grid(row=4, column=0, padx=(0,390), pady=10, sticky='e')
url_entry.grid(row=5, column=0, padx=(200,50), pady=10,sticky='nsew')
path_label.grid(row=6, column=0, padx=(0,390), pady=10, sticky='e')
direc.grid(row=7, column=0, padx=(200,50), pady=10,sticky='nsew')

def show_password():
    if password_entry.cget("show") == "*":
        password_entry.config(show="")
        show_password_button.config(text="Hide Password")
    else:
        password_entry.config(show="*")
        show_password_button.config(text="Show Password")

# Create button to show/hide password
show_password_button = tk.Button(root, text="Show Password", command=show_password)
show_password_button.grid(row=2, columnspan=2, padx=(200,50), pady=10,sticky='se')

def submit():
    dirc=direc.get()
    print(dirc)
    InstaScrap(username_entry,password_entry,url_entry,dirc)
    

# Create submit button
submit_button = tk.Button(root, text="START", bg='hotpink', font=("Helvetica", 16), command=submit)
submit_button.grid(row=8, columnspan=2, padx=(200,50), pady=40,sticky='nsew')

# Make the interface non-resizable
root.resizable(False, False)

# Run the Tkinter event loop
root.mainloop()
