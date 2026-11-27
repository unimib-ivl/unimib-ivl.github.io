---
# Moved from the old website (www.ivl.disco.unimib.it/activities/progetto-e4s-energy-for-safety/, which now redirects
# here, see _data/redirects.yml). Text translated from the Italian of the old page. Period from the University's list of
# research projects (the old page said "active since 4 January 2017"): to check.
# Field descriptions: see the top of _projects/onfoods.md.
layout: ivl-project
title: E4S – Energy for Safety
description: Integrated system for personal safety and energy saving in home and building automation, funded by Regione Lombardia under the "Smart Living" call.
img: assets/img/ivl/projects/e4s-regione-lombardia.jpg
img_alt: "Regione Lombardia"
img_in_aside: false # the logo is shown above the text instead
order: 5
period: 2018 – 2019
funding: >-
  Regione Lombardia, "Smart Living" call.
participants:
  - Raimondo Schettini
  - Gianluigi Ciocca
  - Simone Bianco
  - Paolo Napoletano
publication_tag: e4s
---

<img class="ivl-project-logo" src="{{ '/assets/img/ivl/projects/e4s-regione-lombardia.jpg' | relative_url }}" alt="Regione Lombardia" width="244" height="134">

**E4S – Energy for Safety**: integrated system for personal safety and energy saving in Home & Building Automation applications, funded by Regione Lombardia under the "Smart Living" call.

The goal of E4S was to develop a distributed platform of hardware and software products and systems combining energy saving with solutions for the safety and well-being of users in private (Home Automation), public and professional (Building Automation) environments.

The Bicocca unit acted as advisor in defining the final specifications of the platform and in identifying the image processing, audio processing and machine learning algorithms. Above all, it compared traditional algorithms with algorithms based on neural networks, assessing the computing power they require and identifying optimisation strategies.

For example, two hardware platforms were compared:

1. a workstation with an Intel Core i7-7700 CPU at 3.60 GHz, 16 GB of DDR4 RAM at 2400 MHz and an NVIDIA Titan X Pascal GPU with 3840 CUDA cores (a high-end consumer GPU), running Ubuntu 16.04;
2. an NVIDIA Jetson TX1 board with a 64-bit ARM A57 CPU at 2 GHz, 4 GB of LPDDR4 memory at 1600 MHz and an NVIDIA Maxwell GPU with 256 CUDA cores, with the JetPack 2.3 SDK.

On these platforms we measured the computational complexity of the main state-of-the-art deep neural networks (DNNs) for image recognition. The figure shows the Top-1 accuracy against the number of images processed per second (batch size 1) on the Titan Xp (a) and on the Jetson TX1 (b).

<img src="{{ '/wp-content/uploads/2020/11/fig3.png' | relative_url }}" alt="Top-1 accuracy against images processed per second for state-of-the-art deep neural networks, on the Titan Xp (a) and on the Jetson TX1 (b)" width="954" height="256">

These results show that almost all neural models reach real-time performance or better on a high-end GPU, while only some of them do so on an embedded system. Even DNNs with a very low model complexity need at least about 0.6 GB of GPU memory.

More details are given in the publication below.
