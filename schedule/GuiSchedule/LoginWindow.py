from time import sleep
from tkinter import Tk, ttk, StringVar

import mysql.connector

from .GuiHelpers import display_error_message
from ..Schedule.database import PonyDatabaseConnection as PonyDatabaseConnection
from TestsAndExamples.model_unit_tests import HOST, DB_NAME, PROVIDER
from .ApplicationSelector import ApplicationSelector


class LoginWindow:
    """Class representing the login window of the application.

    Allows the user to login by entering their username and password. If both are valid, window
    will establish connection to remote database and take user to rest of app."""

    def __init__(self, parent: Tk):
        """Creates a new login window.

        notebook: TK = The root element that is the notebook of this LoginWindow."""
        self.parent = parent
        self.frame = self._setup_frame()
        self._setup_interface()

    def _setup_frame(self):
        frame = ttk.Frame(self.parent, padding=30)
        frame.grid()
        return frame

    def _setup_interface(self):
        ttk.Label(self.frame, text="Please login to access the scheduler.").grid(column=1, row=0)
        ttk.Label(self.frame, text="Username").grid(column=0, row=1)
        ttk.Label(self.frame, text="Password").grid(column=0, row=2)
        username_input = StringVar()
        password_input = StringVar()
        self.username_entry = ttk.Entry(self.frame, textvariable=username_input)
        self.username_entry.grid(column=1, row=1, columnspan=2)
        self.password_entry = ttk.Entry(self.frame, textvariable=password_input, show="*")
        self.password_entry.grid(column=1, row=2, columnspan=2)
        self.login_btn = ttk.Button(self.frame, text="Login", command=self._verify_login)
        self.login_btn.grid(column=1, row=3, columnspan=1)
        self.__status_var = StringVar()
        self.status_bar = ttk.Label(self.frame, textvariable=self.__status_var)
        self.status_bar.grid(column=0, row=5, columnspan=3)

    def _verify_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if len(username) == 0 or len(password) == 0:
            display_error_message("Username and password are required.")
            return
        try:
            self.__status_var.set("Connecting...")
            self.parent.update()
            # Attempt to connect to the database using these credentials.
            db = PonyDatabaseConnection.define_database(host=HOST, db=DB_NAME, user=username,
                                                        passwd=password, provider=PROVIDER)
            # Display a success message. Give the user a chance to read it before it disappears.
            self.__status_var.set("Connection successful.")
            self.parent.update()
            sleep(2)
            # If successful, make the LoginWindow's notebook disappear. We don't want the window
            # hanging around as a distraction.
            self.parent.withdraw()
            ApplicationSelector(self.parent, db)
            # Then display the scenario selector window.
            #ScenarioSelector(self.notebook, db)
        except mysql.connector.DatabaseError as err:
            display_error_message(str(err))
        except TypeError as err:
            display_error_message(str(err))
        except mysql.connector.InterfaceError as err:
            display_error_message(str(err))
