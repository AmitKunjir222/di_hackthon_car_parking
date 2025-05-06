import mysql.connector

available_parking_slots = ['P1', 'P2', 'P3', 'P4']
admin_serial_number = [6]


# Function to establish a connection to the MySQL database
def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host="host_name",
            user="user_name",
            password="password",
            database="parking"  # Assuming your database name is CarPark
        )
        print("Connected to the database it..")
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
def update_parking_status_empty_to_occupied(connection, employee_name, Parking_Slot_Number,
                                            admin_passed_employee_name=None):
    try:
        cursor = connection.cursor()
        Parking_Position = ''
        empty_slot_count, empty_Parking_Slot_Number, occupied_slot_count, occupied_Parking_Slot_Number = empty_occupied_parking_slot_info(connection)

        if Parking_Slot_Number not in available_parking_slots:
            return "Please enter correct parking slot number. Valid parking slots are {}".format(str(available_parking_slots))
        elif empty_slot_count == 0:
            return "Parking is full now. Please use other alternatives."
        elif Parking_Slot_Number in occupied_Parking_Slot_Number:
            return "This parking slot {} is used by another employee.\nUse below available parking slots \n {}".format(Parking_Slot_Number, str(empty_Parking_Slot_Number))

        query = "SELECT Employee_Name,Serial_Number from Employee WHERE Employee_Name = \'" + employee_name + "\';"
        cursor.execute(query)
        data = cursor.fetchall()

        for row in data:
            employee_name = row[0]
            Serial_Number = row[1]

        if Parking_Slot_Number in ('P1', 'P3'):
            Parking_Position = "upper"
        elif Parking_Slot_Number in ('P2', 'P4'):
            Parking_Position = "lower"

        if Serial_Number in admin_serial_number and admin_passed_employee_name is not None:
            query = "UPDATE Parking_Slots SET Status = 'occupied', Arrival_time=NOW(),Out_time=null, Parking_Slot_Number ='{Parking_Slot_Number}',Parking_Position='{Parking_Position}' WHERE Serial_Number IN (SELECT Serial_Number from Employee where Employee_Name LIKE '%{admin_passed_employee_name}%');".format(
                Parking_Slot_Number=Parking_Slot_Number,Parking_Position=Parking_Position,admin_passed_employee_name=admin_passed_employee_name)
            print("park1 {}".format(query))
            cursor.execute(query)
            cursor.fetchall()
            return f"{employee_name} has parked vehicle in {Parking_Slot_Number} for {admin_passed_employee_name}"

        else:
            query = "UPDATE Parking_Slots SET Status = 'occupied', Arrival_time=NOW(),Out_time=null, Parking_Slot_Number = %s,Parking_Position=%s WHERE Serial_Number = %s;"
            data = (Parking_Slot_Number, Parking_Position, Serial_Number)
            print("park2 {}".format(query))
            cursor.execute(query, data)
            return f"{employee_name} has parked vehicle in {Parking_Slot_Number}"

    except mysql.connector.Error as e:
        print("Error updating parking status:", e)

    finally:
        print("Parking status updated successfully")
        connection.commit()

    # Function to update the parking status from occupied to empty


