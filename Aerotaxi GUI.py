import tkinter as tk
import pyodbc as pdbc
from tkinter import END, Listbox, ttk, messagebox, Toplevel, Label, Entry, StringVar, DoubleVar, IntVar
from tkinter.ttk import Combobox
import os

server='localhost'
database='Aerotaxi_DB'

# Function to switch frames
def show_frame(frame):
    frame.tkraise()

#Conexão Inicial
def initialize_app():
    global db_connection
    db_connection = connect_to_db()
    if db_connection is None:
        messagebox.showerror("Critical Error", "Application will close due to database connection failure.")
        root.destroy()

SERVER = 'localhost,1433'
DATABASE = 'Aerotaxi_DB'

#Contém a connection string do servidor, e prove feedback para sucesso ou falha da conexão
def connect_to_db():
    try:
        conn = pdbc.connect(
            driver='{ODBC Driver 17 for SQL Server}',
            server=SERVER, 
            database=DATABASE,               
            trusted_connection='yes'
        )
        
        messagebox.showinfo("Sucesso", "Conexão com o banco realizada com sucesso!")
        return conn
    except pdbc.Error as e:
        messagebox.showerror("Erro", f"Erro ao conectar: {e}")
        return None

# Create the main window
root = tk.Tk()
root.title("Gerenciamento Interno")
root.geometry("900x600")

# Create frames
main_menu = ttk.Frame(root)
Flight_Page = ttk.Frame(root)
Aircraft_Page = ttk.Frame(root)
Pilot_Page = ttk.Frame(root)
Attendant_Page = ttk.Frame(root)
GCrew_Page = ttk.Frame(root)
Location_Page = ttk.Frame(root)
Route_Page = ttk.Frame(root)
Flight_Crew_Page = ttk.Frame(root)

for frame in (main_menu, Flight_Page, Aircraft_Page, Pilot_Page, Attendant_Page, GCrew_Page, Location_Page, Route_Page):
    frame.grid(row=0, column=0, sticky="nsew")

# Main menu
ttk.Label(main_menu, text="Main Menu", font=("Arial", 16)).pack(pady=20)
ttk.Button(main_menu, text="Vôos", command=lambda: show_frame(Flight_Page)).pack(pady=10)
ttk.Button(main_menu, text="Aeronaves", command=lambda: show_frame(Aircraft_Page)).pack(pady=10)
ttk.Button(main_menu, text="Piloto/as", command=lambda: show_frame(Pilot_Page)).pack(pady=10)
ttk.Button(main_menu, text="Comissário/as", command=lambda: show_frame(Attendant_Page)).pack(pady=10)
ttk.Button(main_menu, text="Mecanico/as", command=lambda: show_frame(GCrew_Page)).pack(pady=10)
ttk.Button(main_menu, text="Localizações", command=lambda: show_frame(Location_Page)).pack(pady=10)
ttk.Button(main_menu, text="Rotas", command=lambda: show_frame(Route_Page)).pack(pady=10)

