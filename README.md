# spider
Check the site for broken links
```
usage: spider.py [-h] [-q] [-p] [-g] [-m N] url

Check the site for broken inner links in tags <a href=...> and <img src=...>

positional arguments:
  url                URL for links checking

optional arguments:
  -h, --help         show this help message and exit
  -q, --quiet        don't show work progress
  -p, --parents      show list of pages, where the link was used
  -g, --getonly      always use a GET request method instead of HEAD
  -m N, --maxdeep N  maximum recursion level, default is 5
  ```
