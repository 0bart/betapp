# betapp

# Production address: https://betapp.top or http://betapp.top

# About

Betapp is fully-automated platform for odds analysis.

Main features of betapp:

*  looking for future matches with odds and update them after finish
*  fixtures and results tables, with nested odds, result predictions and scores
*  interactive simulation scatter plot with some filter options

Future features:

*  extending database, new leagues
*  new simulation filtering options - league, season, club name, bookmaker etc.
*  ajax requests in tables pagination
*  docker-compose for run

# Current look&feel

## Welcome page
![aboutpage preview](/doc/screenshot_about.JPG)

## Tables
![tables preview](/doc/screenshot_tables.JPG)

## Simulation
![simulation preview](/doc/screenshot_simulation.JPG)

## Microservices
* scheduler: for periodically looking for future matches and update finished matches 
* mongo: for data storage
* flaskapp: backend routing and template engine
* dashapp: generates simulation scatter plots

## Technologies
* backend: Python3, Dash
* frontend: Bootstrap4, JS, React(in Dash), MathJax
* template engine: Jinja2
* storage: MongoDB
* development: Docker
