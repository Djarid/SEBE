---
layout: default
title: Blog
---

# Blog

<ul class="post-list">
{% for post in site.posts %}
  <li>
    <time datetime="{{ post.date | date_to_xmlschema }}">{{ post.date | date: "%e %b %Y" }}</time>
    <br>
    <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
    {% if post.description %}<p>{{ post.description }}</p>{% endif %}
  </li>
{% endfor %}
</ul>
