import sys
import time
import os
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import string



class content_finished_loading(object):
    def __init__(self, element):
        self.element = element

    def __call__(self, driver):
        if self.element.text.strip() == "Loading...":
            return False
        else:
            return self.element

class element_is_expanded(object):
    def __init__(self, root_element, locator, is_expanded="true"):
        self.root_element = root_element
        self.locator = locator
        self.is_expanded = is_expanded 

    def __call__(self, driver):
        element = self.root_element.find_element(*self.locator)
        if self.is_expanded == element.get_attribute("aria-expanded"):
            return element
        else:
            return False

def save_file(path: Path, filename: str, data):
    with Path(path, filename).open("w") as fp:
        fp.write(data)

def save_lesson_as_html(dir, chapter_title, lesson_title, html):
    path = Path(f'./{dir}/{chapter_title}/')
    path.mkdir(parents=True, exist_ok=True)
    save_file(path, f"{lesson_title}.html", html)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("""
$$$$$$$\                                                  $\          
$$  __$$\                                                  $          
$$ |  $$ | $$$$$$\   $$$$$$\   $$$$$$\   $$$$$$\   $$$$$$\  /$$$$$$\ 
$$$$$$$  |$$  __$$\ $$  __$$\ $$  __$$\ $$  __$$\ $$  __$$\ $$  ____|
$$  __$$< $$ /  $$ |$$ /  $$ |$$ /  $$ |$$$$$$$$ |$$ |  \__|\$$$$$$\ 
$$ |  $$ |$$ |  $$ |$$ |  $$ |$$ |  $$ |$$   ____|$$ |       \____$$\\
$$ |  $$ |\$$$$$$  |$$$$$$$  |$$$$$$$  |\$$$$$$$\ $$ |      $$$$$$$  
\__|  \__| \______/ $$  ____/ $$  ____/  \_______|\__|      \_______/
                    $$ |      $$ |                                                           
                    $$ |      $$ |                                                           
                    \__|      \__|""")
        print("""
$$$$$$$$\ $$\       $$\           $$\       $$\  $$$$$$\  $$\           
\__$$  __|$$ |      \__|          $$ |      \__|$$  __$$\ \__|          
   $$ |   $$$$$$$\  $$\ $$$$$$$\  $$ |  $$\ $$\ $$ /  \__|$$\  $$$$$$$\ 
   $$ |   $$  __$$\ $$ |$$  __$$\ $$ | $$  |$$ |$$$$\     $$ |$$  _____|
   $$ |   $$ |  $$ |$$ |$$ |  $$ |$$$$$$  / $$ |$$  _|    $$ |$$ /      
   $$ |   $$ |  $$ |$$ |$$ |  $$ |$$  _$$<  $$ |$$ |      $$ |$$ |      
   $$ |   $$ |  $$ |$$ |$$ |  $$ |$$ | \$$\ $$ |$$ |      $$ |\$$$$$$$\ 
   \__|   \__|  \__|\__|\__|  \__|\__|  \__|\__|\__|      \__| \_______|""")
        print("""
 $$$$$$\                                                             
$$  __$$\                                                            
$$ /  \__| $$$$$$$\  $$$$$$\  $$$$$$\   $$$$$$\   $$$$$$\   $$$$$$\  
\$$$$$$\  $$  _____|$$  __$$\ \____$$\ $$  __$$\ $$  __$$\ $$  __$$\ 
 \____$$\ $$ /      $$ |  \__|$$$$$$$ |$$ /  $$ |$$$$$$$$ |$$ |  \__|
$$\   $$ |$$ |      $$ |     $$  __$$ |$$ |  $$ |$$   ____|$$ |      
\$$$$$$  |\$$$$$$$\ $$ |     \$$$$$$$ |$$$$$$$  |\$$$$$$$\ $$ |      
 \______/  \_______|\__|      \_______|$$  ____/  \_______|\__|      
                                       $$ |                          
                                       $$ |                          
                                       \__|""")
        print("Usage: python ./scrape.py <course_url> <save_dir>")
        print("For example: python ./scrape.py  https://www.roppers.org ComputingFundamentals")
        print("Provide login creds via env vars THINKIFIC_USER and THINKIFIC_PASS")
    else:
        try:
            THINKIFIC_USER = os.environ["THINKIFIC_USER"]
            THINKIFIC_PASS = os.environ["THINKIFIC_PASS"]
        except KeyError:
            print("[!] A username and password are required to login to the course page.")
            print("[!] Please provide values for the env vars THINKIFIC_USER and THINKIFIC_PASS and try again.")
            exit(1)


        try:
            course_url = sys.argv[1]
            save_dir = sys.argv[2]

            # Intialize Selenium browser driver
            opts = ChromeOptions()
            opts.add_argument("--window-size=1600,900")
            #driver = webdriver.Chrome(options=opts)
            cService = webdriver.ChromeService(executable_path='/home/kali/roppers-thinkific-scraper/chromedriver')
            driver = webdriver.Chrome(service = cService)


            driver.implicitly_wait(1)
            driver.get(course_url)

            # Default driver wait
            wait = WebDriverWait(driver, 10)

            # Navigate to sign in page
            sign_in_btn = driver.find_element(By.LINK_TEXT, "SIGN IN")
            sign_in_btn.click()


            # Login in to target Thinkific course page
            user_input = driver.find_element(By.ID, "user[email]")
            user_input.send_keys(THINKIFIC_USER)
            pass_input = driver.find_element(By.ID, "user[password]")
            pass_input.send_keys(THINKIFIC_PASS)

            submit_btn = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            print("Waiting for login process...", flush=True)
            submit_btn.click()
            wait.until(EC.title_contains("Dashboard"))

            # Select Thinkific course from dashboard
            course_anchors = driver.find_elements(By.CSS_SELECTOR, 'ul[class="products__list"] div[class="card__header"] > a')

            print("The following courses were found:")
            for i,anchor in enumerate(course_anchors):
                href = anchor.get_attribute("href")
                text = anchor.get_attribute("text")
                print(f"- {i}: {text.strip()} => {href}")

            index = input("Select a course number: ")

            # Load course page
            print("Navigating to course...", flush=True)
            driver.get(course_anchors[int(index)].get_attribute("href"))
            wait.until(EC.presence_of_element_located((By.ID, "player-wrapper")))

            # Navigate lessons by chapter and save source files
            chapter_divs = driver.find_elements(By.CSS_SELECTOR, 'div[class="course-player__chapters-menu "] > div')
            path = Path('./'+save_dir+'/')
            path.mkdir(parents=True, exist_ok=True)
            file0 = open(save_dir+"/SUMMARY.md","w")
            file0.write("# Summary\n\n")
            file1 = open(save_dir+"/index.html","w")
            file1.write("<h1> Summary </h1>")
            for div in chapter_divs:
                chapter_title = div.find_element(By.TAG_NAME, "h2").text
                print(f"[!] {chapter_title}")
                file0.write("\n## "+chapter_title +"\n\n")
                file1.write("<h2> "+chapter_title +"</h2>")

                chapter_title_stripped = chapter_title.replace(' ', '')
                # Expand chapter if needed
                expand_toggle = div.find_element(By.CSS_SELECTOR, 'span:nth-last-child(1)')

                expanded_div_locator = (By.CSS_SELECTOR, "div:nth-of-type(1)")
                if not element_is_expanded(div, expanded_div_locator, "true")(driver):
                    expand_toggle.click()
                    wait.until(element_is_expanded(div, expanded_div_locator, "true"))
                
                # Save each lesson HTML to file
                lesson_lis = div.find_elements(By.TAG_NAME, "li")

                # TODO: replace time.sleep with appropriate Wait
                time.sleep(0.1) # delay to ensure lesson li tags are loaded
                moduleCount = 0
                for li in lesson_lis:
                    anchor = li.find_element(By.CSS_SELECTOR, "a")
                    href = anchor.get_attribute("href")

                    title = anchor.find_element(By.CSS_SELECTOR, "div:nth-last-child(1)").text.split('\n')[0].strip()
                    orig_title = title
                    for char in string.punctuation:
                        title = title.replace(char, '')
                    titleStripped = title.replace(' ', '')
                    combined_title = str(moduleCount)+"-"+titleStripped
                    file0.write("* ["+title+"]("+chapter_title_stripped+"/"+combined_title+".md)\n")
                    file1.write("<p> <a href= "+chapter_title_stripped+"/"+combined_title +".html>" +title + "</a> </p>")

                    
                    moduleCount+=1

                    print(f"  - {title} => {href}")

                    wait.until(EC.element_to_be_clickable(li))
                    li.click() # open lesson content
                    
                    # Wait until lesson content is loaded
                    #main_content = driver.find_element(By.ID, "content-inner")
                    title_html = driver.find_element(By.CLASS_NAME, "content-item__title")
                    main_content = driver.find_element(By.CLASS_NAME, "fr-view")


                    wait.until(content_finished_loading(main_content))
                    html = "<h1>" + orig_title + "</h1>"
                    html += main_content.get_attribute("innerHTML")

                    save_lesson_as_html(save_dir, chapter_title_stripped, combined_title, '\n'.join([x.strip() for x in html.split('\n')]))

            driver.close
        except KeyboardInterrupt:
            print("\nStopping scrape...")
            exit(0)