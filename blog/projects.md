---
title: 프로젝트
permalink: /projects/
---
<header class="page-heading"><p class="eyebrow">SELECTED WORK</p><h1>프로젝트</h1><p>문제를 정의하고, 선택을 비교하고, 해결한 과정을 정리합니다.</p></header>
{% if site.data.projects.size > 0 %}{% for project in site.data.projects %}<article class="project-entry"><h2><a href="{{ project.url }}">{{ project.title | escape }} ↗</a></h2><p>{{ project.problem | escape }}</p>{% if project.outcome %}<p>{{ project.outcome | escape }}</p>{% endif %}</article>{% endfor %}{% else %}<p class="empty-note">프로젝트 기록은 추후 추가합니다.</p>{% endif %}
{% assign records = site.posts | where: 'content_type', 'project' %}{% if records.size > 0 %}<section class="home-section"><h2>프로젝트 개발 기록</h2><div class="post-list">{% for post in records %}{% include post-row.html post=post %}{% endfor %}</div></section>{% endif %}
