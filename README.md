# ByteSniffer
The purpose of the project is to scan through large amounts of data and return only the desired information.
-The main objective is to take multiple files and pull everything you want into one location for easier access

Currently the project can sift through text files for desired words and return a dictionary "key, value" pair of "byte, sentence".
Update: June-2-2020
-Approximately doubled speed of last method
-Added functionality of saving to database;
--Will create database if none; currently saves to current working directory
--Will create tables if doesn't exist, then populate it

Future updates [pending]:
-Video search function
--Returning the area in a sequence of images where an object is located in bytes and timestamp

-Audio search function
--Assess audio files for specified sequences and return their locations in the file in bytes and timestamp

-Image search function
--Process an image to search through specified color channels for information or process the image entirely to return only desired image

