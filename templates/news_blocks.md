[NEWS_STEP]
2. Run `python fetch_news.py` -> generates news.md (industry news candidates).

[NEWS_SECTION]
   Then add a second section "Industry & business news": for each item in
   news.md give a translated headline + source + date + original link + 1-2
   sentence note based ONLY on the RSS snippet (never invent details). If
   news.md says NO_NEW_ITEMS or ALL_QUERIES_FAILED, state that honestly.

[NEWS_CARD]
   News items each get one simple card:
   <div class="card">
     <div class="meta"><span class="pill">News</span><a href="LINK">Source</a></div>
     <h2>Translated headline</h2><div class="en">source · date</div>
     <div class="news">1-2 sentence note (RSS snippet only)</div>
   </div>
