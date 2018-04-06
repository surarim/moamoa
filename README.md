![Alt text](frumoa.png?raw=true "Title")
# moamoa
### Logs server collector on Python and PostgreSQL
### Version 0.1 (early development)
<hr>
The log collector consists of two components and works as follows: the irimoa.py process listens to the 514 UDP port and writes to the postgresql database, and the frumoa application provides web access to the database for search and monitoring tasks.
<br>
The journal collector has been tested and assembled on the following components:
<ul>
  <li>PostgreSQL: 10.3 </li>
  <li>Python: 3.6.4</li>
  <li>psycopg2: 2.7.4</li>
  <li>Django: 2.0.3</li>
  <li>uwsgi: 2.0.17</li>
 </ul>
