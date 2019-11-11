# Electricity Consumption Web Application

## Instructions

### In Docker
You need to have docker-compose installed in order to proceed  

Run:  
`$ make build && make run`  


### Locally

Install dependencies:  
`$ make install`  

Run the application:  
`$ make run`


Check make options for testing, CI, etc


#### Summary

This task is designed to be fun ( i hope ), educational and help ussess few areas of engineering. I do understand that people are busy and that's why I will leave it to you how much you want to work on it before you will send task. I am also open for alterations if you will find something that you would like to play around - but in this case please come back to me and ask. 

Any feedback is welcome. 

Write simple web application using ( preferably ) Python
Deliver solution as Github repository 

### Part 1 - Ranking

The application should display ranking 
- top 10 countries - consumption of energy ( per capita ) 
- top 10 and bottom 10 countries - access to electricity 
- in both examples make sure the country you are browsing from is added if it is not in the list

### Part 2 - REST API

Design and implement restful API that will take parameter country and return those rankings as a result. 

### Customisations : 

A) Display graph of electricity consumption globally compared to country you are browsing from. (x axis will be a time).  
B) Allow user to change country that calculation are made against 
C) Dockerise APP



## Some resources to help: 

[Worldbank API - List of countries](https://api.worldbank.org/v2/country/all?format=json) 

[Worldbank API - Access to Electricity](https://api.worldbank.org/v2/country/all/indicator/1.1_ACCESS.ELECTRICITY.TOT?format=json)

[Worldbank API - Electricity consumption](https://api.worldbank.org/v2/country/all/indicator/1.1_TOTAL.FINAL.ENERGY.CONSUM?format=json)

[Worldbank API - Population Total](http://api.worldbank.org/v2/en/indicator/SP.POP.TOTL?downloadformat=csv)