# Page 1
def load_flight_data():
    for row in flight_tree.get_children():
        flight_tree.delete(row)

    # Chama dados do banco
    try:
        cursor = db_connection.cursor()
        query = """
        SELECT 
            f.Flight_ID,
            f.Flight_Route,
            f.Flight_Aircraft,
            f.Flight_Departure,
            f.Flight_Arrival,
            f.Flight_Passengers,
            COALESCE(crew_count.total_crew, 0) AS Crew_Count
        FROM 
            Flights_TB f
        LEFT JOIN 
            (SELECT Flight_ID, COUNT(*) AS total_crew 
             FROM Flight_Crew 
             GROUP BY Flight_ID) crew_count
        ON 
            f.Flight_ID = crew_count.Flight_ID
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        for row in rows:
            flight_id = row[0]
            flight_route = row[1]
            flight_aircraft = row[2]
            flight_departure = row[3]
            flight_arrival = row[4]
            flight_passengers = row[5]
            crew_count = row[6]

            # Insere os dados formatados corretamente na Treeview
            flight_tree.insert("", "end", values=(
                flight_id,
                flight_route,
                flight_aircraft,
                flight_departure,
                flight_arrival,
                flight_passengers,
                crew_count
            ))

        cursor.close()
    except pdbc.Error as e:
        messagebox.showerror("Erro", f"Erro ao carregar dados dos voos: {e}")

# Configuração da Treeview
columns = ("Flight_ID", "Flight_Route", "Flight_Aircraft", "Flight_Departure", "Flight_Arrival", "Flight_Passengers", "Crew_Count")
flight_tree = ttk.Treeview(Flight_Page, columns=columns, show="headings")
flight_tree.pack(pady=10, fill="both", expand=True)

# Configuração das colunas
flight_tree.heading("Flight_ID", text="ID do Voo")
flight_tree.heading("Flight_Route", text="Rota")
flight_tree.heading("Flight_Aircraft", text="Aeronave")
flight_tree.heading("Flight_Departure", text="Partida")
flight_tree.heading("Flight_Arrival", text="Chegada")
flight_tree.heading("Flight_Passengers", text="Núm. de Passageiros")
flight_tree.heading("Crew_Count", text="Tripulação Selecionada")

# Ajuste de largura e alinhamento das colunas
flight_tree.column("Flight_ID", width=100, anchor="center")
flight_tree.column("Flight_Route", width=100, anchor="center")
flight_tree.column("Flight_Aircraft", width=100, anchor="center")
flight_tree.column("Flight_Departure", width=100, anchor="center")
flight_tree.column("Flight_Arrival", width=100, anchor="center")
flight_tree.column("Flight_Passengers", width=150, anchor="center")
flight_tree.column("Crew_Count", width=150, anchor="center")

def open_add_flight_page():
    add_flight_window = Toplevel(Flight_Page)
    add_flight_window.title("Adicionar Novo Voo")
    add_flight_window.geometry("500x500")

    # Variáveis para armazenar os dados do formulário
    route_var = StringVar()
    aircraft_var = StringVar()
    departure_var = StringVar()
    arrival_var = StringVar()
    passengers_var = IntVar()

    # Widgets do formulário
    Label(add_flight_window, text="Selecione a Rota:").pack(pady=5, anchor="w")
    route_combobox = ttk.Combobox(add_flight_window, textvariable=route_var)
    route_combobox.pack(pady=5, fill="x")

    Label(add_flight_window, text="Selecione a Aeronave:").pack(pady=5, anchor="w")
    aircraft_combobox = ttk.Combobox(add_flight_window, textvariable=aircraft_var)
    aircraft_combobox.pack(pady=5, fill="x")

    Label(add_flight_window, text="Horário de Partida:").pack(pady=5, anchor="w")
    departure_time = ttk.Entry(add_flight_window, textvariable=departure_var)
    departure_time.pack(pady=5, fill="x")

    Label(add_flight_window, text="Horário de Chegada:").pack(pady=5, anchor="w")
    arrival_time = ttk.Entry(add_flight_window, textvariable=arrival_var)
    arrival_time.pack(pady=5, fill="x")

    Label(add_flight_window, text="Número de Passageiros:").pack(pady=5, anchor="w")
    Entry(add_flight_window, textvariable=passengers_var).pack(pady=5, fill="x")

    # Carregar dados para os comboboxes
    try:
        cursor = db_connection.cursor()

        # Carregar rotas
        cursor.execute("SELECT Route_ID FROM Routes_TB")
        routes = cursor.fetchall()
        route_combobox["values"] = [route[0] for route in routes]

        # Carregar aeronaves
        cursor.execute("SELECT Aircraft_ID FROM Aircraft_TB")
        aircrafts = cursor.fetchall()
        aircraft_combobox["values"] = [aircraft[0] for aircraft in aircrafts]

        cursor.close()
    except pdbc.Error as e:
        messagebox.showerror("Erro", f"Erro ao carregar dados: {e}")
        add_flight_window.destroy()
        return

    # Função para adicionar o voo
    def add_flight():
        flight_route = route_var.get()
        flight_aircraft = aircraft_var.get()
        flight_departure = departure_var.get()
        flight_arrival = arrival_var.get()
        flight_passengers = passengers_var.get()

        # Validação de entrada básica
        if not flight_route or not flight_aircraft or not flight_departure or not flight_arrival or not flight_passengers:
            messagebox.showerror("Erro", "Todos os campos devem ser preenchidos.")
            return
        if not str(flight_passengers).isdigit() or int(flight_passengers) <= 0:
            messagebox.showerror("Erro", "Número de passageiros inválido.")
            return
        
        try:
            cursor = db_connection.cursor()
            # Verificar status da aeronave
            query_aircraft_status = "SELECT Aircraft_Status FROM Aircraft_TB WHERE Aircraft_ID = ?"
            cursor.execute(query_aircraft_status, (flight_aircraft,))
            status_result = cursor.fetchone()

            if status_result is None:
                messagebox.showerror("Erro", "Aeronave selecionada não encontrada.")
                return

            aircraft_status = status_result[0]
            if aircraft_status != "Operacional":
                messagebox.showerror(
                "Erro",
                f"A aeronave selecionada não está operacional. Status atual: {aircraft_status}."
                )
                return
        except pdbc.Error as e:
            messagebox.showerror("Erro", f"Erro ao adicionar voo: {e}")

    

        # Verificar capacidade máxima da aeronave
        try:
            cursor = db_connection.cursor()

                    # Check for overlapping schedules for the same aircraft
            conflict_query_aircraft = """
            SELECT Flight_ID
            FROM Flights_TB
            WHERE Flight_Aircraft = ?
            AND (
                (Flight_Departure <= ? AND Flight_Arrival > ?)
                OR (Flight_Departure < ? AND Flight_Arrival >= ?)
            )
            """
            cursor.execute(
                conflict_query_aircraft,
                (flight_aircraft, flight_departure, flight_departure, flight_arrival, flight_arrival)
            )
            conflicts = cursor.fetchall()

            if conflicts:
                messagebox.showerror(
                    "Erro",
                    f"A aeronave selecionada já está programada para outro voo no horário especificado."
                )
                return

            query_aircraft = "SELECT Aircraft_MaxCap, Aircraft_Crew FROM Aircraft_TB WHERE Aircraft_ID = ?"
            cursor.execute(query_aircraft, (flight_aircraft,))
            result = cursor.fetchone()

            if result is None:
                messagebox.showerror("Erro", "Aeronave selecionada não encontrada.")
                return

            max_cap, min_crew_required = result
            if flight_passengers > max_cap:
                messagebox.showerror(
                    "Erro",
                    f"O número de passageiros ({flight_passengers}) excede a capacidade máxima da aeronave ({max_cap})."
                )
                return    

            # Obter ponto de partida da rota
            query_route = "SELECT Route_Origin, Route_Destination FROM Routes_TB WHERE Route_ID = ?"
            cursor.execute(query_route, (flight_route,))
            route_points = cursor.fetchone()

            if route_points is None:
                messagebox.showerror("Erro", "Rota selecionada não encontrada.")
                return

            departure_point, arrival_point = route_points

            # Verificar posição atual da aeronave
            query_position = "SELECT Current_Location FROM Aircraft_Position WHERE Aircraft_ID = ?"
            cursor.execute(query_position, (flight_aircraft))
            position_data = cursor.fetchone()

            if position_data is None:
                aircraft_base_query = "SELECT Aircraft_Base FROM Aircraft_TB WHERE Aircraft_ID = ?"
                cursor.execute(aircraft_base_query, (flight_aircraft,))
                aircraft_base_data = cursor.fetchone()
                if aircraft_base_data is None:
                    messagebox.showerror("Erro", "Base de operações da aeronave não encontrada.")
                    return

                aircraft_base = aircraft_base_data[0]

                if departure_point != aircraft_base:
                    messagebox.showerror(
                        "Erro",
                        f"O primeiro voo da aeronave deve partir de sua base ({aircraft_base_data})."
                    )
                    return

                # Inserir posição inicial na tabela Aircraft_Position
                insert_position_query = """
                INSERT INTO Aircraft_Position (Aircraft_ID, Current_Location)
                VALUES (?, ?)
                """
                cursor.execute(insert_position_query, (flight_aircraft, arrival_point))

            else:
                # Verificar se o ponto de partida é igual à posição atual
                current_location = position_data[0]
                if departure_point != current_location:
                    messagebox.showerror(
                        "Erro",
                        f"A aeronave não pode partir de {departure_point} porque está localizada em {current_location}."
                    )
                    return

                # Atualizar posição da aeronave após o voo
                update_position_query = """
                UPDATE Aircraft_Position
                SET Current_Location = ?
                WHERE Aircraft_ID = ?
                """
                cursor.execute(update_position_query, (arrival_point, flight_aircraft))

            # Inserir o voo na tabela
            query = """
            INSERT INTO Flights_TB (Flight_Route, Flight_Aircraft, Flight_Departure, Flight_Arrival, Flight_Passengers)
            OUTPUT INSERTED.Flight_ID
            VALUES (?, ?, ?, ?, ?)
            """
            cursor.execute(query, (flight_route, flight_aircraft, flight_departure, flight_arrival, flight_passengers))
            flight_id = cursor.fetchone()[0]  # Recuperar o ID do voo recém-criado
            db_connection.commit()
            cursor.close()

            messagebox.showinfo("Sucesso", "Voo adicionado com sucesso!")

            # Abrir janela de tripulação
            open_add_flight_crew_page(flight_id, min_crew_required)

            # Fechar janela de adição de voo
            add_flight_window.destroy()

        except pdbc.Error as e:
            messagebox.showerror("Erro", f"Erro ao adicionar voo: {e}")

    # Botão para confirmar a adição
    ttk.Button(add_flight_window, text="Adicionar Voo", command=add_flight).pack(pady=20)

    # Botão para fechar a janela
    ttk.Button(add_flight_window, text="Fechar", command=add_flight_window.destroy).pack(pady=10)

def open_add_flight_crew_page(flight_id, min_crew_required):
    add_crew_window = Toplevel()
    add_crew_window.title("Adicionar Tripulação ao Voo")
    add_crew_window.geometry("500x600")
    add_crew_window.protocol("WM_DELETE_WINDOW", lambda: messagebox.showerror(
        "Erro", "Você não pode sair até que a tripulação mínima seja atribuída."
    ))

    # Variáveis para armazenar os dados
    crew_var = StringVar()

    # Widgets do formulário
    Label(add_crew_window, text=f"Voo Selecionado: {flight_id}").pack(pady=5, anchor="w")

    Label(add_crew_window, text="Selecione Membro da Tripulação:").pack(pady=5, anchor="w")
    crew_combobox = ttk.Combobox(add_crew_window, textvariable=crew_var)
    crew_combobox.pack(pady=5, fill="x")

    crew_listbox = Listbox(add_crew_window, height=10)
    crew_listbox.pack(pady=10, fill="x")

    # Carregar dados para o combo box da tripulação
    try:
        cursor = db_connection.cursor()

        # Carregar pilotos e comissários
        cursor.execute("SELECT Pilot_ID, Pilot_Name, Pilot_BOO FROM Pilots_TB")
        pilots = cursor.fetchall()

        cursor.execute("SELECT Attendant_ID, Attendant_Name, Attendant_BOO FROM Attendant_TB")
        attendants = cursor.fetchall()

        # Carregar a posição atual dos tripulantes na tabela Crew_Position
        cursor.execute("""
            SELECT Crew_ID, Current_Location
            FROM Crew_Position
        """)
        crew_positions = cursor.fetchall()
        
        # Criar um dicionário para mapear Crew_ID com a posição atual
        crew_position_map = {crew_position[0]: crew_position[1] for crew_position in crew_positions}

        crew_combobox["values"] = [
            f"P-{pilot[0]}: {pilot[1]} | BOO: {pilot[2]} | Posição: {crew_position_map.get(pilot[0], 'Posição não definida')}"
            for pilot in pilots
        ] + [
            f"A-{attendant[0]}: {attendant[1]} | BOO: {attendant[2]} | Posição: {crew_position_map.get(attendant[0], 'Posição não definida')}"
            for attendant in attendants
        ]

        cursor.close()
    except pdbc.Error as e:
        messagebox.showerror("Erro", f"Erro ao carregar dados: {e}")
        add_crew_window.destroy()
        return
    
    def get_route_points(flight_id):
        try:
            # Obter Route_ID associado ao Flight_ID
            cursor = db_connection.cursor()
            query_route_id = "SELECT Flight_Route FROM Flights_TB WHERE Flight_ID = ?"
            cursor.execute(query_route_id, (flight_id,))
            route_id_data = cursor.fetchone()

            if route_id_data is None:
                messagebox.showerror("Erro", "Voo não encontrado.")
                return None, None

            route_id = route_id_data[0]

            # Obter Route_Origin e Route_Destination associado ao Route_ID
            query_route_points = "SELECT Route_Origin, Route_Destination FROM Routes_TB WHERE Route_ID = ?"
            cursor.execute(query_route_points, (route_id,))
            route_points = cursor.fetchone()

            if route_points is None:
                messagebox.showerror("Erro", "Rota associada ao voo não encontrada.")
                return None, None
            cursor.close()
            return route_points  # Retorna (Route_Origin, Route_Destination)
        except pdbc.Error as e:
            messagebox.showerror("Erro", f"Erro ao acessar o banco de dados: {e}")
            return None, None

    def add_crew_member():
        selected_crew = crew_var.get()
        if not selected_crew:
            messagebox.showerror("Erro", "Selecione um membro da tripulação.")
            return

        crew_type, crew_data = selected_crew.split("-")
        crew_id = int(crew_data.split(":")[0].strip())

        

        # Get departure and arrival points for the flight
        departure_point, arrival_point = get_route_points(flight_id)
        if departure_point is None or arrival_point is None:
            return  # If route data can't be fetched, stop execution

        try:
            cursor = db_connection.cursor()

            # Fetch flight times for the current flight
            cursor.execute(
                "SELECT Flight_Departure, Flight_Arrival FROM Flights_TB WHERE Flight_ID = ?",
                (flight_id,)
            )
            flight_times = cursor.fetchone()
            if not flight_times:
                messagebox.showerror("Erro", "Horários do voo não encontrados.")
                return

            flight_departure, flight_arrival = flight_times

            # Check for schedule conflicts for the selected crew member
            query_schedule_conflict = """
            SELECT F.Flight_ID, F.Flight_Departure, F.Flight_Arrival
            FROM Flight_Crew FC
            JOIN Flights_TB F ON FC.Flight_ID = F.Flight_ID
            WHERE FC.Crew_ID = ?
              AND NOT (
                  ? >= F.Flight_Arrival OR
                  ? <= F.Flight_Departure
              )
            """
            cursor.execute(query_schedule_conflict, (crew_id, flight_departure, flight_arrival))
            conflicts = cursor.fetchall()

            if conflicts:
                conflict_details = "\n".join(
                    [f"Voo {conflict[0]}: {conflict[1]} - {conflict[2]}" for conflict in conflicts]
                )
                messagebox.showerror(
                    "Conflito de Horário",
                    f"O membro da tripulação já está atribuído aos seguintes voos com conflito de horário:\n{conflict_details}"
                )
                return

            # Verificar se a posição do tripulante já está registrada na tabela Crew_Position
            query_position = "SELECT Current_Location FROM Crew_Position WHERE Crew_ID = ?"
            cursor.execute(query_position, (crew_id,))
            position_data = cursor.fetchone()

            if position_data is None:
                # Posição não registrada - Obter base de operações do tripulante
                # Obter base de operações do tripulante se posição não registrada
                if crew_type == "P":
                    base_query = "SELECT Pilot_BOO FROM Pilots_TB WHERE Pilot_ID = ?"
                else:
                    base_query = "SELECT Attendant_BOO FROM Attendant_TB WHERE Attendant_ID = ?"
                cursor.execute(base_query, (crew_id,))
                base_data = cursor.fetchone()

                if base_data is None:
                    messagebox.showerror(f"Base de operações não encontrada para o tripulante {crew_id}.")
                    return
                
                crew_base = base_data[0]
                
                # Verificar se o ponto de partida coincide com a base de operações
                if departure_point != crew_base:
                    messagebox.showerror(
                        "Erro",
                        f"O primeiro voo do tripulante deve partir de sua base ({crew_base})."
                    )
                    return

                # Registrar a posição inicial do tripulante na tabela Crew_Position
                insert_position_query = """INSERT INTO Crew_Position (Crew_ID, Current_Location) VALUES (?, ?)"""
                cursor.execute(insert_position_query, (crew_id, arrival_point))
                db_connection.commit()

            else:
                # Verificar se o ponto de partida coincide com a localização atual
                current_location = position_data[0]
                if departure_point != current_location:
                    messagebox.showerror(
                        "Erro",
                        f"O tripulante não pode partir de {departure_point} porque está localizado em {current_location}."
                    )
                    return
                # Atualizar a posição do tripulante após o voo
                update_position_query = """
                UPDATE Crew_Position
                SET Current_Location = ?
                WHERE Crew_ID = ?
                """
                cursor.execute(update_position_query, (arrival_point, crew_id))


            # Inserir membro da tripulação no voo
            query_insert_crew = """
            INSERT INTO Flight_Crew (Flight_ID, Crew_ID)
            VALUES (?, ?)
            """
            cursor.execute(query_insert_crew, (flight_id, crew_id))
            db_connection.commit()
            cursor.close()

            # Adicionar ao listbox e limpar seleção
            crew_listbox.insert(END, selected_crew)
            crew_var.set("")

            # Verificar contagem da tripulação
            verify_crew_count()
        except pdbc.Error as e:
            messagebox.showerror("Erro", f"Erro ao adicionar tripulante: {e}")

    # Verificar se a tripulação mínima foi alcançada
    def verify_crew_count():
        try:
            cursor = db_connection.cursor()
            query = "SELECT COUNT(*) FROM Flight_Crew WHERE Flight_ID = ?"
            cursor.execute(query, (flight_id,))
            crew_count = cursor.fetchone()[0]
            cursor.close()

            if crew_count >= min_crew_required:
                if messagebox.askyesno("Tripulação Completa", "Tripulação mínima atingida. Deseja sair?"):
                    add_crew_window.destroy()
                # Ativar o botão de fechar se a tripulação mínima for atingida
                close_button.config(state="normal")
            else:
                # Desativar o botão de fechar se a tripulação mínima não for atingida
                close_button.config(state="disabled")
        except pdbc.Error as e:
            messagebox.showerror("Erro", f"Erro ao verificar tripulação: {e}")

    # Botão para adicionar tripulante
    ttk.Button(add_crew_window, text="Adicionar Tripulante", command=add_crew_member).pack(pady=10)

    close_button = ttk.Button(add_crew_window, text="Fechar", command=add_crew_window.destroy, state="disabled")
    close_button.pack(pady=10)

def open_delete_flight_window():
    delete_flight_window = Toplevel()
    delete_flight_window.title("Deletar Voo")
    delete_flight_window.geometry("400x200")

    Label(delete_flight_window, text="Selecione o Voo para Deletar:").pack(pady=10, anchor="w")

    flight_var = StringVar()
    flight_combobox = ttk.Combobox(delete_flight_window, textvariable=flight_var)
    flight_combobox.pack(pady=5, fill="x")

    # Load available flights
    try:
        cursor = db_connection.cursor()
        cursor.execute("SELECT Flight_ID FROM Flights_TB")
        flights = cursor.fetchall()
        cursor.close()

        # Populate the combobox with flight IDs
        flight_combobox["values"] = [flight[0] for flight in flights]
    except pdbc.Error as e:
        messagebox.showerror("Erro", f"Erro ao carregar voos: {e}")
        delete_flight_window.destroy()
        return

    def delete_flight():
        flight_id = flight_var.get()

        if not flight_id:
            messagebox.showerror("Erro", "Selecione um voo para deletar.")
            return

        try:
            cursor = db_connection.cursor()

            # Delete from Flight_Crew table
            delete_crew_query = "DELETE FROM Flight_Crew WHERE Flight_ID = ?"
            cursor.execute(delete_crew_query, (flight_id,))

            # Delete from Flights_TB table
            delete_flight_query = "DELETE FROM Flights_TB WHERE Flight_ID = ?"
            cursor.execute(delete_flight_query, (flight_id,))

            db_connection.commit()
            cursor.close()

            messagebox.showinfo("Sucesso", f"Voo {flight_id} deletado com sucesso.")
            delete_flight_window.destroy()
        except pdbc.Error as e:
            messagebox.showerror("Erro", f"Erro ao deletar voo: {e}")

    ttk.Button(delete_flight_window, text="Deletar Voo", command=delete_flight).pack(pady=10)
    ttk.Button(delete_flight_window, text="Cancelar", command=delete_flight_window.destroy).pack(pady=5)

# Botão para atualizar os dados da tabela
ttk.Button(Flight_Page, text="Atualizar Dados", command=load_flight_data).pack(pady=10)

# Botão para abrir a janela de adicionar voos
ttk.Button(Flight_Page, text="Adicionar Novo Voo", command=open_add_flight_page).pack(pady=10)

# Botão para abrir a janela de remover voos
ttk.Button(Flight_Page, text="Deletar Voo", command=open_delete_flight_window).pack(pady=10)

# Botão para retornar ao menu principal
ttk.Button(Flight_Page, text="Voltar ao Menu Principal", command=lambda: show_frame(main_menu)).pack(pady=10)

#TODO: Application layer here must make sure of a number of things
#A: The application must have an extra column that shows the count of crew assigned to the flight
#B: When creating the flight, after inputing all the data, it progresses to a window interacting with the hidden Flight_Crew Table, automatically assigned to the current flight ID, to allow one to use dropdowns to select the crew. They must be allowed to make multiple selections
#C: The user cannot be allowed to leave the crew selection window until the minimum crew has been assigned, based on the aircraft_crew column
#D: A button can open the crew assignment window again
#E: Crew selection has to be from both pilots and attendants.
#F: The extra column must update to show the count of crew assigned to a flight by selecting the count from Flight_Crew_TB based on flight ID.

# Page 2
def load_aircraft_data():
    for row in aircraft_tree.get_children():
        aircraft_tree.delete(row)

    # Chama dados do banco
    try:
        cursor = db_connection.cursor()
        query = """
        SELECT * FROM Aircraft_TB
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        for row in rows:
            aircraft_id = row[0]
            aircraft_model = row[1]
            aircraft_base = row[2]
            aircraft_type = row[3]
            aircraft_crew = row[4]
            aircraft_maxcap = row[5]
            aircraft_fuelburn = float(row[6])  # Converte para float
            aircraft_status = row[7]

            aircraft_tree.insert("", "end", values=(
                aircraft_id,
                aircraft_model,
                aircraft_base,
                aircraft_type,
                aircraft_crew,
                aircraft_maxcap,
                f"{aircraft_fuelburn:.2f}",  # Formata para 2 casas decimais
                aircraft_status
            ))

        cursor.close()
    except pdbc.Error as e:
        messagebox.showerror("Erro", f"Erro ao carregar dados das aeronaves: {e}")

