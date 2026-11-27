---
layout: page
title: Luca Cogo
name: Luca Cogo
initials: LC
position: PhD Student
order: 7
image: assets/img/ivl/people/luca-cogo.png
email: l.cogo@campus.unimib.it
office: Building U14, Room 1038
phone: +39 02 6448 7893
links:
  - title: GitHub
    url: https://github.com/LucaCogo
    icon: fa-brands fa-github
  - title: LinkedIn
    url: https://www.linkedin.com/in/luca-cogo
    icon: fa-brands fa-linkedin
  - title: ORCID
    url: https://orcid.org/0009-0001-0056-053X
    icon: fa-brands fa-orcid
  - title: Personal Website
    url: https://lucacogo.github.io/
    icon: fa-solid fa-globe
  - title: Google Scholar
    url: https://scholar.google.com/citations?user=Sm13__0AAAAJ
    icon: fa-brands fa-google-scholar

bio: >-
  Luca Cogo is a PhD student in DISCo at the University of Milano-Bicocca. He received bachelor's and master's degrees in Computer Science from the same university in 2020 and 2023. His research focuses on computational photography and image enhancement.

# Optional: courses taught by the member (the Teaching section is hidden when empty)
# teaching:
#   - course: Course name
#     degree: B.Sc. in Computer Science
#     url: https://elearning.unimib.it/
#     period: 2025–present
---

{% include person_profile.liquid person=page %}

## Publications

<div class="publications lab-member-publications" data-pub-list data-page-size="10">
{% bibliography --query @*[author~=Cogo] %}
</div>
