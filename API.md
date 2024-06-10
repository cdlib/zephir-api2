
# Zephir API Documentation
[http://localhost/documentation](http://localhost/documentation)

### Purpose
The Zephir Item API provides an access point to the item-level metadata record for all 
items submitted to Zephir.

### Content Negotiation
The API response body content (records, error messages) are available in XML and JSON. 
XML is the default content type, but can be explicitly requested. Content type
preferences can be made with the following methods.

* Content negotiation with the HTTP Accept Header (__preferred__)

> [http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.1](http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.1)

* Explicit extension (.xml, .json) to the API call (debug option)

> Example: [http://localhost/ping.json](http://localhost/ping.json))  

>     {"status":200, "message":"Success"}

> Example [http://localhost/item/mdp.39015012078393.json](http://localhost/item/mdp.39015012078393.json)

>     {"leader":"00925nam a22003011  4500","fields":[{"001":"mdp.39015012078393"},...

### API Calls

### System

__GET /ping__  
[http://localhost/ping](http://localhost/ping)

    <response>
    <status>200</status>
    <message>Success</message>
    </response>

__Response Content Type__  
'text/xml' *(default)*  
'application/json'  

__Responses__  
*Success*  
Condition: Request was successful.  
Status: 200  
Content: 'Success' Message  

*Failure*  
Condition: An error occurred while processing this request.  
Status: 500  
Content: 'Failure' Message 

### Item

__GET /item/{htid}__  
[http://localhost/item/mdp.39015012078393](http://localhost/item/mdp.39015012078393)

    <record xmlns="http://www.loc.gov/MARC21/slim">
    <leader>00925nam a22003011 4500</leader>
    <controlfield tag="001">mdp.39015012078393</controlfield>
    ...

__Implementation Notes__  
Returns the item-level MARC record.

__Response Content Type__  
'text/xml' *(default)*  
'application/json'  

__Responses__  
*Success*  
Condition: Record is found and successfully returned.  
Status: 200  
Content: MARC Record

*Not Found*  
Condition: Record is not found.  
Status: 404  
Content: 'Not Found' Message

*Unacceptable Parameter*  
Condition: The HTID format used was unacceptable.  
Status: 422  
Content: 'Unacceptable Parameter' Message

*Failure*  
Condition: An error occurred while processing this request.  
Status: 500   
Content: 'Failure' Message 