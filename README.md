# PERSONAL BUDGET CONTROL
#### Video Demo: https://youtu.be/BtaIH22RsXQ
#### Description: Web application to control your personal budget using Flask, JavaScript, JQuery, SQL.
#### This is a responsive dashboard to control your personal budget.

### Spending
#### In here the user can see his/hers spending by year or by category in the selected year.
#### Right below the dashboard there is the spending list, where it shows all the user's spendings ordered by date.

### Items
#### In this tab you can add items that make up the selected spending.
#### In the items list, the user can edit or remove any item

### Categories
#### Here the user can add new categories and subcategories or edit or remove current ones.

### Further Details:
##### I based some of this project code on pset8/finance and changed the style using some bootstrap examples (dashboard and login)
##### I also tryed to make the application best friendly user possible with several dynamic forms and tables using JQuery and Javascript (thanks to stackoverflow and w3schools), and lots of AJAX operations. Examples:
###### 1 - Show/Hide buttons in all tabs;
###### 2 - Edit form. Previously I was creating this form after the document was ready but I was unable to submit for reasons I dont fully understand yet. So generetad the form with the original document but with style="display:none". The edit button changes the display status to table-row and insert the form after the selected object via JQuery.
###### 3 - Subcategory Form. I did this as I did the edit form.

##### For the charts in the dashboard I used Chartjs. 

##### In the add items' form of items.html I was using several select, but I decided to change that to an input type text so the user has more freedom. If you insert a new item that is not previously registered in the database, back-end will automaticaly register it for the user, adding new ID to it. The same apllies to subcategory.

