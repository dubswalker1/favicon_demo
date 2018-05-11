# favicon_demo
A basic django Favicon Finder app.  
Launch the server from the root directory via:  
python manage.py runserver
Launch the client via http://127.0.0.1:8000/faviconfinder

Unfortunately I was unable to get it deployed to a host yet, so the DB is not fully populated. It has an admin functionality to seed the DB via downloaded zip.

Launch the admin client via http://127.0.0.1:8000/admin
login: walkerb
password: !!Password!!

The Admin DB Seeding functionality is possible to use but is quite time consuming and a bit hacky: if you select any User or Favicon Object (at least one much be selected) and choose the "Seed DB" action,
it will kick off the DB download and seeding operation.
