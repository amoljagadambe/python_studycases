import requests
from bs4 import BeautifulSoup
import smtplib

URL = 'https://www.amazon.in/Samsung-Galaxy-Storage-Additional-Exchange/dp/B07KXCH2FP/ref=sr_1_4?dchild=1&keywords' \
      '=samsung+s10&qid=1598435296&sr=8-4 '

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/84.0.4147.135 Safari/537.36"}


def check_price():
    page = requests.get(URL, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')

    title = soup.find(id="productTitle").get_text()
    price = soup.find(id='priceblock_dealprice').get_text()
    converted_price = int(price[2:8].replace(',', ''))

    if converted_price > 45000:
        send_email(title)


passowrd = 'lhmwvmeisetwvgrr'
mail = 'amoljagadambe0076@gmail.com'


def send_email(title):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()

    server.login(mail, passowrd)

    subject = 'Hey, Amol this is your Lazarus'
    body = f"Please check amazon link now {URL}"

    msg = f"Subject:  {subject} \n\nYour Product {title.strip()} is available below price of 450000 \n\n{body}"

    server.sendmail(
        from_addr=mail, to_addrs='amol.jagdambe@gmail.com',
        msg=msg
    )
    print('hey email has been sent')
    server.quit()


check_price()