def update_parking_status_occupied_to_empty(connection, employee_name, Parking_Slot_Number, admin_passed_employee_name=None):
    try:
        cursor = connection.cursor()
        empty_slot_count, empty_Parking_Slot_Number, occupied_slot_count, occupied_Parking_Slot_Number = empty_occupied_parking_slot_info(connection)

        if Parking_Slot_Number not in available_parking_slots:
            return "Please enter correct parking slot number. Valid parking slots are {}".format(str(available_parking_slots))
        # elif empty_slot_count == 0:
        #     return "Parking is full now. Please use other alternatives."
        # elif Parking_Slot_Number in occupied_Parking_Slot_Number:
        #     return "This parking slot {} is used by another employee.\nUse below available parking slots \n {}".format(Parking_Slot_Number, str(empty_Parking_Slot_Number))

        # employee_car = {}
        if Parking_Slot_Number == "P1":
            query = "SELECT e.Employee_Name, e.Serial_Number, ps.Parking_Slot_Number, ps.Parking_Position, ps.Status from Employee e JOIN Parking_Slots ps on e.Serial_Number = ps.Serial_Number where Parking_Slot_Number='P2';"
            cursor.execute(query)
            data = cursor.fetchall()
            if len(data) > 0:
                for row in data:
                    employee_name_p2 = row[0]
                    Serial_Number_p2 = row[1]
                    Parking_Slot_Number_p2 = row[2]
                    Parking_Position_p2 = row[3]
                    Status_p2 = row[4]
                if Status_p2 == 'occupied':
                    if admin_passed_employee_name is not None:
                        return f"{employee_name_p2} Please unpark your vehicle from {Parking_Slot_Number_p2} so that {admin_passed_employee_name} can unpark from parking slot {Parking_Slot_Number}"
                    else:
                        return f"{employee_name_p2} Please unpark your vehicle from {Parking_Slot_Number_p2} so that {employee_name} can unpark from parking slot {Parking_Slot_Number}"
        elif Parking_Slot_Number == "P3":
            query = "SELECT e.Employee_Name, e.Serial_Number, ps.Parking_Slot_Number, ps.Parking_Position, ps.Status from Employee e JOIN Parking_Slots ps on e.Serial_Number = ps.Serial_Number where Parking_Slot_Number='P4';"
            cursor.execute(query)
            data = cursor.fetchall()
            if len(data) > 0:
                for row in data:
                    employee_name_p4 = row[0]
                    Serial_Number_p4 = row[1]
                    Parking_Slot_Number_p4 = row[2]
                    Parking_Position_p4 = row[3]
                    Status_p4 = row[4]
                if Status_p4 == 'occupied':
                    if admin_passed_employee_name is not None:
                        return f"{employee_name_p4} Please unpark your vehicle from {Parking_Slot_Number_p4} so that {admin_passed_employee_name} can unpark from parking slot {Parking_Slot_Number}"
                    else:
                        return f"{employee_name_p4} Please unpark your vehicle from {Parking_Slot_Number_p4} so that {employee_name} can unpark from parking slot {Parking_Slot_Number}"

            # employee_car[employee_name] = (serial_number, parking_slot_number)
            # employee_car.update{"employee_name":employee_name,"Serial_Number":Serial_Number,"Parking_Slot_Number":Parking_Slot_Number,"Parking_Position":Parking_Position, "Status":Status }
        query = "SELECT e.Employee_Name,e.Serial_Number,ps.Parking_Slot_Number from Employee e JOIN Parking_Slots ps ON e.Serial_Number = ps.Serial_Number WHERE Employee_Name = \'" + employee_name + "\';"
        print("Emp1 {}".format(query))
        cursor.execute(query)
        data = cursor.fetchall()

        for row in data:
            employee_name = row[0]
            Serial_Number = row[1]
            db_Parking_Slot_Number = row[2]

        if Serial_Number in admin_serial_number and admin_passed_employee_name is not None:
            query = "UPDATE Parking_Slots SET Status = 'empty',Out_time=NOW(), Parking_Slot_Number = null,Parking_Position=null WHERE Serial_Number in (SELECT Serial_Number from Employee where Employee_Name LIKE '%{admin_passed_employee_name}%');".format(
                admin_passed_employee_name=admin_passed_employee_name)
            print("Yadav query {}".format(query))
            cursor.execute(query)
            return f"{employee_name} has unparked vehicle from {Parking_Slot_Number} for {admin_passed_employee_name}"
        else:
            if db_Parking_Slot_Number != Parking_Slot_Number:
                if db_Parking_Slot_Number is None:
                    return "You have not parked your vechile yet.".format(str(db_Parking_Slot_Number))
                else:
                    return "You have entered incorrect parking slot number. Your parking slot number is {}".format(str(db_Parking_Slot_Number))
            else:
                query = "UPDATE Parking_Slots SET Status = 'empty',Out_time=NOW(), Parking_Slot_Number = null,Parking_Position=null WHERE Serial_Number = {};".format(int(Serial_Number))

                cursor.execute(query)
                cursor.fetchall()
                return f"{employee_name} has un-parked vehicle from {Parking_Slot_Number} slot. Drive Safe :blue_car:"

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
def fetch_car_details(connection, car_no, give_dict = False):
    try:
        cursor = connection.cursor()

        query = "SELECT Employee_Name, Team, Floor,MobileNo from Employee where (Car1 = \'" + car_no + "\' OR Car2 = \'" + car_no + "\');"
        cursor.execute(query)
        data = cursor.fetchall()
        car_details = {}
        if len(data) > 0:
            for row in data:
                employee_name = row[0]
                team = row[1]
                floor = row[2]
                mobile = row[3]
                if give_dict:
                    car_details.update({'employee_name': employee_name})
                    car_details.update({'team': team})
                    car_details.update({'floor': floor})
                    car_details.update({'mobile': mobile})
                    return car_details

            return " Car Details for {}\n\nEmployee Name - {}\nTeam - {}\nFloor - {}\nMobile No - {}".format(car_no, employee_name, team, floor, mobile)
        else:
            return " Car {} doesn't belong to DI employee".format(car_no)

    except mysql.connector.Error as e:
        print("Error while fetching fetching car details:", e)

    finally:
        print("Car details fetched successfully")
        connection.commit()


# Function to fetch employee-car details
# Function to fetch employee-car details
def get_employee_and_car_details(connection):
    try:
        cursor = connection.cursor()
        query = "SELECT e.Employee_Name, e.Team, e.Floor, COALESCE(e.Car1, 'NA') AS Car, e.MobileNo, COALESCE(ps.Parking_Slot_Number, 'NA') AS Parking_Slot_Number,ps.Status FROM Employee e JOIN Parking_Slots ps ON e.Serial_Number = ps.Serial_Number;"
        cursor.execute(query)
        data = cursor.fetchall()
        car_employee_dict = {}
        for row in data:
            employee_name = row[0]
            team = row[1]
            floor = row[2]
            car_no = row[3]
            mobileno = row[4]
            Parking_Slot_Number = row[5]
            Status = row[6]
            car_employee_dict.update({row: {"employee_name": employee_name, "car_no": car_no, "mobileno": mobileno,"Parking_Slot_Number": Parking_Slot_Number, "Status": Status}})
        print("Car employee details {}".format(car_employee_dict))
        return car_employee_dict

    except mysql.connector.Error as e:
        print("Error while fetching fetching car-employee details:", e)
