{% extends "base.html" %}
{% load cms_tags %}

{% block title %}Rules{% endblock title %}

{% block content %}
    <table id="rules_list" class="list list-rules">
        {% for player in objects %}
        <tr>
            <td>{{ player }}</td>
            <td>Blah table</td>
        </tr>
        {% endfor %}
    </table>
This is where the player stuff will go.
{% endblock content %}