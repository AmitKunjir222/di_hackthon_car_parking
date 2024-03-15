import mysql.connector

available_parking_slots = ['P1', 'P2', 'P3', 'P4']


# Function to establish a connection to the MySQL database
def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host="mysql1-dev-useast.deepintent.com",
            user="tejas.jain@deepintent.com",
            password="QzUDDkYpnzHKnasjEh",
            database="bidder"  # Assuming your database name is CarPark
        )
        print("Connected to the database")
        return connection
    except mysql.connector.Error as e:
        print("Error connecting to the database:", e)
        return None


# Function to close the database connection
def close_connection(connection):
    if connection:
        connection.close()
        print("Connection to the database closed")


# Function to retrieve parking availability
def get_parking_availability(connection):
    try:
        global available_parking_slots
        empty_slot_count, empty_Parking_Slot_Number, occupied_slot_count, occupied_Parking_Slot_Number = empty_occupied_parking_slot_info(
            connection)
        intersection = [x for x in available_parking_slots if x in occupied_Parking_Slot_Number]
        print("Intersection {}".format(intersection))

        available_parking_slots = set(available_parking_slots)
        intersection = set(intersection)
        print("Inside available_parking_slots {}".format(str(list(available_parking_slots))))
        # Find the set difference to remove common elements
        newly_available_parking_slot = available_parking_slots - intersection

        print("Inside get parking {}".format(str(list(newly_available_parking_slot))))

        if empty_slot_count > 0:
            return list(newly_available_parking_slot)
        else:
            return "No Parking Available ... "
    except mysql.connector.Error as e:
        print("Error retrieving parking availability:", e)
        return None


# Function to update the parking status from empty to occupied
def update_parking_status_empty_to_occupied(connection, employee_name, Parking_Slot_Number):
    try:
        cursor = connection.cursor()
        empty_slot_count, empty_Parking_Slot_Number, occupied_slot_count, occupied_Parking_Slot_Number = empty_occupied_parking_slot_info(connection)

        if Parking_Slot_Number not in available_parking_slots:
            return "Please enter correct parking slot number. Valid parking slots are {}".format(str(available_parking_slots))
        elif empty_slot_count == 0:
            return "Parking is full now. Please use other alternatives."
        elif Parking_Slot_Number in occupied_Parking_Slot_Number:
            return "This parking slot {} is used by another employee.\nUse below available parking slots \n {}".format(Parking_Slot_Number, str(empty_Parking_Slot_Number))


        query = "SELECT Employee_Name,Serial_Number from Employee WHERE Employee_Name = \'"+employee_name+"\';"
        cursor.execute(query)
        data = cursor.fetchall()

        for row in data:
            employee_name = row[0]
            Serial_Number = row[1]

        query = "UPDATE Parking_Slots SET Status = 'occupied', Arrival_time=NOW(),Out_time=null, Parking_Slot_Number = %s WHERE Serial_Number = %s;"
        data = (Parking_Slot_Number, Serial_Number)
        cursor.execute(query, data)
        return f"{employee_name} has parked vehicle in {Parking_Slot_Number}"

    except mysql.connector.Error as e:
        print("Error updating parking status:", e)

    finally:
        print("Parking status updated successfully")
        connection.commit()

    # Function to update the parking status from occupied to empty


def update_parking_status_occupied_to_empty(connection, employee_name, Parking_Slot_Number):
    try:
        cursor = connection.cursor()
        empty_slot_count, empty_Parking_Slot_Number, occupied_slot_count, occupied_Parking_Slot_Number = empty_occupied_parking_slot_info(connection)

        query = "SELECT e.Employee_Name,e.Serial_Number,ps.Parking_Slot_Number from Employee e JOIN bidder.Parking_Slots ps ON e.Serial_Number = ps.Serial_Number WHERE Employee_Name = \'"+employee_name+"\';"
        cursor.execute(query)
        data = cursor.fetchall()

        for row in data:
            employee_name = row[0]
            Serial_Number = row[1]
            db_Parking_Slot_Number = row[2]

        if db_Parking_Slot_Number != Parking_Slot_Number:
            if db_Parking_Slot_Number is None:
                return "You have not parked your vechile yet.".format(str(db_Parking_Slot_Number))
            else:
                return "You have entered incorrect parking slot number. Your parking slot number is {}".format(str(db_Parking_Slot_Number))
        else:
            query = "UPDATE Parking_Slots SET Status = 'empty',Out_time=NOW(), Parking_Slot_Number = null WHERE Serial_Number = {};".format(int(Serial_Number))

            cursor.execute(query)
            cursor.fetchall()

            return f"{employee_name} has un-parked vehicle from {Parking_Slot_Number} slot. Bye Bye"

    except mysql.connector.Error as e:
        print("Error updating parking status:", e)

    finally:
        print("Parking status updated successfully")
        connection.commit()


def empty_occupied_parking_slot_info(connection):
    global available_parking_slots
    cursor = connection.cursor()
    global_available_parking_slots = available_parking_slots

    query_parking_slots = "SELECT Parking_Slot_Number,Status from Parking_Slots"

    cursor.execute(query_parking_slots)
    no_of_records_parking_slots = cursor.fetchall()

    empty_slot_count = 0
    occupied_slot_count = 0
    empty_Parking_Slot_Number = []
    occupied_Parking_Slot_Number = []

    if len(no_of_records_parking_slots) > 0:
        for row in no_of_records_parking_slots:
            Parking_Slot_Number = row[0]
            Status = row[1]
            # dictionary_parking_slots.update(Parking_Slot_Number:Status)
            if Status == 'empty':
                empty_slot_count = empty_slot_count + 1
                empty_Parking_Slot_Number.append(Parking_Slot_Number)
            elif Status == 'occupied':
                occupied_slot_count = occupied_slot_count + 1
                occupied_Parking_Slot_Number.append(Parking_Slot_Number)

        intersection = [x for x in global_available_parking_slots if x in occupied_Parking_Slot_Number]
        print("Intersection in empty_occupied_parking_slot_info {}".format(intersection))

        global_available_parking_slots = set(global_available_parking_slots)
        intersection = set(intersection)
        print("Inside available_parking_slots {}".format(str(list(available_parking_slots))))
        # Find the set difference to remove common elements
        empty_Parking_Slot_Number = global_available_parking_slots - intersection
        empty_slot_count = len(empty_Parking_Slot_Number)
        print("empty_slot_count", empty_slot_count)
        print("occupied_slot_count", occupied_slot_count)
        print("empty_Parking_Slot_Number", empty_Parking_Slot_Number)
        print("occupied_Parking_Slot_Number", occupied_Parking_Slot_Number)

    return empty_slot_count, empty_Parking_Slot_Number, occupied_slot_count, occupied_Parking_Slot_Number


# Function to fetch employee details from car number
def fetch_car_details(connection, car_no):
    try:
        cursor = connection.cursor()

        query = "SELECT Employee_Name, Team, Floor from bidder.Employee where (Car1 = \'"+car_no+"\' OR Car2 = \'"+car_no+"\');"
        cursor.execute(query)
        data = cursor.fetchall()

        if len(data) > 0:
            for row in data:
                employee_name = row[0]
                team = row[1]
                floor = row[2]
            return "Car Details for {}\nEmployee Name - {}\nTeam - {}\nFloor - {}".format(car_no, employee_name, team, floor)
        else:
            return "Car {} doesn't belong to DI employee".format(car_no)

    except mysql.connector.Error as e:
        print("Error while fetching fetching car details:", e)

    finally:
        print("Car details fetched successfully")
        connection.commit()