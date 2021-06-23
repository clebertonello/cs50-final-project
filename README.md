# BUDGET CONTROL
#### Video Demo: https://youtu.be/BtaIH22RsXQ
#### Description: Web application to control your personal budget using Flask, JavaScript, JQuery, SQL.
#### This is a responsive dashboard to control your personal budget.

## Web Application content:

#### The user must register in order to use this web application. Once registered, the user must login.
#### The user will be redirected to the main page (Spending tab). There are 3 different tabs:

### Spending
#### In here the user can see his/hers spending by year or by category in the selected year.
#### Right below the dashboard there is the spending list, where it shows all the user's spendings ordered by date.

### Items
#### In this tab you can add items that make up the selected spending.
#### In the items list, the user can edit or remove any item

### Categories
#### Here the user can add new categories and subcategories or edit or remove current ones.

## Further Details:
##### I based some of this project code on pset8/finance and changed the style using some bootstrap examples (dashboard and login)
##### I also tryed to make the application best friendly user possible with several dynamic forms and tables using JQuery and Javascript (thanks to stackoverflow and w3schools), and lots of AJAX operations. Examples:
###### 1 - Show/Hide buttons in all tabs;
###### 2 - Edit form. Previously I was creating this form after the document was ready but I was unable to submit for reasons I dont fully understand yet. So generetad the form with the original document but with style="display:none". The edit button changes the display status to table-row and insert the form after the selected object via JQuery.
###### 3 - Subcategory Form. I did this as I did the edit form.

##### For the charts in the dashboard I used Chartjs. The user can see them by month or by category for the selected year.
###### By month: all expenses are grouped and shown as total
###### By category: the user can see as a bar or donut chart.

##### In the add items' form of items.html I was using several select, but I decided to change that to an input type text so the user has more freedom. If you insert a new item that is not previously registered in the database, back-end will automaticaly register it for the user, adding new ID to it. The same apllies to subcategory.

##### When adding new categoreis, the server checks if typed ID or description already exists and alerts the user if it does exists, focusing that input and removing previous text.

##### When adding new items to the selected spending ID, the server will return with current current categories' subcategories and related items for autocomplete.

### Database:
##### Database stores users, items (produtos), categories (catgoria), items categories (produto_categoria), places (fornecedor), item bought (compra_produto) and spending (compras). For more information check script.sql.

### Plans:
##### My original plan for this web application was to make something similar to Excel's pivot tables and Power BI full of filters, but then it started to take too long. So I decided to stop in current stage (since its main features are in place) to submit it. 
