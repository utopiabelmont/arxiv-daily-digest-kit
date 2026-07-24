[YOUTUBE_SECTION]
   Then add a section "Research videos": for each item in youtube.md give a
   translated title + channel + date + original YouTube link + a 1-2 sentence
   note based ONLY on the API description snippet. Never claim to have watched,
   transcribed, or verified the video. If youtube.md says NO_NEW_VIDEOS or
   ALL_YOUTUBE_QUERIES_FAILED, state that honestly.

[YOUTUBE_CARD]
   YouTube items each get one simple card:
   <div class="card">
     <div class="meta"><span class="pill yt">YouTube</span>
       <a href="LINK">Watch</a></div>
     <a href="LINK"><img class="video-thumb" src="THUMBNAIL" alt=""
       loading="lazy" referrerpolicy="no-referrer"></a>
     <h2>Translated title</h2><div class="en">channel · date</div>
     <div class="video">1-2 sentence note based only on the description
       snippet</div>
   </div>
   Use the image element only when THUMBNAIL begins with
   `https://i.ytimg.com/`; otherwise omit it.
