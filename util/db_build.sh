docker exec books_db /usr/bin/pg_dump -U picket books --file="/tmp/books.sql" --column-inserts
docker cp books_db:/tmp/books.sql ../etc/db/