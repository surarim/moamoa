![Alt text](frumoa.png?raw=true "Title")
# moamoa
### Logs server collector on Python and PostgreSQL
### Version 0.32 (early development)
<hr>
The log collector consists of two components and works as follows: the irimoa.py process listens to the 514 UDP port and writes to the postgresql database, and the frumoa.py application provides web access to the database for search and monitoring tasks.
<br>
The journal collector has been tested and assembled on the following components:
<ul>
  <li>Python: 3.7.3</li>
  <li>psycopg2: 2.8</li>
  <li>PostgreSQL: 11.2 </li>
  <li>uwsgi: 2.0.18</li>
 </ul>
