

total_page = 5
url = "https://iohk.io/page-data/en/blog/posts/page-{}/page-data.json"

for i in range(total_page):
	print(url.format(i))
