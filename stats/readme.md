# FOIA Machine Data Record Layout

All dates/times are UTC standard. 

Note: All data is input by users as part of open records requests. FOIA Machine attempts to verify data, but does not formally audit the data. Users often send requests by email, but can also send requests out of the system and use FOIA Machine to track requests. In such cases, all information is dependent on users to update.

### agencies
* id - Unique ID for the agency.
* government_id - ID of associated government for the agency, affects which open records law is applicable. (Joins to governments table.)
* name - Name of agency.
* slug - Used to create the unique URL for the agency-s web page.
* created - Date/Time agency was created in database.
* contacts - Number of unique contacts associated with each agency.

### contacts
* id - Unique ID for the contact.
* agency_id - ID of associated agency for the contact. (Joins to agency table.)
* first_name  - Contact-s first name. 
* last_name  - Contact-s last name. 
* created - Date/Time contact was created in database.
* address - Contact address.
* phone - Contact-s phone number.
* emails - Contact-s email. Multiple emails separated by semicolon. 
### governements
* id - Unique ID for the government. 
* name - Name of the government.
* slug - Used to create the unique URL for the government's web page.
* created - Date government was created in database.
* agencies - Number of associated agencies connected to the government.

### requests
* id - Unique ID for the request.
* agency_id  - Associated agency ID. (Joins to agencies table.)
* status  - Status of the request, includes following options:
  * New (Unsent) and  Incomplete - Both indicate user hasn-t sent the request yet.
  * Filed (Request sent) - Request sent, but not response indicated. 
  * Response received (but not complete) 
  * Partially fulfilled 
  * Fulfilled
  * Denied
  * Deleted - Request deleted by user.
* created  - Date the request was created in the system. Not necessarily when the request was sent to the agency. 
* sent  - Date/Time the request was sent to agency. 
* due_date  -  Date the agency is supposed to respond. _Note: this auto-fills in based on statute when the request is initially sent. After that it is dependent on the user to update this._
* fullfilled_date  - Date the request was fulfilled. (Users fill this in. it-s possible for a request to be listed as -fulfilled- but not have a fulfilled date if the user didn-t update the information.) 
* private - T/F flag on whether the user is keeping the request.
* num_messages  - Number of message sent between requester and agency, includes personal notes request can add.
* contacts  - Number of contacts initial request was sent to.