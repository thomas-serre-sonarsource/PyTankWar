import multiprocessing
import subprocess  # Still useful for the actual execution

def run_process(script_path):
    try:
        subprocess.run(['python', script_path], check=True)
        print(f"Process for {script_path} finished.")
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_path}: {e}")
    except FileNotFoundError:
        print(f"Error: Script not found at {script_path}")
    except Exception as e:
        print(f"An error occurred while running {script_path}: {e}")

if __name__ == "__main__":
    game_script_path = "logic/game.py"
    server_script_path = "server/server.py"
    drawer_script_path = "drawer/game_drawer.py"
    ai_script_path = "ai/ai_player.py"
    
    processes = []
    for script in [game_script_path, server_script_path, drawer_script_path, ai_script_path]:
        process = multiprocessing.Process(target=run_process, args=(script,))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()  # Wait for all processes to complete (optional)

    print("All processes completed.")