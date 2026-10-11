# Real 1950s pages

These are the ground-truth samples. Boxes are pixels of the PNG in this folder, `[x, y, width, height]`, origin at the top left. `order` inside an article is the reading order.

| File | Page |
|---|---|
| [`newmarket_1952-01-31_p1.png`](./newmarket_1952-01-31_p1.png) | *The Newmarket Era and Express*, Newmarket, Ontario, Thursday 31 January 1952. Front page. English, left to right. |
| [`newmarket_1952-01-31_p1.json`](./newmarket_1952-01-31_p1.json) | The articles a student must separate on that page, and the traps. |
| [`falastin_1958-10-31_p1.png`](./falastin_1958-10-31_p1.png) | *Falastin* (فلسطين), Jerusalem, Friday 31 October 1958. Front page. Arabic, right to left. |
| [`falastin_1958-10-31_p1.json`](./falastin_1958-10-31_p1.json) | The banner, the speech, and the traps. |
| [`chettinadu_1955-10_p8.png`](./chettinadu_1955-10_p8.png) | *செட்டிநாடு*, Devakottai, October–November 1955, printed page 8. Tamil, left to right. A weekly, two columns, with a picture. |
| [`chettinadu_1955-10_p8.json`](./chettinadu_1955-10_p8.json) | The picture, the Kamala article, the right-column continuation, and the traps. |
| [`elpaso_herald_1920-08-20_p1.png`](./elpaso_herald_1920-08-20_p1.png) | *El Paso Herald*, El Paso, Texas, Friday evening, 20 August 1920. Front page. The print is faint. This is the page to score. |
| [`elpaso_herald_1920-08-20_p1.json`](./elpaso_herald_1920-08-20_p1.json) | Every story on that page. Each story is one or more boxes. Merge the boxes that share an article. |

## Where the scans come from

- English. [Internet Archive, Newmarket Era and Express, 31 January 1952](https://archive.org/details/NewmarketEraAndExpress_847). The item is marked Public Domain.
- Arabic. [Palestinian Papers, Falastin 31 October 1958](https://palpapers.net/download/falastin-1958-31-10/). That archive says its scans are out of copyright and freely downloadable.
- Tamil. [Internet Archive, செட்டிநாடு வார இதழ், October–November 1955](https://archive.org/details/acc.-no.-33771-chettinadu-1955-nov-dec). The item is marked Public Domain. Printed page 8 of that issue.
- English, the scored page. [The Portal to Texas History, El Paso Herald, 20 August 1920](https://texashistory.unt.edu/ark:/67531/metapth137750/). Marked Public Domain. Digitized from 35mm microfilm. The file in this folder is that front page at 1500 by 1795 pixels.

Newmarket, Falastin, and Chettinadu are 1600 pixels wide. The El Paso Herald file is 1500 by 1795. Use the width and height written in each JSON. A box from one file does not fit another scan.

## Tamil

This page is a 1955 Tamil **weekly**, not Dinamani or another daily. Those dailies are not in a collection that lets us put the scan in this public repo. செட்டிநாடு is real 1955 Tamil news print, two columns, with a picture in the column, and the archive marks it public domain. Use it to try `lang="ta"`. The page that is graded is the El Paso Herald.

## What “correct” means here

On the Newmarket, Falastin, and Chettinadu pages, the boxes cover the traps. A student passes those when each article’s blocks come out in the `order` given, and a block from one article does not appear inside another.

On the El Paso Herald page, the JSON is the whole front page. There are 30 stories. A story that crosses a column has several boxes, in reading order. Merge those boxes and no others.

How a student compares:

1. Open `elpaso_herald_1920-08-20_p1.png`. It is 1500 pixels wide and 1795 tall.
2. A box is `[x, y, width, height]` in pixels of that file. The origin is the top left.
3. For each object in `articles`, the `boxes` list is one story. `polish_war` has four boxes. `villa` has two. `allendorf` has four. Most stories have one.
4. Your article passes when the region you merged covers that list and does not include a box from a different article.
5. `not_a_story` is the price box, the masthead, the weather box, and the line along the bottom. Leave them out.

The boxes were drawn on the scan again after they were written. A headline stays inside its own story, including the last word of "Appeal to de la Huerta," and a box does not cross into the story beside it. The boxes do not overlap. Tesseract, asked for the words on this file, returned 89 of them. The body type is still there for a person. The score is the boxes, not those 89 words.
