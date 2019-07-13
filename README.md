# The Book Stop

#### Site Address: 

-----

## Table of Contents

1. [Overview](#overview)

2. [UX Design Procedure](#ux)
    - [Strategy Plane](#strategy-plane)
    - [Scope Plane](#scope-plane)

3. [Features](#features)
    - [Existing Features](#existing-features)
    
4. [Technologies Used](#technologies-used)

5. [Testing](#testing)

6. [Deployment](#deployment)

7. [Credits](#credits)

-----

## Overview

This is a data-driven web application called 'The Book Stop' that acts like a book library for users. Each user creates
a profile then can insert and remove books.

-----


## UX

## Strategy Plane

The inspiration for this project came from <a href="https://ourworldindata.org/natural-disasters"> Our World In Data </a> they had a vast amount
of dashboards but I decided to use the Natural Disasters database from <a href="https://www.emdat.be/"> The International Disaster Database</a>.

This Interactive Data Dashboard was built to display and visualise data for the end user to interact with. There are charts to further
improve their knowledge on the effects of disasters. This site was mainly itended for students, for educational purposes or
people genrally interested in this topic.

## Scope Plane

Taking into account that that users will visit my site to look specifically on visual data I want the main attention
focusing on the graphs themselves. Therefore, little content as possible is required to suffice the goal.


## Structure Plane

Before I started my project I created a mockup using Adobe XD (image below). I understood that this was the foundation of my
site as other ideas would come to mind when progressing with the project.

<img src="assets/img/mockup-page1.jpg" alt="Mockup Design"/>
<br>

This is the overall structure that I wanted, as the content is minimal with only the chart description and charts availble for the user to look at. Also, I want 
padding around each peice of content to create more of a spacious effect so the user isn't overwhemled with infomation or content.

## Interaction Design

Apart from the interaction with each chart, the menu situated top left was implemented to help catergorise the charts but initally I had planned to add a link to each graph on
the page.

For Example, below you can see when I change the first drop downmenu to a specific type of disaster the charts will change accordingly.

<img src="assets/img/menu-func.jpg" alt="Menu in initial state"/>
<img src="assets/img/menu-func2.jpg" alt="Menu in initial state"/>
 

## Surface Plane

The typogragphy was found on google fonts and I chose the font <a href="https://fonts.google.com/specimen/Rajdhani">Rajdhani</a> as it
stood out to me the most, it has a nice futuristic effect with soft-rounded edges.

The color scheme I chose for this project is seen below:

 - #cedb9c
 - #393b79

<img src="assets/img/color.png" alt="color scheme"/>

### Development

#### IDE
Cloud9 IDE was the Integrated development enviroment for this website.

#### Version Control
Git Hub was the version control station for this website which was used to manage and store versions of the source code.

-----
## Features


### Existing Features

 1. Single Page Website - This was used to ensure a better user experience.
 2. Modal - To introduce the website's intentions and functionality.
 2. Charts - To view a barchart, linechart and pie chart. Additionally, the feature to scroll and zoom into the chart to render more specific data.
 3. Menu - To catergorise the charts into, type of diaster or country and also to reset each sssssscharts.

-----

## Technologies Used


### HTML
To provide the structure of the webiste.

### CSS
To make the website look better visually.

### Javascript


### Jquery
Entirely to enable bootstrap functions with navbar expanding

### Bootstrap (https://getbootstrap.com/)
To use their responsive grid system and also their sass variables where certain variables have an established design to it already.

### DC (https://dc-js.github.io/dc.js/)
To display interactive charts from datasets.
 
### D3 (https://d3js.org/)
To render each graph

### Crossfilter (http://crossfilter.github.io/crossfilter/)
To create an interaction with all graphs in the dataset.
 

-----

## Testing

I tested this project manually and also with the use of Jasmine.js.

## Manual Testing

1. Both Modal "Close" Button and "X" Button successfully close the modal.

2. The "Reset all Data" Button successfully resets all data on each charts.

3. Both Drop Down Menu's successfully change all graphs accordingly.

4. Each Chart Interacts with each other successfully.

I also used Google Developer Tools to simulate a mobile to help me see the responsiveness. I discovered the charts we not rendering proper on small device
so I introduced a horizontal scroll to help mobile users to view my charts.

There are zero errors in the published console log.

## Jasmine Testing

I understood that d3 did not need to be tested as the developers test it already so my main focus with
jasmine was to test if the methods function successfully called the fucntions to render the charts.

<img src="assets/img/jstest.png" alt="Jasmine Test Screenshot"/>


-----

## Deployment

The version control and deployment of this project is based on Git Hub. After every session I push the local code within Cloud9 into my GIT HUB repository.


This is my procedure: 

After I have finished working on the files in my IDE I would open the terminal and do the following commands to push the updated files across to the repository on GitHub

``` $git add . ```

```$git commit -m "describe the stage I am at"```

```git push -u origin master```

I would now ```$git status``` to check if everything is finished and then look at the repository to see there aswell.

-----

## Credits
### Content
All data came from https://emdat.be.
All Icons came from https://fontawesome.com/.
The main font was found at https://fonts.google.com/specimen/Rajdhani.
### Media