columns = (
    "Aircraft_ID", "Aircraft_Model", "Aircraft_Base", "Aircraft_Type", 
    "Aircraft_Crew", "Aircraft_MaxCap", "Aircraft_FuelBurn", "Aircraft_Status"
)
aircraft_tree = ttk.Treeview(Aircraft_Page, columns=columns, show="headings")
aircraft_tree.pack(pady=10, fill="both", expand=True)

# Configuração das colunas do Treeview
aircraft_tree.heading("Aircraft_ID", text="ID")
aircraft_tree.heading("Aircraft_Model", text="Modelo")
aircraft_tree.heading("Aircraft_Base", text="Base")
aircraft_tree.heading("Aircraft_Type", text="Tipo")
aircraft_tree.heading("Aircraft_Crew", text="Tripulação")
aircraft_tree.heading("Aircraft_MaxCap", text="Capacidade Máxima")
aircraft_tree.heading("Aircraft_FuelBurn", text="Consumo de Combustível")
aircraft_tree.heading("Aircraft_Status", text="Status")

# Alinhamento e largura das colunas
aircraft_tree.column("Aircraft_ID", width=50, anchor="center")
aircraft_tree.column("Aircraft_Model", width=150, anchor="w")
aircraft_tree.column("Aircraft_Base", width=70, anchor="center")
aircraft_tree.column("Aircraft_Type", width=100, anchor="w")
aircraft_tree.column("Aircraft_Crew", width=100, anchor="center")
aircraft_tree.column("Aircraft_MaxCap", width=150, anchor="center")
aircraft_tree.column("Aircraft_FuelBurn", width=150, anchor="e")
aircraft_tree.column("Aircraft_Status", width=100, anchor="w")

