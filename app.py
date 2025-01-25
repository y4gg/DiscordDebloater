import requests, time, sys, pwinput, os, json

def config():
    if not os.path.exists("config.json"):
        dc_token = pwinput.pwinput(prompt="Discord Token: ")
    else:
        with open("config.json", "r") as f:
            config = json.load(f)
            dc_token = config["dc_token"]
    return dc_token

dc_token = config()

headers = {
    "Authorization": dc_token
}

def get_servers():
    try:
        url = "https://discordapp.com/api/users/@me/guilds"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        guilds_data = response.json()
        server_ids = [guild["id"] for guild in guilds_data]
        server_names = [guild["name"] for guild in guilds_data]
        
        print("Successfully fetched server IDs and names.")
        return server_ids, server_names
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return [], []

def mute_server(server_id, server_name):
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
        return(f"Successfully muted {server_name} ({server_id})")
    except requests.exceptions.RequestException as e:
        return(f"Error muting server {server_name} ({server_id}): {e}")

def mute_all(server_ids, server_names):
    total = len(server_ids)
    start_time = time.time()
    last_text_length = 0
    
    for i, (server_id, server_name) in enumerate(zip(server_ids, server_names), 1):
        status = mute_server(server_id, server_name)
        
        progress = i / total
        bar_length = 40
        block = int(round(bar_length * progress))

        elapsed_time = time.time() - start_time
        avg_time_per_item = elapsed_time / i
        remaining_time = avg_time_per_item * (total - i)

        text = f"\rProgress: [{'#' * block + '-' * (bar_length - block)}] {i}/{total} | Time left: {remaining_time:.1f}s > {status}"

        if len(text) < last_text_length:
            text += ' ' * (last_text_length - len(text))

        last_text_length = len(text)
        
        sys.stdout.write(text)
        sys.stdout.flush()
        time.sleep(1)
    print()

def prompt_mute_servers():
    server_ids, server_names = get_servers()
        
    for name, server_id in zip(server_names, server_ids):
        name = name.strip()
        server_id = server_id.strip()
        
        while True:
            response = input(f"Do you want to mute {name}? (y)es / (n)o / (a)ll: ").lower()
            
            if response in ['y', 'yes']:
                mute_server(server_id, name)
                break
            elif response in ['n', 'no']:
                break
            elif response in ['a', 'all']:
                mute_all(server_ids, server_names)
                return
            else:
                print("Invalid input. Please enter y/yes, n/no, or a/all")

prompt_mute_servers()
