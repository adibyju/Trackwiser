#!/usr/bin/env python3

# Trackwiser Log Tool
# Tool to log day-to-day software tasks
# Author: Aditya Byju
# Date: 01-02-2024

import argparse
import sqlite3
import os
import time
import json
import datetime


class Trackwiser:
    """Tool to log day-to-day software tasks."""

    def __init__(self):
        # Initialize the parser with a description
        self.parser = argparse.ArgumentParser(
            prog="log", description="Trackwiser Log Tool"
        )
        self.subparsers = self.parser.add_subparsers(dest="command", help="Description")
        self.setup_subparsers()

        curr_dir_path = os.path.dirname(os.path.realpath(__file__))

        self.con = sqlite3.connect(curr_dir_path + "\log_data.db")
        self.cur = self.con.cursor()

        self.cur.execute("CREATE TABLE IF NOT EXISTS log(date, entry)")

        # res = self.cur.execute("SELECT name FROM sqlite_master")
        # print(res.fetchone())

    def setup_subparsers(self):
        """Sets up the subparsers for different log commands."""
        # Sub-parser for the 'add' command
        parser_add = self.subparsers.add_parser("add", help="Add a new log entry")
        parser_add.add_argument("entry", type=str, help="The log entry text")

        # Sub-parser for the 'fetch' command
        parser_fetch = self.subparsers.add_parser(
            "fetch", help="Fetch a previous log entry for the specified date"
        )
        parser_fetch.add_argument(
            "date", type=str, help="The log entry date in the format: 'DD-MM-YY'"
        )

        # Sub-parser for the 'list' command
        parser_list = self.subparsers.add_parser(
            "list", help="List previous log entries for a specified number of days"
        )
        parser_list.add_argument("number", type=str, help="Required number of days")

        # Sub-parser for the 'range' command
        parser_range = self.subparsers.add_parser(
            "range", help="Fetch previous log entries for a range of days"
        )
        parser_range.add_argument(
            "initial_date", type=str, help="The initial date in the format: 'DD-MM-YY'"
        )
        parser_range.add_argument(
            "final_date", type=str, help="The final date in the format: 'DD-MM-YY'"
        )

        # Sub-parser for the 'modify' command
        parser_modify = self.subparsers.add_parser(
            "modify", help="List previous log entries for a specified number of days"
        )
        parser_modify.add_argument(
            "date",
            type=str,
            help="The log entry date to modify in the format: 'DD-MM-YY'",
        )
        parser_modify.add_argument("entry", type=str, help="The log entry text")

        # Sub-parser for the 'del' command
        parser_delete = self.subparsers.add_parser(
            "del", help="Delete a previous log entry"
        )
        parser_delete.add_argument(
            "date",
            type=str,
            help="The log entry date to delete in the format: 'DD-MM-YY'",
        )

    def run(self):
        """Runs the command-line argument parser and handles the user input."""
        args = self.parser.parse_args()

        # Handling different commands
        if args.command == "add":
            self.handle_add(args.entry)
        elif args.command == "fetch":
            self.handle_fetch(args.date)
        elif args.command == "list":
            self.handle_list(args.number)
        elif args.command == "range":
            self.handle_range(args.initial_date, args.final_date)
        elif args.command == "modify":
            self.handle_modify(args.date, args.entry)
        elif args.command == "del":
            self.handle_delete(args.date)
        else:
            self.parser.print_help()

    def handle_add(self, entry):
        """Handles the 'add' command."""
        date = time.strftime("%d/%m/%Y")

        self.cur.execute("SELECT * FROM log WHERE date = ?", (date,))
        record = self.cur.fetchone()

        if record:
            temp = json.loads(record[1])
            temp.append(entry)
            updated_entry = json.dumps(temp)
            self.cur.execute(
                "UPDATE log SET entry = ? WHERE date = ?", (updated_entry, date)
            )
        else:
            updated_entry = json.dumps([entry])
            self.cur.execute(
                "INSERT INTO log (date, entry) VALUES (?, ?)", (date, updated_entry)
            )
        self.con.commit()
        self.con.close()
        print("Entry added...")

    def process_date(self, date):
        """Function to process the date into the required format"""
        date = date.replace("-", "/")
        date = date.replace(",", "/")
        date = date.replace(".", "/")
        date = date.replace(" ", "")

        if len(date) > 10 or date.count("/") != 2:
            return 0
        for x in date:
            if x not in "0123456789/":
                return 0

        try:
            dateObject = datetime.datetime.strptime(date, "%d/%m/%Y")
            date = dateObject.strftime("%d/%m/%Y")
        except ValueError:
            try:
                dateObject = datetime.datetime.strptime(date, "%d/%m/%y")
                date = dateObject.strftime("%d/%m/%Y")
            except:
                return 0

        return date

    def handle_fetch(self, date):
        """Handles the 'fetch' command."""
        date = self.process_date(date)
        if date:
            self.cur.execute("SELECT * FROM log WHERE date = ?", (date,))
            record = self.cur.fetchone()
            if record:
                print(f"Entry for the date {date} is:") if len(
                    record[1]
                ) == 1 else print(f"Entries for the date {date} are:")
                temp = json.loads(record[1])
                for x in temp:
                    print(f"> {x}")
            else:
                self.con.commit()
                self.con.close()
                print("Entry not found!")
                return
            self.con.commit()
            self.con.close()
        else:
            print("Invalid date format!")

    def handle_list(self, number):
        """Handles the 'list' command."""
        final_date = time.strftime("%d/%m/%Y")
        final_date_object = datetime.datetime.strptime(final_date, "%d/%m/%Y")
        initial_date_object = final_date_object - datetime.timedelta(
            days=int(number) - 1
        )
        initial_date = initial_date_object.strftime("%d/%m/%Y")
        self.handle_range(initial_date, final_date)

    def handle_range(self, initial_date, final_date):
        """Handles the 'range' command."""
        initial_date = self.process_date(initial_date)
        final_date = self.process_date(final_date)

        if not initial_date or not final_date:
            print("Invalid date format!")
            return

        initial_date = datetime.datetime.strptime(initial_date, "%d/%m/%Y")
        final_date = datetime.datetime.strptime(final_date, "%d/%m/%Y")

        curr_date = initial_date
        while curr_date <= final_date:
            date = curr_date.strftime("%d/%m/%Y")
            self.cur.execute("SELECT * FROM log WHERE date = ?", (date,))
            record = self.cur.fetchone()
            if record:
                print(f"Entry for the date {date} is:") if len(
                    record[1]
                ) == 1 else print(f"Entries for the date {date} are:")
                temp = json.loads(record[1])
                for x in temp:
                    print(f"> {x}")
            else:
                print(f"Entry not found for {date}.")
            curr_date += datetime.timedelta(days=1)

        self.con.commit()
        self.con.close()

    def handle_modify(self, date, entry):
        """Handles the 'modify' command."""
        date = self.process_date(date)

        if not date:
            print("Invalid date format!")
            return

        self.cur.execute("SELECT * FROM log WHERE date = ?", (date,))
        record = self.cur.fetchone()

        if record:
            temp = json.loads(record[1])
            temp.append(entry)
            updated_entry = json.dumps(temp)
            self.cur.execute(
                "UPDATE log SET entry = ? WHERE date = ?", (updated_entry, date)
            )
        else:
            updated_entry = json.dumps([entry])
            self.cur.execute(
                "INSERT INTO log (date, entry) VALUES (?, ?)", (date, updated_entry)
            )
        self.con.commit()
        self.con.close()
        print("Entry modified..")

    def handle_delete(self, date):
        """Handles the 'delete' command."""
        date = self.process_date(date)
        if date:
            self.cur.execute("SELECT * FROM log WHERE date = ?", (date,))
            record = self.cur.fetchone()
            if record:
                self.cur.execute("DELETE FROM log WHERE date = ?", (date,))
            else:
                self.con.commit()
                self.con.close()
                print("Entry not found!")
                return
            self.con.commit()
            self.con.close()
            print("Entry deleted...")
        else:
            print("Invalid date format!")


if __name__ == "__main__":
    try:
        trackwiser = Trackwiser()
        trackwiser.run()
    except Exception as e:
        print(f"Error: {e}")