# Abre a janela para adicionar aeronaves
def open_add_aircraft_page():
    add_aircraft_window = Toplevel(Aircraft_Page)
    add_aircraft_window.title("Adicionar Nova Aeronave")
    add_aircraft_window.geometry("400x600")

    # Variáveis para armazenar os dados para inserção
    id_var = StringVar()
    model_var = StringVar()
    base_var = StringVar()
    type_var = StringVar()
    crew_var = IntVar()
    maxcap_var = IntVar()
    fuelburn_var = DoubleVar()
    status_var = StringVar()

    # Busca os IDs de bases para preencher a combobox de seleção
    try:
        cursor = db_connection.cursor()
        cursor.execute("SELECT Airport_ID FROM Serviced_Locations_TB")
        airport_ids = [row[0] for row in cursor.fetchall()]
        cursor.close()
    except pdbc.Error as e:
        messagebox.showerror("Erro", f"Erro ao carregar bases: {e}")
        return

    # Labels e widgets
    Label(add_aircraft_window, text="ID da Aeronave:").pack(pady=5, anchor="w")
    Entry(add_aircraft_window, textvariable=id_var).pack(pady=5, fill="x")

    Label(add_aircraft_window, text="Modelo:").pack(pady=5, anchor="w")
    Entry(add_aircraft_window, textvariable=model_var).pack(pady=5, fill="x")

    Label(add_aircraft_window, text="Base:").pack(pady=5, anchor="w")
    base_combobox = Combobox(add_aircraft_window, textvariable=base_var, values=airport_ids, state="readonly")
    base_combobox.pack(pady=5, fill="x")

    Label(add_aircraft_window, text="Tipo:").pack(pady=5, anchor="w")
    Entry(add_aircraft_window, textvariable=type_var).pack(pady=5, fill="x")

    Label(add_aircraft_window, text="Tripulação:").pack(pady=5, anchor="w")
    Entry(add_aircraft_window, textvariable=crew_var).pack(pady=5, fill="x")

    Label(add_aircraft_window, text="Capacidade Máxima:").pack(pady=5, anchor="w")
    Entry(add_aircraft_window, textvariable=maxcap_var).pack(pady=5, fill="x")

    Label(add_aircraft_window, text="Consumo de Combustível:").pack(pady=5, anchor="w")
    Entry(add_aircraft_window, textvariable=fuelburn_var).pack(pady=5, fill="x")

    Label(add_aircraft_window, text="Status:").pack(pady=5, anchor="w")
    status_combobox = Combobox(
    add_aircraft_window, 
    textvariable=status_var, 
    values=["Operacional", "Em Manutenção", "Indisponível"], 
    state="readonly"
    )
    status_combobox.pack(pady=5, fill="x")

    # Função para adicionar a aeronave
    def add_aircraft():
        aircraft_id = id_var.get()
        model = model_var.get()
        base = base_var.get()
        aircraft_type = type_var.get()
        crew = crew_var.get()
        maxcap = maxcap_var.get()
        fuelburn = fuelburn_var.get()
        status = status_var.get()

        # Valida os inputs
        if not aircraft_id or not model or not base or not aircraft_type or not status or crew <= 0 or maxcap <= 0 or fuelburn <= 0:
            messagebox.showerror("Erro", "Por favor, preencha todos os campos corretamente.")
            return

        # Insere os dados no banco de dados
        try:
            cursor = db_connection.cursor()
            query = """
            INSERT INTO Aircraft_TB (Aircraft_ID, Aircraft_Model, Aircraft_Base, Aircraft_Type, Aircraft_Crew, Aircraft_MaxCap, Aircraft_FuelBurn, Aircraft_Status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(query, (aircraft_id, model, base, aircraft_type, crew, maxcap, fuelburn, status))
            db_connection.commit()
            cursor.close()
            messagebox.showinfo("Sucesso", "Aeronave adicionada com sucesso!")

            # Limpa os campos
            id_var.set("")
            model_var.set("")
            base_var.set("")
            type_var.set("")
            crew_var.set(0)
            maxcap_var.set(0)
            fuelburn_var.set(0.0)
            status_var.set("")

            # Atualiza a tabela principal
            load_aircraft_data()
        except pdbc.Error as e:
            messagebox.showerror("Erro", f"Erro ao adicionar aeronave: {e}")

    # Botões
    ttk.Button(add_aircraft_window, text="Adicionar Aeronave", command=add_aircraft).pack(pady=20)
    ttk.Button(add_aircraft_window, text="Fechar", command=add_aircraft_window.destroy).pack(pady=10)

def open_delete_aircraft_window():
    # Novo Toplevel
    delete_aircraft_window = Toplevel(Aircraft_Page)
    delete_aircraft_window.title("Deletar Aeronave")
    delete_aircraft_window.geometry("300x200")

    # Variável para o ID a ser removido
    aircraft_id_var = StringVar()

    Label(delete_aircraft_window, text="ID da Aeronave:").pack(pady=10, anchor="w")
    Entry(delete_aircraft_window, textvariable=aircraft_id_var).pack(pady=5, fill="x")

    # Função que executa a remoção dos dados
    def delete_aircraft():
        aircraft_id = aircraft_id_var.get()

        # Valida input
        if not aircraft_id:
            messagebox.showerror("Erro", "Por favor, insira um ID de aeronave válido.")
            return

        # Tenta remover o dado do banco
        try:
            cursor = db_connection.cursor()
            query = "DELETE FROM Aircraft_TB WHERE Aircraft_ID = ?"
            cursor.execute(query, (aircraft_id,))
            if cursor.rowcount == 0:
                messagebox.showerror("Erro", "Nenhuma aeronave encontrada com este ID.")
            else:
                db_connection.commit()
                messagebox.showinfo("Sucesso", "Aeronave deletada com sucesso!")
                load_aircraft_data()  # Atualiza os dados na tabela principal
            cursor.close()
        except pdbc.Error as e:
            messagebox.showerror("Erro", f"Erro ao deletar aeronave: {e}")

    # Botão para confirmar o pedido de remoção
    ttk.Button(delete_aircraft_window, text="Deletar Aeronave", command=delete_aircraft).pack(pady=20)

    ttk.Button(delete_aircraft_window, text="Fechar", command=delete_aircraft_window.destroy).pack(pady=10)

def open_change_status_window():
    # Novo Toplevel
    change_status_window = Toplevel(Aircraft_Page)
    change_status_window.title("Alterar Status da Aeronave")
    change_status_window.geometry("300x300")

    # Variáveis
    aircraft_id_var = StringVar()
    new_status_var = StringVar()

    # Busca os IDs de aeronaves para preencher o combobox
    try:
        cursor = db_connection.cursor()
        cursor.execute("SELECT Aircraft_ID FROM Aircraft_TB")
        aircraft_ids = [row[0] for row in cursor.fetchall()]
        cursor.close()
    except pdbc.Error as e:
        messagebox.showerror("Erro", f"Erro ao carregar IDs de aeronaves: {e}")
        return

    # Labels e widgets
    Label(change_status_window, text="Selecione a Aeronave:").pack(pady=10, anchor="w")
    aircraft_id_combobox = Combobox(change_status_window, textvariable=aircraft_id_var, values=aircraft_ids, state="readonly")
    aircraft_id_combobox.pack(pady=5, fill="x")

    Label(change_status_window, text="Novo Status:").pack(pady=10, anchor="w")
    status_combobox = Combobox(
        change_status_window,
        textvariable=new_status_var,
        values=["Operacional", "Em Manutenção", "Indisponível"],
        state="readonly"
    )
    status_combobox.pack(pady=5, fill="x")

    # Função para alterar o status
    def change_aircraft_status():
        aircraft_id = aircraft_id_var.get()
        new_status = new_status_var.get()

        # Validação dos inputs
        if not aircraft_id or not new_status:
            messagebox.showerror("Erro", "Por favor, selecione um ID de aeronave e um novo status.")
            return

        # Tenta atualizar o status no banco
        try:
            cursor = db_connection.cursor()
            query = "UPDATE Aircraft_TB SET Aircraft_Status = ? WHERE Aircraft_ID = ?"
            cursor.execute(query, (new_status, aircraft_id))
            if cursor.rowcount == 0:
                messagebox.showerror("Erro", "Nenhuma aeronave encontrada com este ID.")
            else:
                db_connection.commit()
                messagebox.showinfo("Sucesso", "Status da aeronave atualizado com sucesso!")
                load_aircraft_data()  # Atualiza a tabela principal
            cursor.close()
        except pdbc.Error as e:
            messagebox.showerror("Erro", f"Erro ao alterar status da aeronave: {e}")

    # Botões
    ttk.Button(change_status_window, text="Alterar Status", command=lambda: (change_aircraft_status(), change_status_window.destroy())).pack(pady=20)
    ttk.Button(change_status_window, text="Fechar", command=change_status_window.destroy).pack(pady=10)

# Botão para atualizar dados
ttk.Button(Aircraft_Page, text="Atualizar Dados", command=load_aircraft_data).pack(pady=10)

# Botão para abrir a janela de adicionar aeronaves
ttk.Button(Aircraft_Page, text="Adicionar Nova Aeronave", command=open_add_aircraft_page).pack(pady=10)

# Botão para abrir a janela de alteração de status
ttk.Button(Aircraft_Page, text="Alterar Status da Aeronave", command=open_change_status_window).pack(pady=10)

# Botão para abrir a janela de remover aeronaves
ttk.Button(Aircraft_Page, text="Remover Aeronave", command=open_delete_aircraft_window).pack(pady=10)

# Botão para retornar ao menu principal
ttk.Button(Aircraft_Page, text="Voltar ao Menu Principal", command=lambda: show_frame(main_menu)).pack(pady=10)

# Carregar os dados quando a página é carregada
Aircraft_Page.bind("<Visibility>", lambda e: load_aircraft_data())


# Page 3
def load_pilot_data():
    for row in pilot_tree.get_children():
        pilot_tree.delete(row)
    
    # Chama dados do banco
    try:
        cursor = db_connection.cursor()
        query = """
        SELECT * FROM Pilots_TB
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        
        for row in rows:
            #Valores da tabela são transferidos para variáveis para impedir problemas de formatação, como o nome se divindo em duas colunas
            pilot_id = row[0]
            pilot_name = row[1]
            pilot_age = row[2]
            pilot_boo = row[3]
            pilot_rank = row[4]
            
            #Formatação do salário de decimal para float para que ele seja mostrado de forma correta na tabela
            try:
                pilot_salary = float(row[5])
            except ValueError:
                pilot_salary = 0.0#Lida com casos em que o dado salarial esteja faltando ou corrompido
                
            pilot_experience = row[6]

            #Insere os dados formatados corretamente na Treeview
            pilot_tree.insert("", "end", values=(
                pilot_id, 
                pilot_name, 
                pilot_age, 
                pilot_boo, 
                pilot_rank, 
                f"R$ {pilot_salary:,.2f}",  #Formata o salário com 2 pontos decimais e o simbolo de moeda
                pilot_experience
            ))

        cursor.close()
    except pdbc.Error as e:
        messagebox.showerror("Erro", f"Erro ao carregar dados dos pilotos: {e}")

