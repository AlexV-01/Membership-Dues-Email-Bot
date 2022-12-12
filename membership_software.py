import pandas as pd
import pandasql as ps
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from termcolor import colored

"""
EMAIL BOT
"""
# chrome driver setup
options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_experimental_option('excludeSwitches', ['enable-logging'])
e_options = webdriver.ChromeOptions() # USE THIS TO SEE HEAD (DEBUGGING)

def emailLogin(): # returns the driver for sendEmail function to use
    try:
        driver = webdriver.Chrome(options=options)
        driver.get('https://account.proton.me/login?language=en')
        sleep(2)
        username = driver.find_element('id', 'username')
        username.send_keys("automatedtest@protonmail.com") # this is the email address of the bot. Using protonmail
        password = driver.find_element('id', 'password')
        password.send_keys("moosemilk")
        password.submit()
        sleep(14)
    except Exception as e:
        input(colored(f"{e}\nPRESS ENTER TO EXIT.", 'red'))
        exit()
    return driver

def sendEmail(first, last, year, amount, email, driver):
    try:
        actions = ActionChains(driver)
        actions.send_keys('n')
        actions.pause(1)
        actions.send_keys(email) # sending email to this person
        actions.pause(0.1)
        actions.send_keys(",")
        actions.pause(0.1)
        actions.send_keys(Keys.TAB)
        actions.pause(0.5)
        actions.send_keys("MEMBERSHIP DUES EMAIL TEST")
        actions.pause(0.5)
        actions.send_keys(Keys.TAB)
        actions.pause(0.2)
        actions.send_keys(f"First name: {first}. Last name: {last}. Year: {year}. Amount owed: {amount}.")
        actions.pause(2)
        for i in range(40): # delete the "sent with protonmail" text
            actions.send_keys(Keys.DELETE)
            actions.pause(0.02)
        for i in range(15):
            actions.send_keys(Keys.TAB)
            actions.pause(0.1)
        actions.pause(5)
        actions.send_keys(Keys.ENTER)
        actions.perform()
        sleep(2)
        print(colored(f"Email sent to {first} {last} for {amount}.", 'green'))
        sleep(0.5)
    except Exception as e:
        print(f"Unable to send email. Error: {e}")

"""
FILTERING
"""
def makeDataFrame(file, year): # returns a dataframe filtered by year
    data = pd.read_csv(file)
    pd.set_option('display.max_rows', None)
    filtered = data[['MemberID', 'LNAME', 'NAME1', 'amount-'+str(year), 'paid-'+str(year), 'Email:']]
    filtered.columns = ['MemberID', 'LNAME', 'FNAME', 'amount'+str(year), 'paid'+str(year), 'EMAIL']
    return filtered
    
def getNotPaid(df, year): # returns a dataframe of only those who haven't paid in the year
    filtered = ps.sqldf(f"SELECT * FROM df WHERE amount{str(year)} IS NOT NULL AND paid{str(year)} IS NULL")
    return filtered

def getNamesAndAmount(df, year): # returns a hash table of the names of those who haven't paid with the amounts due and emails
    nameToInfo = {}
    for i in range(len(df)):
        nameToInfo[(df._get_value(i, 'FNAME'), df._get_value(i, 'LNAME'))] = (df._get_value(i, 'amount' + str(year)), df._get_value(i, 'EMAIL'))
    return nameToInfo

"""
MAIN
"""
def main():
    year = input(colored("Year: ", 'green'))
    valid = False
    while not valid:
        try:
            df = makeDataFrame('testfile.csv', year) # 'data.csv' is the input file
            valid = True
        except:
            print(colored("This year does not exist in the database. Choose another year.", 'red'))
            year = input(colored("Year: ", 'green'))
    print()
    not_paid = getNotPaid(df, year)
    hash_table = getNamesAndAmount(not_paid, year)
    if len(hash_table) == 0:
        print(colored("EVERYONE HAS PAID!", 'green'))
    else:
        print(colored("Logging in...", 'green'))
        driver = emailLogin()
        print(colored("Login successful!", 'green'))
    for person in hash_table:
        if hash_table[person][1] is None:
            print(colored(f"{person[0]} {person[1]} owes {hash_table[person][0][:-1]}. No email recorded.", 'yellow'))
            continue
        print(colored("Writing email...", 'green'))
        sendEmail(person[0], person[1], year, hash_table[person][0][:-1], hash_table[person][1], driver)
    try:
        driver.quit()
    except:
        pass
    input(colored("Press Enter to finish.", 'yellow'))
    print(colored("Closing...", 'yellow'))

if __name__ == '__main__':
    main()
