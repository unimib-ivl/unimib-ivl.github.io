---
layout: page
title: Accessibility statement
permalink: /accessibility/
description: Accessibility statement for the website of the Imaging and Vision Laboratory.
nav: false
# Date of the evaluation the statement is based on; update it after each re-test.
prepared: 2026-11-25
# When the University publishes the AgID accessibility statement for this site (form.agid.gov.it),
# paste its URL here and it is linked under "Preparation of this accessibility statement".
agid_statement_url:
---

{% comment %}
  Structure and wording follow the model accessibility statement of Commission Implementing Decision (EU) 2018/1523
  (Annex, Section 1: mandatory content). Re-test before changing the compliance status or the list of non-accessible content.
{% endcomment %}

The University of Milano-Bicocca is committed to making its websites accessible, in accordance with Law no. 4 of 9 January 2004,
as amended by Legislative Decree no. 106 of 10 August 2018 transposing Directive (EU) 2016/2102 of the European Parliament and of the Council.

This accessibility statement applies to the website of the Imaging and Vision Laboratory, {{ site.url | remove: 'https://' }}.

## Compliance status

This website is partially compliant with the requirements of the harmonised standard EN 301 549 (WCAG 2.1, level AA),
due to the non-compliances and the exemptions listed below.

## Non-accessible content

The content listed below is non-accessible for the following reasons.

(a) Non-compliance with Law 4/2004:

- Images illustrating publications have a text alternative that gives the title of the paper but does not describe the figure (WCAG 2.1, success criterion 1.1.1).
- PDF files of publications published after 23 September 2018 may lack tags, a defined reading order or text alternatives for figures (success criteria 1.1.1 and 1.3.1).
- The DALib, CCIW 2024 and RawFooT websites (pages under /minisites/), kept in the form they had on the previous website of the laboratory, have text with insufficient colour contrast, links distinguished from the surrounding text only by colour, and links made of an icon without a text alternative (success criteria 1.4.1, 1.4.3, 2.4.4 and 4.1.2).

(c) The content is not within the scope of the applicable legislation:

- PDF files of publications published before 23 September 2018 (office file formats, Article 1(4)(a) of Directive (EU) 2016/2102).
- The interactive map on the "Get in touch" page, provided by OpenStreetMap (online maps, Article 1(4)(d) of Directive (EU) 2016/2102).

Accessible alternatives: the address of the laboratory and a link to directions are given as text on the "Get in touch" page.
An accessible version of a publication can be requested using the contact details below.

## Preparation of this accessibility statement

This statement was prepared on {{ page.prepared | date: "%-d %B %Y" }}.

The statement is based on a self-assessment carried out by the laboratory: automated testing of the main page types with axe-core
(WCAG 2.1 A and AA rules), and manual checks of keyboard navigation and of the page layout at 400% zoom.
{% if page.agid_statement_url %}

The accessibility statement for this website published by the University on the AgID platform is available at
[{{ page.agid_statement_url }}]({{ page.agid_statement_url }}).
{% endif %}

## Feedback and contact information

To report accessibility problems on this website, or to request information and content excluded from the scope of the Directive,
write to <a href="mailto:accessibilita@unimib.it">accessibilita@unimib.it</a>, indicating the address (URL) of the page concerned.

## Enforcement procedure

In case of an unsatisfactory response, or of no response within 30 days of the notification or request, users can report the matter to the
[Difensore civico per il digitale](https://www.agid.gov.it/it/agenzia/difensore-civico-il-digitale) (Digital Ombudsman) at the Agenzia per
l'Italia Digitale (AgID), pursuant to Article 3-quinquies, paragraph 3, of Law 4/2004.