columns = ("Pilot_ID", "Pilot_Name", "Pilot_Age", "Pilot_BOO", "Pilot_Rank", "Pilot_Salary", "Pilot_Experience")
pilot_tree = ttk.Treeview(Pilot_Page, columns=columns, show="headings")
pilot_tree.pack(pady=10, fill="both", expand=True)

#os nomes das colunas
pilot_tree.heading("Pilot_ID", text="ID")
pilot_tree.heading("Pilot_Name", text="Nome")
pilot_tree.heading("Pilot_Age", text="Idade")
pilot_tree.heading("Pilot_BOO", text="Base")
pilot_tree.heading("Pilot_Rank", text="Patente")
pilot_tree.heading("Pilot_Salary", text="Salário")
pilot_tree.heading("Pilot_Experience", text="Horas de Experiência")

#Alinhamento e largura das colunas
pilot_tree.column("Pilot_ID", width=50, anchor="center")
pilot_tree.column("Pilot_Name", width=150, anchor="w")
pilot_tree.column("Pilot_Age", width=70, anchor="center")
pilot_tree.column("Pilot_BOO", width=70, anchor="center")
pilot_tree.column("Pilot_Rank", width=100, anchor="w")
pilot_tree.column("Pilot_Salary", width=100, anchor="e")
pilot_tree.column("Pilot_Experience", width=150, anchor="center")

#Abre a Janela para adicionar pilotos
def open_add_pilot_page():
    #Abre um novo toplevel/iframe
    add_pilot_window = Toplevel(Pilot_Page)
    add_pilot_window.title("Add New Pilot")
    add_pilot_window.geometry("400x600")

    #Variáveis para armazenar os dados para inserção na tabela
    name_var = StringVar()
    age_var = IntVar()
    boo_var = StringVar()
    rank_var = StringVar()
    salary_var = DoubleVar()
    experience_var = IntVar()

    #Busca os IDs de aeroportos para preencher a combobox de seleção
    try:
        cursor = db_connection.cursor()
        cursor.execute("SELECT Airport_ID FROM Serviced_Locations_TB")
        airport_ids = [row[0] for row in cursor.fetchall()]
        cursor.close()
    except pdbc.Error as e:
        messagebox.showerror("Erro", f"Erro ao carregar locais de serviço: {e}")
        return

    #labels e widgets
    Label(add_pilot_window, text="Nome:").pack(pady=5, anchor="w")
    Entry(add_pilot_window, textvariable=name_var).pack(pady=5, fill="x")

    Label(add_pilot_window, text="Idade:").pack(pady=5, anchor="w")
    Entry(add_pilot_window, textvariable=age_var).pack(pady=5, fill="x")

    Label(add_pilot_window, text="Base (BOO):").pack(pady=5, anchor="w")
    boo_combobox = Combobox(add_pilot_window, textvariable=boo_var, values=airport_ids, state="readonly")
    boo_combobox.pack(pady=5, fill="x")

    Label(add_pilot_window, text="Patente:").pack(pady=5, anchor="w")
    Entry(add_pilot_window, textvariable=rank_var).pack(pady=5, fill="x")

    Label(add_pilot_window, text="Salário:").pack(pady=5, anchor="w")
    Entry(add_pilot_window, textvariable=salary_var).pack(pady=5, fill="x")

    Label(add_pilot_window, text="Horas de Experiência:").pack(pady=5, anchor="w")
    Entry(add_pilot_window, textvariable=experience_var).pack(pady=5, fill="x")

    #Função para pegar os dados do formulário para inserção na tabela
    def add_pilot():
        name = name_var.get()
        age = age_var.get()
        boo = boo_var.get()
        rank = rank_var.get()
        salary = salary_var.get()
        experience = experience_var.get()

        #valida os inputs
        if not name or not boo or not rank or age <= 0 or salary < 0 or experience < 0:
            messagebox.showerror("Erro", "Por favor, preencha todos os campos corretamente.")
            return

        #Insere os dados no banco de dados
        try:
            cursor = db_connection.cursor()
            query = """
            INSERT INTO Pilots_TB (Pilot_Name, Pilot_Age, Pilot_BOO, Pilot_Rank, Pilot_Salary, Pilot_Experience)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            cursor.execute(query, (name, age, boo, rank, salary, experience))
            db_connection.commit()
            cursor.close()
            messagebox.showinfo("Sucesso", "Piloto adicionado com sucesso!")

            #apaga os dados anteriores para próxima inserção
            name_var.set("")
            age_var.set(0)
            boo_var.set("")
            rank_var.set("")
            salary_var.set(0.0)
            experience_var.set(0)

            #Atualiza a tabela principal
            load_pilot_data()
        except pdbc.Error as e:
            messagebox.showerror("Erro", f"Erro ao adicionar comissário(a): {e}")

    #Botão para confirmar os dados para inserção
    ttk.Button(add_pilot_window, text="Adicionar Piloto", command=add_pilot).pack(pady=20)

    #botão para fechar a janela
    ttk.Button(add_pilot_window, text="Fechar", command=add_pilot_window.destroy).pack(pady=10)
#Abre a janela para remover dados
def open_delete_pilot_window():
    #Novo Toplevel
    delete_pilot_window = Toplevel(Pilot_Page)
    delete_pilot_window.title("Deletar Piloto")
    delete_pilot_window.geometry("300x200")

    #Variável para o id a ser removido
    pilot_id_var = IntVar()

    Label(delete_pilot_window, text="ID do Piloto:").pack(pady=10, anchor="w")
    Entry(delete_pilot_window, textvariable=pilot_id_var).pack(pady=5, fill="x")

    #Função que executa a remoção dos dados
    def delete_pilot():
        pilot_id = pilot_id_var.get()

        #valida input
        if pilot_id <= 0:
            messagebox.showerror("Erro", "Por favor, insira um ID de comissário(a) válido.")
            return

        #Tenta remover o dado do banco
        try:
            cursor = db_connection.cursor()
            query = "DELETE FROM Pilots_TB WHERE Pilot_ID = ?"
            cursor.execute(query, (pilot_id,))
            if cursor.rowcount == 0:
                messagebox.showerror("Erro", "Nenhum comissário(a) encontrado com este ID.")
            else:
                db_connection.commit()
                messagebox.showinfo("Sucesso", "Piloto deletado com sucesso!")
                load_pilot_data()  #Atualiza os dados na tabela principal
            cursor.close()
        except pdbc.Error as e:
            messagebox.showerror("Erro", f"Erro ao deletar comissário(a): {e}")

    #Botão para confirmar o pedido de remoção
    ttk.Button(delete_pilot_window, text="Deletar Piloto", command=delete_pilot).pack(pady=20)

    ttk.Button(delete_pilot_window, text="Fechar", command=delete_pilot_window.destroy).pack(pady=10)

#Botão para atualizar dados
ttk.Button(Pilot_Page, text="Atualizar Dados", command=load_pilot_data).pack(pady=10)

#Botão para abrir a janela de adicionar pilotos
ttk.Button(Pilot_Page, text="Adicionar Novo Piloto", command=open_add_pilot_page).pack(pady=10)

#Botão para abrir a janela de remover pilotos
ttk.Button(Pilot_Page, text="Deletar Piloto", command=open_delete_pilot_window).pack(pady=10)

#botão para retornar ao menu principal
ttk.Button(Pilot_Page, text="Voltar ao Menu Principal", command=lambda: show_frame(main_menu)).pack(pady=10)

#Carregar os dados quando a pagina é carregada
Pilot_Page.bind("<Visibility>", lambda e: load_pilot_data())

# Page 4
def load_attendant_data():
    for row in attendant_tree.get_children():
        attendant_tree.delete(row)
    
    # Chama dados do banco
    try:
        cursor = db_connection.cursor()
        query = """
        SELECT * FROM Attendant_TB
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        
        for row in rows:
            #Valores da tabela são transferidos para variáveis para impedir problemas de formatação, como o nome se divindo em duas colunas
            attendant_id = row[0]
            attendant_name = row[1]
            attendant_age = row[2]
            attendant_boo = row[3]
            
            #Formatação do salário de decimal para float para que ele seja mostrado de forma correta na tabela
            try:
                attendant_salary = float(row[4])
            except ValueError:
                attendant_salary = 0.0#Lida com casos em que o dado salarial esteja faltando ou corrompido

            #Insere os dados formatados corretamente na Treeview
            attendant_tree.insert("", "end", values=(
                attendant_id, 
                attendant_name, 
                attendant_age, 
                attendant_boo, 
                f"R$ {attendant_salary:,.2f}",  #Formata o salário com 2 pontos decimais e o simbolo de moeda
            ))

        cursor.close()
    except pdbc.Error as e:
        messagebox.showerror("Erro", f"Erro ao carregar dados dos(as) comissários(as): {e}")

