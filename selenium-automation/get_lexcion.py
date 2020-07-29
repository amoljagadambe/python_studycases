from selenium import webdriver
from time import sleep
import os

word_list = []
BASE_DIR = os.getcwd()
word_file_path = os.path.join(BASE_DIR, 'NID_lexicon_health.txt')
store_lex_file_path = os.path.join(BASE_DIR, 'output_lexicon.txt')
nid_word_store_path = os.path.join(BASE_DIR, 'not_found_words.txt')


class LexiconBot:
    def __init__(self):
        self.driver = webdriver.Chrome('C:/Installed-Software/sel-chrome-driver/chromedriver.exe')
        self.driver.get("http://www.speech.cs.cmu.edu/cgi-bin/cmudict")
        self.driver.find_element_by_xpath('//input[@type="checkbox"]') \
            .click()
        sleep(2)

    def load_file(self, file_path, mode):
        file_loader = open(file_path, mode)
        for word in file_loader:
            word_list.append(word.strip('\n'))
        file_loader.close()
        return word_list

    def get_phonemes(self):
        file_loader = self.load_file(word_file_path, "r")
        save_file = open(store_lex_file_path, "a")
        exception_word = open(nid_word_store_path, "a")
        for word in file_loader:
            try:
                word_element = self.driver.find_element_by_xpath("//input[@name=\"in\"]")
                word_element.clear()
                word_element.send_keys(word)
                self.driver.find_element_by_xpath('//input[@type="submit"]') \
                    .click()
                sent_word = self.driver.find_element_by_xpath('/html/body/div/tt[1]')
                phonemes = self.driver.find_element_by_xpath('/html/body/div/tt[2]')
                output = sent_word.text + " " + phonemes.text.strip('.') + '\n'
                print(output)
                save_file.write(str(output))

            except:
                exception_word.write(word.upper() + '\n')
        self.driver.close()
        save_file.close()
        exception_word.close()


lex_bot = LexiconBot()
lex_bot.get_phonemes()
