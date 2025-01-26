import requests, time, sys, pwinput, os, json

def config():
    if not os.path.exists("config.json"):
        config = {"accounts": []}
    else:
        with open("config.json", "r") as f:
            config = json.load(f)
    
    if not config.get("accounts"):
        account_name = input("Enter account name: ").strip()
        dc_token = pwinput.pwinput(prompt="Discord Token: ")
        config["accounts"] = [{"name": account_name, "dc_token": dc_token}]
        with open("config.json", "w") as f:
            json.dump(config, f, indent=4)
        return dc_token
    
    # Account selection
    print("\nAvailable accounts:")
    for i, account in enumerate(config["accounts"], 1):
        print(f"{i}. {account['name']}")
    print("n. Add new account")
    
    while True:
        choice = input("Select account (number) or 'n' for new: ").strip().lower()
        
        if choice == 'n':
            account_name = input("Enter account name: ").strip()
            dc_token = pwinput.pwinput(prompt="Discord Token: ")
            config["accounts"].append({"name": account_name, "dc_token": dc_token})
            with open("config.json", "w") as f:
                json.dump(config, f, indent=4)
            return dc_token
        elif choice.isdigit() and 0 < int(choice) <= len(config["accounts"]):
            selected = config["accounts"][int(choice) - 1]
            return selected["dc_token"]
        else:
            print("Invalid selection. Please try again.")

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
            response = input(f"Do you want to mute {name}? (y)es / (n)o / (a)ll / (c)ancel: ").lower()
            
            if response in ['y', 'yes']:
                mute_server(server_id, name)
                break
            elif response in ['n', 'no']:
                break
            elif response in ['a', 'all']:
                mute_all(server_ids, server_names)
                return
            elif response in ['c', 'cancel']:
                actions()
                break
            else:
                print("Invalid input. Please enter y/yes, n/no, or a/all")

def prompt_leave_servers():
    server_ids, server_names = get_servers()
    
    for name, server_id in zip(server_names, server_ids):
        name = name.strip()
        server_id = server_id.strip()
        
        while True:
            response = input(f"Do you want to leave {name}? (y)es / (n)o / (a)ll / (c)ancel: ").lower()
            
            if response in ['y', 'yes']:
                leave_server(server_id, name)
                break
            elif response in ['n', 'no']:
                break
            elif response in ['a', 'all']:
                leave_all(server_ids, server_names)
                return
            elif response in ['c', 'cancel']:
                return
            else:
                print("Invalid input. Please enter y/yes, n/no, a/all, or c/cancel")

def leave_server(server_id, server_name):
    url = "https://discord.com/api/v9/users/@me/guilds/" + server_id
    payload = {
        "lurking": False
    }
    
    try:
        response = requests.delete(url, headers=headers, json=payload)
        response.raise_for_status()
        return(f"Successfully left {server_name} ({server_id})")
    except requests.exceptions.RequestException as e:
        return(f"Error leaving server {server_name} ({server_id}): {e}")

def leave_all(server_ids, server_names):
    total = len(server_ids)
    start_time = time.time()
    last_text_length = 0
    
    for i, (server_id, server_name) in enumerate(zip(server_ids, server_names), 1):
        status = leave_server(server_id, server_name)
        
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

def select_mode():
    print("\n\n")
    print("Mute Dbloader\n")
    print("Select mode:")
    print("1. Actions")
    print("2. Stats")
    print("3. Account Selector")
    print("4. Exit")
    
    while True:
        mode = input("Enter mode: ").strip().lower()

        if mode in ['1', 'actions']:
            actions()
            break
        elif mode in ['2', 'stats']:
            stats()
            break
        elif mode in ['3', 'config']:
            config()
            break
        elif mode in ['4', 'exit']:
            print("Exiting...")
            break
        else:
            print("Invalid input. Please enter 1/actions, 2/stats, 3/config, or 4/exit")

def stats():
    server_ids, server_names = get_servers()
    print("\nYour servers:")
    for i, name in enumerate(server_names, 1):
        print(f"{i}. {name}")
    print()
    input("Press enter to leave...")
    select_mode()

def actions():
    print("1. Mute servers")
    print("2. Leave Servers")
    print("3. Back")

    while True:
        action = input("Enter action: ").strip().lower()

        if action in ['1', 'mute servers']:
            prompt_mute_servers()
            break
        elif action in ['2', 'leave servers']:
            prompt_leave_servers()
            break
        elif action in ['3', 'back']:
            select_mode()
            break
        else:
            print("Invalid input. Please enter 1/mute servers, 2/leave servers, or 3/back")

select_mode()