columns = ("Attendant_ID", "Attendant_Name", "Attendant_Age", "Attendant_BOO", "Attendant_Salary")
attendant_tree = ttk.Treeview(Attendant_Page, columns=columns, show="headings")
attendant_tree.pack(pady=10, fill="both", expand=True)

#os nomes das colunas
attendant_tree.heading("Attendant_ID", text="ID")
attendant_tree.heading("Attendant_Name", text="Nome")
attendant_tree.heading("Attendant_Age", text="Idade")
attendant_tree.heading("Attendant_BOO", text="Base")
attendant_tree.heading("Attendant_Salary", text="Salário")

#Alinhamento e largura das colunas
attendant_tree.column("Attendant_ID", width=50, anchor="center")
attendant_tree.column("Attendant_Name", width=150, anchor="w")
attendant_tree.column("Attendant_Age", width=70, anchor="center")
attendant_tree.column("Attendant_BOO", width=70, anchor="center")
attendant_tree.column("Attendant_Salary", width=100, anchor="e")

#Abre a Janela para adicionar registros
def open_add_attendant_page():
    #Abre um novo toplevel/iframe
    add_attendant_window = Toplevel(Attendant_Page)
    add_attendant_window.title("Adicionar novo comissário")
    add_attendant_window.geometry("400x600")

    #Variáveis para armazenar os dados para inserção na tabela
    name_var = StringVar()
    age_var = IntVar()
    boo_var = StringVar()
    salary_var = DoubleVar()

    #Busca os IDs de aeroportos para preencher a combobox de seleção
    try:
        cursor = db_connection.cursor()
        cursor.execute("SELECT Airport_ID FROM Serviced_Locations_TB")
        airport_ids = [row[0] for row in cursor.fetchall()]
        cursor.close()
    except pdbc.Error as e:
        messagebox.showerror("Erro", f"Erro ao carregar locais de serviço: {e}")
        return

    #labels e widgets
    Label(add_attendant_window, text="Nome:").pack(pady=5, anchor="w")
    Entry(add_attendant_window, textvariable=name_var).pack(pady=5, fill="x")

    Label(add_attendant_window, text="Idade:").pack(pady=5, anchor="w")
    Entry(add_attendant_window, textvariable=age_var).pack(pady=5, fill="x")

    Label(add_attendant_window, text="Base (BOO):").pack(pady=5, anchor="w")
    boo_combobox = Combobox(add_attendant_window, textvariable=boo_var, values=airport_ids, state="readonly")
    boo_combobox.pack(pady=5, fill="x")

    Label(add_attendant_window, text="Salário:").pack(pady=5, anchor="w")
    Entry(add_attendant_window, textvariable=salary_var).pack(pady=5, fill="x")

    #Função para pegar os dados do formulário para inserção na tabela
    def add_attendant():
        name = name_var.get()
        age = age_var.get()
        boo = boo_var.get()
        salary = salary_var.get()

        #valida os inputs
        if not name or not boo or age <= 0 or salary < 0:
            messagebox.showerror("Erro", "Por favor, preencha todos os campos corretamente.")
            return

        #Insere os dados no banco de dados
        try:
            cursor = db_connection.cursor()
            query = """
            INSERT INTO Attendant_TB (Attendant_Name, Attendant_Age, Attendant_BOO, Attendant_Salary)
            VALUES (?, ?, ?, ?)
            """
            cursor.execute(query, (name, age, boo, salary))
            db_connection.commit()
            cursor.close()
            messagebox.showinfo("Sucesso", "Comissário adicionado com sucesso!")

            #apaga os dados anteriores para próxima inserção
            name_var.set("")
            age_var.set(0)
            boo_var.set("")
            salary_var.set(0.0)

            #Atualiza a tabela principal
            load_attendant_data()
        except pdbc.Error as e:
            messagebox.showerror("Erro", f"Erro ao adicionar comissário: {e}")

    #Botão para confirmar os dados para inserção
    ttk.Button(add_attendant_window, text="Adicionar Comissário(a)", command=add_attendant).pack(pady=20)

    #botão para fechar a janela
    ttk.Button(add_attendant_window, text="Fechar", command=add_attendant_window.destroy).pack(pady=10)
#Abre a janela para remover dados
def open_delete_attendant_window():
    #Novo Toplevel
    delete_attendant_window = Toplevel(Attendant_Page)
    delete_attendant_window.title("Deletar Comissário(a)")
    delete_attendant_window.geometry("300x200")

    #Variável para o id a ser removido
    attendant_id_var = IntVar()

    Label(delete_attendant_window, text="ID do(a) comissário(a):").pack(pady=10, anchor="w")
    Entry(delete_attendant_window, textvariable=attendant_id_var).pack(pady=5, fill="x")

    #Função que executa a remoção dos dados
    def delete_attendant():
        attendant_id = attendant_id_var.get()

        #valida input
        if attendant_id <= 0:
            messagebox.showerror("Erro", "Por favor, insira um ID de comissário válido.")
            return

        #Tenta remover o dado do banco
        try:
            cursor = db_connection.cursor()
            query = "DELETE FROM Attendant_TB WHERE Attendant_ID = ?"
            cursor.execute(query, (attendant_id,))
            if cursor.rowcount == 0:
                messagebox.showerror("Erro", "Nenhum comissário(a) encontrado com este ID.")
            else:
                db_connection.commit()
                messagebox.showinfo("Sucesso", "comissário(a) deletado com sucesso!")
                load_pilot_data()  #Atualiza os dados na tabela principal
            cursor.close()
        except pdbc.Error as e:
            messagebox.showerror("Erro", f"Erro ao deletar comissário(a): {e}")

    #Botão para confirmar o pedido de remoção
    ttk.Button(delete_attendant_window, text="Deletar Comissário(a)", command=delete_attendant).pack(pady=20)

    ttk.Button(delete_attendant_window, text="Fechar", command=delete_attendant_window.destroy).pack(pady=10)

#Botão para atualizar dados
ttk.Button(Attendant_Page, text="Atualizar Dados", command=load_attendant_data).pack(pady=10)

#Botão para abrir a janela de adicionar registros
ttk.Button(Attendant_Page, text="Adicionar Novo(a) Comissário(a)", command=open_add_attendant_page).pack(pady=10)

#Botão para abrir a janela de remover registros
ttk.Button(Attendant_Page, text="Deletar Comissário(a)", command=open_delete_attendant_window).pack(pady=10)

#botão para retornar ao menu principal
ttk.Button(Attendant_Page, text="Voltar ao Menu Principal", command=lambda: show_frame(main_menu)).pack(pady=10)

