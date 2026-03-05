---
layout: default
title: Blog
description: "Posts on SEBE, automation and fiscal policy"
---

<h1 style="font-family: var(--serif); font-size: 2rem; font-weight: 700; margin-bottom: 2rem;">Blog</h1>

<ul class="post-list">
{% for post in site.posts %}
  <li>
    <time datetime="{{ post.date | date_to_xmlschema }}">{{ post.date | date: "%e %B %Y" }}</time>
    <br>
    <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
    {% if post.description %}<p>{{ post.description }}</p>{% endif %}
  </li>
{% endfor %}
</ul>
