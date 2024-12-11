import zipfile
import sys
import os
import pyfiglet
from termcolor import colored

# Function to clear the terminal
def clear_terminal():
    os.system('clear')  # Clears the terminal screen

# Banner function using pyfiglet with a more stylish font
def banner():
    ascii_banner = pyfiglet.figlet_format("ZIP CRACKER", font="slant")  # "slant" font added here
    print(colored(ascii_banner, "cyan"))  # Banner in cyan color for a better look
    print(colored("=====================================", "cyan"))
    print(colored("Created by: Sunil", "green"))
    print(colored("Channel: Noob Cyber Tech", "yellow"))
    print(colored("Instagram: @annon_4you", "yellow"))
    print(colored("GitHub: https://github.com/yourusername", "green"))
    print(colored("=====================================", "cyan"))

# Function to crack zip password
def crack_zip_password(zip_file, wordlist_file):
    try:
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            total_words = sum(1 for line in open(wordlist_file, 'r'))
            print(colored(f"Total words in wordlist: {total_words}", "cyan"))
            
            with open(wordlist_file, 'r') as file:
                attempts = 0
                found = False
                for word in file:
                    word = word.strip()
                    attempts += 1
                    try:
                        zip_ref.setpassword(word.encode())
                        zip_ref.testzip()
                        if not found:
                            found = True
                            print(colored(f"✅ Password found: {word}", "green"))
                            break
                    except:
                        pass
                if not found:
                    print(colored("❌ Password not found in the wordlist.", "red"))
                else:
                    print(colored(f"Total Attempts: {attempts}", "yellow"))

    except FileNotFoundError:
        print(colored("❌ Zip file not found. Please check the file path.", "red"))
        sys.exit(1)

# Main function
def main():
    clear_terminal()  # Clear terminal before running the script
    banner()

    # User input for zip file and wordlist
    zip_file = input(colored("Enter the path to the zip file: ", "green"))
    if not os.path.exists(zip_file):
        print(colored("❌ Zip file does not exist. Please check the file path.", "red"))
        sys.exit(1)

    wordlist_file = input(colored("Enter the path to the wordlist file: ", "green"))
    if not os.path.exists(wordlist_file):
        print(colored("❌ Wordlist file does not exist. Please check the file path.", "red"))
        sys.exit(1)

    # Start the cracking process
    crack_zip_password(zip_file, wordlist_file)

if __name__ == "__main__":
    main()