# Page 5
# ttk.Label(GCrew_Page, text="Mecânico/as", font=("Arial", 16)).pack(pady=20)
# ttk.Button(GCrew_Page, text="Voltar ao Menu Principal", command=lambda: show_frame(main_menu)).pack(pady=10)
def load_gcrew_data():
    for row in gcrew_tree.get_children():
        gcrew_tree.delete(row)

    # Chama dados do banco
    try:
        cursor = db_connection.cursor()
        query = """
        SELECT * FROM Mechanics_TB
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        for row in rows:
            # Transfere valores da tabela para variáveis
            mechanics_id = row[0]
            mechanics_name = row[1]
            mechanics_age = row[2]
            mechanics_boo = row[3]
            mechanics_function = row[4]
            
            # Formata salário
            try:
                mechanics_salary = float(row[5])
            except ValueError:
                mechanics_salary = 0.0

            # Insere os dados formatados na Treeview
            gcrew_tree.insert("", "end", values=(
                mechanics_id,
                mechanics_name,
                mechanics_age,
                mechanics_boo,
                mechanics_function,
                f"R$ {mechanics_salary:,.2f}"
            ))

        cursor.close()
    except pdbc.Error as e:
        messagebox.showerror("Erro", f"Erro ao carregar dados da equipe de manutenção: {e}")

columns = ("Mechanics_ID", "Mechanics_Name", "Mechanics_Age", "Mechanics_BOO", "Mechanics_Function", "Mechanics_Salary")
gcrew_tree = ttk.Treeview(GCrew_Page, columns=columns, show="headings")
gcrew_tree.pack(pady=10, fill="both", expand=True)

# Configuração dos nomes das colunas
gcrew_tree.heading("Mechanics_ID", text="ID")
gcrew_tree.heading("Mechanics_Name", text="Nome")
gcrew_tree.heading("Mechanics_Age", text="Idade")
gcrew_tree.heading("Mechanics_BOO", text="Base")
gcrew_tree.heading("Mechanics_Function", text="Função")
gcrew_tree.heading("Mechanics_Salary", text="Salário")

# Alinhamento e largura das colunas
gcrew_tree.column("Mechanics_ID", width=50, anchor="center")
gcrew_tree.column("Mechanics_Name", width=150, anchor="w")
gcrew_tree.column("Mechanics_Age", width=70, anchor="center")
gcrew_tree.column("Mechanics_BOO", width=70, anchor="center")
gcrew_tree.column("Mechanics_Function", width=100, anchor="w")
gcrew_tree.column("Mechanics_Salary", width=100, anchor="e")

# Abre a janela para adicionar membros da equipe de manutenção
def open_add_gcrew_page():
    add_gcrew_window = Toplevel(GCrew_Page)
    add_gcrew_window.title("Adicionar Novo Membro da Equipe de Manutenção")
    add_gcrew_window.geometry("400x500")

    # Variáveis para os dados
    name_var = StringVar()
    age_var = IntVar()
    boo_var = StringVar()
    function_var = StringVar()
    salary_var = DoubleVar()

    # Carrega as bases
    try:
        cursor = db_connection.cursor()
        cursor.execute("SELECT Airport_ID FROM Serviced_Locations_TB")
        airport_ids = [row[0] for row in cursor.fetchall()]
        cursor.close()
    except pdbc.Error as e:
        messagebox.showerror("Erro", f"Erro ao carregar locais de serviço: {e}")
        return

    # Widgets do formulário
    Label(add_gcrew_window, text="Nome:").pack(pady=5, anchor="w")
    Entry(add_gcrew_window, textvariable=name_var).pack(pady=5, fill="x")

    Label(add_gcrew_window, text="Idade:").pack(pady=5, anchor="w")
    Entry(add_gcrew_window, textvariable=age_var).pack(pady=5, fill="x")

    Label(add_gcrew_window, text="Base (BOO):").pack(pady=5, anchor="w")
    boo_combobox = Combobox(add_gcrew_window, textvariable=boo_var, values=airport_ids, state="readonly")
    boo_combobox.pack(pady=5, fill="x")

    Label(add_gcrew_window, text="Função:").pack(pady=5, anchor="w")
    Entry(add_gcrew_window, textvariable=function_var).pack(pady=5, fill="x")

    Label(add_gcrew_window, text="Salário:").pack(pady=5, anchor="w")
    Entry(add_gcrew_window, textvariable=salary_var).pack(pady=5, fill="x")

    def add_gcrew_member():
        name = name_var.get()
        age = age_var.get()
        boo = boo_var.get()
        function = function_var.get()
        salary = salary_var.get()

        # Valida inputs
        if not name or not boo or not function or age <= 0 or salary < 0:
            messagebox.showerror("Erro", "Por favor, preencha todos os campos corretamente.")
            return

        # Insere no banco
        try:
            cursor = db_connection.cursor()
            query = """
            INSERT INTO Mechanics_TB (Mechanics_Name, Mechanics_Age, Mechanics_BOO, Mechanics_Function, Mechanics_Salary)
            VALUES (?, ?, ?, ?, ?)
            """
            cursor.execute(query, (name, age, boo, function, salary))
            db_connection.commit()
            cursor.close()
            messagebox.showinfo("Sucesso", "Membro adicionado com sucesso!")

            # Limpa os campos
            name_var.set("")
            age_var.set(0)
            boo_var.set("")
            function_var.set("")
            salary_var.set(0.0)

            # Atualiza a tabela
            load_gcrew_data()
        except pdbc.Error as e:
            messagebox.showerror("Erro", f"Erro ao adicionar membro: {e}")

    ttk.Button(add_gcrew_window, text="Adicionar", command=add_gcrew_member).pack(pady=20)
    ttk.Button(add_gcrew_window, text="Fechar", command=add_gcrew_window.destroy).pack(pady=10)

# Função para deletar membro da equipe
def open_delete_gcrew_window():
    delete_gcrew_window = Toplevel(GCrew_Page)
    delete_gcrew_window.title("Deletar Membro da Equipe de Manutenção")
    delete_gcrew_window.geometry("300x200")

    mechanics_id_var = IntVar()

    Label(delete_gcrew_window, text="ID do Membro:").pack(pady=10, anchor="w")
    Entry(delete_gcrew_window, textvariable=mechanics_id_var).pack(pady=5, fill="x")

    def delete_gcrew_member():
        mechanics_id = mechanics_id_var.get()

        if mechanics_id <= 0:
            messagebox.showerror("Erro", "Por favor, insira um ID válido.")
            return

        try:
            cursor = db_connection.cursor()
            query = "DELETE FROM Mechanics_TB WHERE Mechanics_ID = ?"
            cursor.execute(query, (mechanics_id,))
            if cursor.rowcount == 0:
                messagebox.showerror("Erro", "Nenhum membro encontrado com este ID.")
            else:
                db_connection.commit()
                messagebox.showinfo("Sucesso", "Membro deletado com sucesso!")
                load_gcrew_data()
            cursor.close()
        except pdbc.Error as e:
            messagebox.showerror("Erro", f"Erro ao deletar membro: {e}")

    ttk.Button(delete_gcrew_window, text="Deletar", command=delete_gcrew_member).pack(pady=20)
    ttk.Button(delete_gcrew_window, text="Fechar", command=delete_gcrew_window.destroy).pack(pady=10)

# Botões principais
ttk.Button(GCrew_Page, text="Atualizar Dados", command=load_gcrew_data).pack(pady=10)
ttk.Button(GCrew_Page, text="Adicionar Novo Membro", command=open_add_gcrew_page).pack(pady=10)
ttk.Button(GCrew_Page, text="Deletar Membro", command=open_delete_gcrew_window).pack(pady=10)
ttk.Button(GCrew_Page, text="Voltar ao Menu Principal", command=lambda: show_frame(main_menu)).pack(pady=10)
# Page 6
def load_location_data():
    for row in location_tree.get_children():
        location_tree.delete(row)

    # Chama dados do banco
    try:
        cursor = db_connection.cursor()
        query = """
        SELECT * FROM Serviced_Locations_TB
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        for row in rows:
            airport_id = row[0]
            airport_name = row[1]
            airport_loc = row[2]

            # Insere os dados formatados corretamente na Treeview
            location_tree.insert("", "end", values=(
                airport_id,
                airport_name,
                airport_loc
            ))

        cursor.close()
    except pdbc.Error as e:
        messagebox.showerror("Erro", f"Erro ao carregar dados dos locais: {e}")

columns = ("Airport_ID", "Airport_Name", "Airport_Loc")
location_tree = ttk.Treeview(Location_Page, columns=columns, show="headings")
location_tree.pack(pady=10, fill="both", expand=True)

# os nomes das colunas
location_tree.heading("Airport_ID", text="ID")
location_tree.heading("Airport_Name", text="Nome do Aeroporto")
location_tree.heading("Airport_Loc", text="Localização")

# Alinhamento e largura das colunas
location_tree.column("Airport_ID", width=100, anchor="center")
location_tree.column("Airport_Name", width=350, anchor="w")
location_tree.column("Airport_Loc", width=200, anchor="w")

