import requests, time

# token
dc_token = input("Enter your Discord token: ")

headers = {
    "Authorization": dc_token
}

def get_server_ids():
    try:

        url = "https://discordapp.com/api/users/@me/guilds"

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        

        guilds_data = response.json()
        server_ids = [guild["id"] for guild in guilds_data]
        server_names = [guild["name"] for guild in guilds_data]

        with open("server_ids.txt", "w") as f:
            for server_id in server_ids:
                f.write(f"{server_id}\n")

        with open("server_names.txt", "w", encoding="utf-8") as f:
            for server_name in server_names:
                f.write(f"{server_name}\n")
            
        print("Successfully fetched server IDs and names.")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")

def mute_server(server_id):
    url = "https://discord.com/api/v9/users/@me/guilds/settings"
    payload = {
        "guilds": {
            server_id: {
                "muted": True,
                "mute_config": {
                    "selected_time_window": -1,
                    "end_time": None
                }
            }
        }
    }
    
    try:
        response = requests.patch(url, headers=headers, json=payload)
        response.raise_for_status()
        print(f"Successfully muted server {server_id}")
    except requests.exceptions.RequestException as e:
        print(f"Error muting server {server_id}: {e}")

def mute_all():
    with open("server_ids.txt", "r") as f:
        server_ids = [line.strip() for line in f]
        
    for server_id in server_ids:
        mute_server(server_id)
        time.sleep(1)

def prompt_mute_servers():
    with open("server_names.txt", "r", encoding="utf-8") as names_file, \
         open("server_ids.txt", "r") as ids_file:
        server_names = names_file.readlines()
        server_ids = ids_file.readlines()
        
        for name, server_id in zip(server_names, server_ids):
            name = name.strip()
            server_id = server_id.strip()
            
            while True:
                response = input(f"Do you want to mute {name}? (y)es / (n)o / (a)ll: ").lower()
                
                if response in ['y', 'yes']:
                    mute_server(server_id)
                    break
                elif response in ['n', 'no']:
                    break
                elif response in ['a', 'all']:
                    mute_all()
                    return
                else:
                    print("Invalid input. Please enter y/yes, n/no, or a/all")

get_server_ids()
prompt_mute_servers()