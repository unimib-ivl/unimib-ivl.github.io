---
layout: page
title: Privacy
permalink: /privacy/
description: Information on the processing of personal data of users of this website.
nav: false
# Edit these two lines if the site moves to another host (e.g. GitHub Pages: "GitHub, Inc. (USA)").
hosting_provider: Netlify, Inc. (USA)
updated: 2026-11-25
---

{% comment %}
  Information notice under Art. 13 GDPR. Section order follows the notice the Garante per la protezione dei dati personali
  publishes for its own website. The Google Analytics paragraphs appear automatically when _config.yml sets
  analytics.google AND enable_cookie_consent: true; keep them in sync with the Google Analytics settings they describe.
  Review with the University DPO (rpd@unimib.it) before publishing.
{% endcomment %}
{% assign ga = false %}
{% if site.analytics.google and site.enable_cookie_consent %}{% assign ga = true %}{% endif %}

_Last updated: {{ page.updated | date: "%-d %B %Y" }}_

## Why we provide this information

This page describes how the personal data of users who consult the website of the Imaging and Vision Laboratory
({{ site.url | remove: 'https://' }}) are processed, pursuant to Article 13 of Regulation (EU) 2016/679 (General Data Protection Regulation, GDPR).
It applies only to this website and not to other websites that users may reach through its links.

## Data controller

The data controller is the University of Milano-Bicocca, Piazza dell'Ateneo Nuovo 1, 20126 Milano, Italy;
e-mail <a href="mailto:rettorato@unimib.it">rettorato@unimib.it</a>; certified e-mail (PEC) ateneo.bicocca@pec.unimib.it.

The Data Protection Officer can be contacted at <a href="mailto:rpd@unimib.it">rpd@unimib.it</a> (PEC rpd@pec.unimib.it).

## Legal basis for the processing

Personal data are processed for the performance of tasks carried out in the public interest by the University (Article 6(1)(e) GDPR),
including institutional communication about its research activities.
{%- if ga %}
Statistical cookies are used only with the consent of the user (Article 6(1)(a) GDPR and Article 122 of Legislative Decree 196/2003).
{%- endif %}

## Types of data processed and purposes of the processing

### Browsing data

The IT systems and software procedures used to operate this website acquire, during their normal operation, some personal data whose
transmission is implicit in the use of Internet communication protocols. This category includes the IP addresses or domain names of the
devices used to connect to the website, the addresses of the requested resources, the time of the request, the method used to submit it,
the size of the response, the code indicating the status of the response and other parameters relating to the user's operating system
and browser.

These data are recorded by the hosting provider, {{ page.hosting_provider }}, and are used only to deliver the website and to ensure its
security. They are retained for the period set out in the provider's privacy policy.

### Data provided by users

The website contains no forms. Personal data contained in e-mails that users send to the addresses published on the website are used
only to reply to them.

### Cookies and other tracking systems

{% if ga -%}
This website does not use profiling cookies.

A technical cookie (cc_cookie, duration 6 months) records the user's choice in the cookie banner. Without the user's consent, no other
cookies are set.

With the user's consent, given through the banner shown on the first visit, the website uses Google Analytics 4, provided by
Google Ireland Limited, to produce aggregate statistics on the use of the website (pages visited, referring page, approximate location,
device and browser type). The cookies used are \_ga and \_ga\_&lt;ID&gt; (duration up to 2 years). Google Analytics 4 does not store
IP addresses; data are retained by Google for 2 months, and Google signals and advertising features are disabled.
Consent can be withdrawn at any time through the "Cookie settings" link at the bottom of each page.
{%- else -%}
This website does not use cookies or other tracking systems and does not store any information on the user's device.
{%- endif %}

### Third-party content

Fonts and scripts are served by this website itself. The interactive map on the "Get in touch" page is provided by the
OpenStreetMap Foundation and is loaded only when the user requests it; OpenStreetMap then receives the user's IP address and processes it
under its own [privacy policy](https://osmfoundation.org/wiki/Privacy_Policy).

### Laboratory members

The names, roles, photographs, institutional contact details and publications of members and former members of the laboratory are published
as part of the University's institutional communication. Requests for their correction or removal can be sent to the laboratory
(see [Get in touch]({{ '/how-to-reach/' | relative_url }})).

## Data recipients

Browsing data are processed by the hosting provider, {{ page.hosting_provider }}, on behalf of the University.
{%- if ga %}
Statistical data are processed by Google Ireland Limited and may be transferred to Google LLC in the United States, which is certified under
the EU-U.S. Data Privacy Framework.
{%- endif %}
Where data are transferred outside the European Economic Area, the transfer takes place on the basis of an adequacy decision of the
European Commission or of standard contractual clauses (Articles 45 and 46 GDPR).

## Rights of data subjects

Users have the right to obtain from the University, where applicable, access to their personal data, their rectification or erasure,
the restriction of processing, or to object to the processing (Articles 15 to 22 GDPR). Requests can be sent to the Data Protection Officer
at <a href="mailto:rpd@unimib.it">rpd@unimib.it</a>.

## Right to lodge a complaint

Users who consider that the processing of their personal data infringes the GDPR have the right to lodge a complaint with the
[Garante per la protezione dei dati personali](https://www.garanteprivacy.it/) (Article 77 GDPR) or to take legal action (Article 79 GDPR).

The University's general privacy notices are available on the [University privacy page](https://www.unimib.it/privacy-cookie-policy).
