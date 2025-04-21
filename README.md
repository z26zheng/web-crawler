# web-crawler

## TODOs
1. The redfin crawler can't advance the search result pages. It's currently only scraping listings on Page 1.
1. Scraping can get stuck and we need to solve two corner cases:
    1. After scraping 40 properties, a captch page will show up. We need to solve work with captcha.
    1. The page will pop up a login, we should either login, or refresh the page, or maybe this doens't matter to playwrite.