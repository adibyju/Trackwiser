# Trackwiser

Tool to log day-to-day software tasks

I have used sqlite3 for the backend database. Commands and arguments are being passed onto the python file using the batch file.

To use the tool:

- Add to PATH the directory where the files are stored
- Change \<path of log.py> accordingly in log.bat file
- Now you can use the tool from any directory

Commands:

1. **add:** &nbsp;&nbsp; to add a log entry into the database

```
log add "Completed Codeforces Round 921"
```

1. **fetch:** &nbsp;&nbsp; to fetch a log entry of the specified date from the database

```
log fetch "01/02/2024"
```

1. **list:** &nbsp;&nbsp; to list log records from the past specified number of days

```
log list 3
```

1. **range:** &nbsp;&nbsp; to list records from a specified range of past days

```
log range "07/01/2024" "01/02/2024"
```

1. **modify:** &nbsp;&nbsp; to modify a previous log entry

```
log modify "23/01/2024" "Created login page of chat application"
```

1. **del:** &nbsp;&nbsp; to delete a previous log entry

```
log del "02/01/2024"
```
