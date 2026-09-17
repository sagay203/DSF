DSF Scholarship Portal

A searchable directory of 141 scholarship schemes available to students in Karnataka for the academic year 2026–27, built by Dream School Foundation.

Live site: https://YOUR-PROJECT.vercel.app (replace with your actual Vercel URL)

Students, families, and field staff can filter schemes by class, social category, family income, gender, and course type, then track deadlines and build a shortlist.

⚠️ Before you quote a figure to a family

Karnataka state scheme details here come from secondary sources and are not verified against the state portal. Central schemes were read from the National Scholarship Portal.

Always check the official link on a scheme before relying on an amount or a date. Deadlines move, amounts change, and eligibility rules get revised mid-year. This directory is a starting point for finding schemes, not a substitute for the official source.

What's in this repository
File	Purpose
DSF_Scholarship_Portal.html	The public site. Self-contained — all scheme data is inside the file.
DSF_Scholarship_Editor.html	Internal tool for reviewing and updating scheme records.
DSF_scholarships.json	Source data for all schemes. The single source of truth.
update_portal.py	Rewrites the scheme data inside both HTML files from the JSON.
vercel.json	Points the site root at the portal page.
How it works

There is no framework, no database, no build step, and no server code. Each HTML file carries its own copy of the scheme data inlined as a JavaScript array, along with all its styles and logic.

That design has a useful side effect: the portal works offline. Download DSF_Scholarship_Portal.html, open it on any laptop or phone, and it runs with no internet connection — which matters for field work in areas with patchy connectivity. It can be shared over WhatsApp or copied to a USB drive and it still works.

Nothing a visitor types is stored or transmitted. Filters and shortlists live in the browser tab and disappear when it closes.

Updating the scheme data

For one small fix (a shifted deadline, a typo), edit the HTML directly on GitHub using the pencil icon. Make the same edit in both HTML files, or they will drift out of sync.

For anything larger, use the script:

Open DSF_Scholarship_Editor.html, make your changes, and export the updated JSON.
Rename the export to DSF_scholarships.json.
Put that file, both HTML files, and update_portal.py in one folder.
Run:
   python update_portal.py
Upload the two updated HTML files to this repository. The live site redeploys automatically within a minute.

The script validates the data before writing anything — it checks the JSON parses, that every scheme has an id and a name, and that no id appears twice. If any check fails it reports the problem and changes nothing. It also saves a timestamped backup of each HTML file before editing it.

Deployment

Hosted on Vercel. Every commit to the main branch redeploys the site automatically — there is nothing to build or configure.

Because the site is three static files, it can be hosted anywhere that serves static content. Cloudflare Pages, Netlify, or GitHub Pages would all work with the same files.

Contributing

Corrections are welcome, particularly from anyone working with these schemes on the ground. If you spot a wrong deadline, a changed amount, or a scheme that has closed, please open an issue with the scheme name and a link to the official source.

About Dream School Foundation

DSF is a Bangalore-based nonprofit working in education and youth development across Karnataka, including the TYDE Rural Programme and NMMS scholarship coaching. This portal was built to help students find the financial support they are already entitled to but often never hear about.
