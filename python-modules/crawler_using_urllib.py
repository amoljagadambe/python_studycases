import requests

download_dir = 'C:/Users/amolj/OneDrive/Pictures/Quotes_for_mobile/'


# image_url = 'https://cdn2.geckoandfly.com/wp-content/uploads/2018/04/iphone-smartphone-wallpaper-102.jpg'
# img_data = requests.get(image_url, allow_redirects=True).content
# with open(download_dir+ 'quote_2.jpg', 'wb') as handler:
#     handler.write(img_data)

for i in range(5,103):
    image_url = 'https://cdn2.geckoandfly.com/wp-content/uploads/2018/04/iphone-smartphone-wallpaper-{0:03}.jpg'.format(i)
    img_data = requests.get(image_url, allow_redirects=True).content
    with open(download_dir + 'quotes_{0:03}.jpg'.format(i), 'wb') as handler:
        handler.write(img_data)
