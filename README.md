# Introduction
This is a UQCS 2025 Hackathon mini-project, a terminal program called "When It's Due" that allows UQ students to automatically add their assignment deadlines to their Google Calendar.

# Note
This was made to work during Semester 2 2025, and so the links may break after this semester ends. I do plan to polish up this project and possibly make it a website for easier access.

# How It Works
The program takes in a course code from the user and navigates to the intended ECP (electronic course profile) and scrapes and assessment information in the format "DD/MM/YYYY HH:MM am/pm". The deadlines are added to the user's Google Calendar (meaning it requires them to login with their Google account) in the form of Tasks.

# How to use
This program depends on the use of a Google API key (which I obviously have not provided here). You can download this code and make a `credentials.json` file to store the API info (which you will have to set up yourself). There is **commented out** code that stores credentials to our device to reuse in future reruns of the program should you wish to make use of.
