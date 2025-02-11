CREATE DATABASE Aerotaxi_DB

USE Aerotaxi_DB

CREATE TABLE Pilots_TB(
    Pilot_ID INT PRIMARY KEY NOT NULL IDENTITY (1000, 1),
    Pilot_Name VARCHAR(50),
    Pilot_Age SMALLINT,
    Pilot_BOO CHAR(4),
    Pilot_Rank VARCHAR(20),
    Pilot_Salary DECIMAL(9,2) CHECK (Pilot_Salary >= 0),
    Pilot_Experience INT CHECK (Pilot_Experience >= 0)
)

CREATE TABLE Attendant_TB(
    Attendant_ID INT PRIMARY KEY NOT NULL IDENTITY (2000, 1),
    Attendant_Name VARCHAR(50),
    Attendant_Age SMALLINT,
    Attendant_BOO CHAR(4),
    Attendant_Salary DECIMAL(9,2) CHECK (Attendant_Salary >= 0),
)

CREATE TABLE Mechanics_TB(
    Mechanics_ID INT PRIMARY KEY NOT NULL IDENTITY (3000, 1),
    Mechanics_Name VARCHAR(50),
    Mechanics_Age SMALLINT,
    Mechanics_BOO CHAR(4),
    Mechanics_Function VARCHAR(50),
    Mechanics_Salary DECIMAL(9,2) CHECK (Mechanics_Salary >= 0),
)

CREATE TABLE Routes_TB(
    Route_ID VARCHAR(10) PRIMARY KEY NOT NULL,
    Route_Origin CHAR(4),
    Route_Destination CHAR(4),
    Route_Alternate CHAR(4)
)

CREATE TABLE Aircraft_TB(
    Aircraft_ID VARCHAR(6) PRIMARY KEY NOT NULL,
    Aircraft_Model VARCHAR(20),
    Aircraft_Base CHAR(4),
    Aircraft_Type VARCHAR(20),
    Aircraft_Crew SMALLINT,
    Aircraft_MaxCap SMALLINT,
    Aircraft_FuelBurn DECIMAL(10,2),
    Aircraft_Status VARCHAR(50)
)

CREATE TABLE Serviced_Locations_TB(
    Airport_ID CHAR(4) PRIMARY KEY NOT NULL,
    Airport_Name VARCHAR(100),
    Airport_Loc VARCHAR(50)
)

CREATE TABLE Flights_TB(
    Flight_ID INT PRIMARY KEY NOT NULL IDENTITY (10000, 1),
    Flight_Route VARCHAR(10) FOREIGN KEY REFERENCES Routes_TB(Route_ID),
    Flight_Aircraft VARCHAR(6) FOREIGN KEY REFERENCES Aircraft_TB(Aircraft_ID),
    Flight_Departure TIME,
    Flight_Arrival TIME,
    Flight_Passengers SMALLINT
)

CREATE TABLE Flight_Crew(
    Flight_ID INT NOT NULL,
    Crew_ID INT NOT NULL
    FOREIGN KEY (Flight_ID) References Flights_TB
)

CREATE TABLE Aircraft_Position (
    Aircraft_ID VARCHAR(6) PRIMARY KEY,
    Current_Location CHAR(4) NOT NULL
    FOREIGN KEY (Aircraft_ID) References Aircraft_TB
    FOREIGN KEY (Current_Location) REFERENCES Serviced_Locations_TB
)

CREATE TABLE Crew_Position (
    Crew_ID INT PRIMARY KEY NOT NULL,
    Crew_Type VARCHAR(10) CHECK (Crew_Type IN ('Pilot', 'Attendant')),  -- Para saber se é piloto ou comissário
    Current_Location CHAR(4),  -- Base de operações ou localização atual
    FOREIGN KEY (Current_Location) REFERENCES Serviced_Locations_TB
)

ALTER TABLE Pilots_TB
ADD CONSTRAINT FK_Pilot_BOO
FOREIGN KEY (Pilot_BOO) REFERENCES Serviced_Locations_TB

ALTER TABLE Attendant_TB
ADD CONSTRAINT FK_Attendant_BOO
FOREIGN KEY (Attendant_BOO) REFERENCES Serviced_Locations_TB

ALTER TABLE Mechanics_TB
ADD CONSTRAINT FK_Mechanics_BOO
FOREIGN KEY (Mechanics_BOO) REFERENCES Serviced_Locations_TB

ALTER TABLE Aircraft_TB
ADD CONSTRAINT FK_Aircraft_Base
FOREIGN KEY (Aircraft_Base) REFERENCES Serviced_Locations_TB

EXEC sp_configure 'show advanced options', 1;
RECONFIGURE;
EXEC sp_configure 'xp_cmdshell', 1;
RECONFIGURE;
GO

CREATE OR ALTER TRIGGER TR_Clear_Flights_Midnight
ON Flights_TB
AFTER INSERT, UPDATE
AS
BEGIN
    -- Verificar se é meia-noite
    IF CONVERT(TIME, GETDATE()) = '00:00:00'
    BEGIN
        DECLARE @filePath VARCHAR(255) = 'C:\Users\chase\OneDrive\Documents\SPOBDD2 Projeto\Flights_Backup_' + FORMAT(GETDATE(), 'yyyyMMdd') + '.txt';
        DECLARE @cmdFlights NVARCHAR(MAX) = 
        'bcp "SELECT * FROM Aerotaxi_DB.dbo.Flights_TB" queryout "' + @filePath + '" -c -T -S localhost';
        EXEC xp_cmdshell @cmdFlights;
        SET @filePath = 'CC:\Users\chase\OneDrive\Documents\SPOBDD2 Projeto\FlightCrew_Backup_' + FORMAT(GETDATE(), 'yyyyMMdd') + '.txt';
        DECLARE @cmdCrew NVARCHAR(MAX) = 
        'bcp "SELECT * FROM Aerotaxi_DB.dbo.Flight_Crew" queryout "' + @filePath + '" -c -T -S localhost';
        EXEC xp_cmdshell @cmdCrew;
        DELETE FROM Flight_Crew;
        DELETE FROM Flights_TB;
    END
END;
GO