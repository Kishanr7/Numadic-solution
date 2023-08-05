Step-by-step guide of running this solution:-

1. run the python script with any IDE.
2. Use postman or curl to send API request
   for Postman :-
3. Open Postman.
4. Choose the request type as POST.
5. Enter the URL: http://127.0.0.1:5000/generate_report.
6. Go to the "Body" tab and select "raw", then choose "JSON (application/json)" from the dropdown.
7. Enter the JSON data: {"start_time": 1527618419, "end_time": 1527618420}.
8. Click the "Send" button.

This will return a CSV file as an output to your postman.
