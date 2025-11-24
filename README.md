# la-dining-relational-data-system

# How to run project

## 1) Requirements
**Required datafiles:**  
"Healthgrade.csv"  
"Ratings_Type_Link.csv"  

**Required py files:**  
app.py  
table.py  
parse.py  
projection.py  
filtering.py  
group_aggregation.py  
innerJoin.py  

**Required html files:**  
index - Copy.html  
index.html  
base.html  

## 2) Change Directory  
Navigate directory to the extracted zip containing all required files in terminal

## 3) Start the App  
In terminal, run python app.py. Then open http created (Ex: Running on http://127.0.0.1:5000)

## 4) Select the Dataset  
Under the dropdown, there will be three options. Ratings, Healthgrade, and combined (joined between Ratings and Healthgrade on Restaurant Name).  
**As a test case,** choose Ratings dataset.

## 5) Select the Filter  
Next choose a column you would like to filter down on. Note: only columns containing numeric values can use <, >, <=, >= operations. Otherwise, equals will be used.  
**As a test case,** choose Rating column. Choose Operation >= and set Value to 4.8. Then click Run Query.

## 6) Select Desired Projection Columns  
Next select which columns you would like to see. Otherwise, keep all columns unselected to project all columns.   
**As a test case,** choose projection columns: Restaurant Name, Cuisine Type, Neighborhood, Rating. Note: Must click Run Query to update displayed results.

## 7) Group By and Aggregation  
Next select which column you would like to group values by. Then select which column you would like to aggregate on. Note: must aggregate on a numerical values column.  
**As a test case,** choose Group By: Cuising Type, Aggregate: Ratings, Aggregate Function: Average. Since we already filtered on values with rating >= 4.8, we should notice that all averages are >= 4.8 as well.

## 8) Changing Datasets  
Steps 4 - 7 cover how to effectively utilize our app. If you would like to change datasets, first change the dataset and then run query. This will reset all column dropdowns to update to the current datasets columns.  
**As a test case,** switch from Ratings dataset to Healthgrade or Combined. Click Run Query and then repeat steps 4 - 7 as desired.

## 9) Quiting App  
In Terminal, click CTRL + C to quit and end running the app