# Abre a Janela para adicionar locais
def open_add_location_page():
    add_location_window = Toplevel(Location_Page)
    add_location_window.title("Adicionar Novo Local")
    add_location_window.geometry("400x400")

    # Variáveis para armazenar os dados para inserção na tabela
    id_var = StringVar()
    name_var = StringVar()
    loc_var = StringVar()

    # Labels e widgets
    Label(add_location_window, text="ID do Aeroporto (4 caracteres):").pack(pady=5, anchor="w")
    Entry(add_location_window, textvariable=id_var).pack(pady=5, fill="x")

    Label(add_location_window, text="Nome do Aeroporto:").pack(pady=5, anchor="w")
    Entry(add_location_window, textvariable=name_var).pack(pady=5, fill="x")

    Label(add_location_window, text="Localização:").pack(pady=5, anchor="w")
    Entry(add_location_window, textvariable=loc_var).pack(pady=5, fill="x")

    # Função para pegar os dados do formulário para inserção na tabela
    def add_location():
        airport_id = id_var.get()
        airport_name = name_var.get()
        airport_loc = loc_var.get()

        # valida os inputs
        if not airport_id or not airport_name or not airport_loc or len(airport_id) != 4:
            messagebox.showerror("Erro", "Por favor, preencha todos os campos corretamente.")
            return

        # Insere os dados no banco de dados
        try:
            cursor = db_connection.cursor()
            query = """
            INSERT INTO Serviced_Locations_TB (Airport_ID, Airport_Name, Airport_Loc)
            VALUES (?, ?, ?)
            """
            cursor.execute(query, (airport_id, airport_name, airport_loc))
            db_connection.commit()
            cursor.close()
            messagebox.showinfo("Sucesso", "Local adicionado com sucesso!")

            # apaga os dados anteriores para próxima inserção
            id_var.set("")
            name_var.set("")
            loc_var.set("")

            # Atualiza a tabela principal
            load_location_data()
        except pdbc.Error as e:
            messagebox.showerror("Erro", f"Erro ao adicionar local: {e}")

    # Botão para confirmar os dados para inserção
    ttk.Button(add_location_window, text="Adicionar Local", command=add_location).pack(pady=20)

    # botão para fechar a janela
    ttk.Button(add_location_window, text="Fechar", command=add_location_window.destroy).pack(pady=10)

# Abre a janela para remover locais
def open_delete_location_window():
    delete_location_window = Toplevel(Location_Page)
    delete_location_window.title("Deletar Local")
    delete_location_window.geometry("300x200")

    # Variável para o id a ser removido
    location_id_var = StringVar()

    Label(delete_location_window, text="ID do Local:").pack(pady=10, anchor="w")
    Entry(delete_location_window, textvariable=location_id_var).pack(pady=5, fill="x")

    # Função que executa a remoção dos dados
    def delete_location():
        airport_id = location_id_var.get()

        # valida input
        if not airport_id or len(airport_id) != 4:
            messagebox.showerror("Erro", "Por favor, insira um ID de local válido.")
            return

        # Tenta remover o dado do banco
        try:
            cursor = db_connection.cursor()
            query = "DELETE FROM Serviced_Locations_TB WHERE Airport_ID = ?"
            cursor.execute(query, (airport_id,))
            if cursor.rowcount == 0:
                messagebox.showerror("Erro", "Nenhum local encontrado com este ID.")
            else:
                db_connection.commit()
                messagebox.showinfo("Sucesso", "Local deletado com sucesso!")
                load_location_data()  # Atualiza os dados na tabela principal
            cursor.close()
        except pdbc.Error as e:
            messagebox.showerror("Erro", f"Erro ao deletar local: {e}")

    # Botão para confirmar o pedido de remoção
    ttk.Button(delete_location_window, text="Deletar Local", command=delete_location).pack(pady=20)

    ttk.Button(delete_location_window, text="Fechar", command=delete_location_window.destroy).pack(pady=10)

# Botão para atualizar dados
ttk.Button(Location_Page, text="Atualizar Dados", command=load_location_data).pack(pady=10)

# Botão para abrir a janela de adicionar locais
ttk.Button(Location_Page, text="Adicionar Novo Local", command=open_add_location_page).pack(pady=10)

# Botão para abrir a janela de remover locais
ttk.Button(Location_Page, text="Deletar Local", command=open_delete_location_window).pack(pady=10)

# botão para retornar ao menu principal
ttk.Button(Location_Page, text="Voltar ao Menu Principal", command=lambda: show_frame(main_menu)).pack(pady=10)


#Page 7
from tkinter import Toplevel, Label, Entry, StringVar, ttk, messagebox

def load_route_data():
    for row in route_tree.get_children():
        route_tree.delete(row)

    try:
        cursor = db_connection.cursor()
        query = """
        SELECT * FROM Routes_TB
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        for row in rows:
            route_id = row[0]
            route_origin = row[1]
            route_destination = row[2]
            route_alternate = row[3]

            route_tree.insert("", "end", values=(
                route_id,
                route_origin,
                route_destination,
                route_alternate
            ))

        cursor.close()
    except pdbc.Error as e:
        messagebox.showerror("Erro", f"Erro ao carregar dados das rotas: {e}")

columns = ("Route_ID", "Route_Origin", "Route_Destination", "Route_Alternate")
route_tree = ttk.Treeview(Route_Page, columns=columns, show="headings")
route_tree.pack(pady=10, fill="both", expand=True)

route_tree.heading("Route_ID", text="ID")
route_tree.heading("Route_Origin", text="Origem")
route_tree.heading("Route_Destination", text="Destino")
route_tree.heading("Route_Alternate", text="Alternativa")

route_tree.column("Route_ID", width=50, anchor="center")
route_tree.column("Route_Origin", width=100, anchor="center")
route_tree.column("Route_Destination", width=100, anchor="center")
route_tree.column("Route_Alternate", width=100, anchor="center")

def open_add_route_page():
    add_route_window = Toplevel(Route_Page)
    add_route_window.title("Adicionar Nova Rota")
    add_route_window.geometry("400x450")

    route_id_var = StringVar()
    origin_var = StringVar()
    destination_var = StringVar()
    alternate_var = StringVar()

    try:
        cursor = db_connection.cursor()
        cursor.execute("SELECT Airport_ID FROM Serviced_Locations_TB")
        airport_ids = [row[0] for row in cursor.fetchall()]
        cursor.close()
    except pdbc.Error as e:
        messagebox.showerror("Erro", f"Erro ao carregar aeroportos: {e}")
        return

    Label(add_route_window, text="ID da Rota:").pack(pady=5, anchor="w")
    Entry(add_route_window, textvariable=route_id_var).pack(pady=5, fill="x")

    Label(add_route_window, text="Origem:").pack(pady=5, anchor="w")
    origin_combobox = ttk.Combobox(add_route_window, textvariable=origin_var, values=airport_ids, state="readonly")
    origin_combobox.pack(pady=5, fill="x")

    Label(add_route_window, text="Destino:").pack(pady=5, anchor="w")
    destination_combobox = ttk.Combobox(add_route_window, textvariable=destination_var, values=airport_ids, state="readonly")
    destination_combobox.pack(pady=5, fill="x")

    Label(add_route_window, text="Alternativa:").pack(pady=5, anchor="w")
    alternate_combobox = ttk.Combobox(add_route_window, textvariable=alternate_var, values=airport_ids, state="readonly")
    alternate_combobox.pack(pady=5, fill="x")

    def add_route():
        route_id = route_id_var.get()
        origin = origin_var.get()
        destination = destination_var.get()
        alternate = alternate_var.get()

        if not route_id or not origin or not destination or not alternate:
            messagebox.showerror("Erro", "Por favor, preencha todos os campos.")
            return

        try:
            cursor = db_connection.cursor()
            query = """
            INSERT INTO Routes_TB (Route_ID, Route_Origin, Route_Destination, Route_Alternate)
            VALUES (?, ?, ?, ?)
            """
            cursor.execute(query, (route_id, origin, destination, alternate))
            db_connection.commit()
            cursor.close()
            messagebox.showinfo("Sucesso", "Rota adicionada com sucesso!")

            route_id_var.set("")
            origin_var.set("")
            destination_var.set("")
            alternate_var.set("")

            load_route_data()
        except pdbc.Error as e:
            messagebox.showerror("Erro", f"Erro ao adicionar rota: {e}")

    ttk.Button(add_route_window, text="Adicionar Rota", command=add_route).pack(pady=20)
    ttk.Button(add_route_window, text="Fechar", command=add_route_window.destroy).pack(pady=10)

def open_delete_route_page():
    delete_route_window = Toplevel(Route_Page)
    delete_route_window.title("Deletar Rota")
    delete_route_window.geometry("300x200")

    route_id_var = StringVar()

    Label(delete_route_window, text="ID da Rota:").pack(pady=10, anchor="w")
    Entry(delete_route_window, textvariable=route_id_var).pack(pady=5, fill="x")

    def delete_route():
        route_id = route_id_var.get()

        if not route_id:
            messagebox.showerror("Erro", "Por favor, insira um ID de rota válido.")
            return

        try:
            cursor = db_connection.cursor()
            query = "DELETE FROM Routes_TB WHERE Route_ID = ?"
            cursor.execute(query, (route_id,))
            if cursor.rowcount == 0:
                messagebox.showerror("Erro", "Nenhuma rota encontrada com este ID.")
            else:
                db_connection.commit()
                messagebox.showinfo("Sucesso", "Rota deletada com sucesso!")
                load_route_data()
            cursor.close()
        except pdbc.Error as e:
            messagebox.showerror("Erro", f"Erro ao deletar rota: {e}")

    ttk.Button(delete_route_window, text="Deletar Rota", command=delete_route).pack(pady=20)
    ttk.Button(delete_route_window, text="Fechar", command=delete_route_window.destroy).pack(pady=10)

ttk.Button(Route_Page, text="Atualizar Dados", command=load_route_data).pack(pady=10)
ttk.Button(Route_Page, text="Adicionar Nova Rota", command=open_add_route_page).pack(pady=10)
ttk.Button(Route_Page, text="Deletar Rota", command=open_delete_route_page).pack(pady=10)
ttk.Button(Route_Page, text="Voltar ao Menu Principal", command=lambda: show_frame(main_menu)).pack(pady=10)


#Inicializa conexão com o DB no inicio da aplicação
initialize_app()

# Start with the main menu
show_frame(main_menu)

# Run the application
root.mainloop()