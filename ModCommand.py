import hashlib
import os
import shutil

# The game directory
# Modify with the base directory of the game
base_game_path = ""

# The name of the log file used
log_filename = "ModCommand_Log.txt"

# The folder containing the mods to copy, organized as if its contents were inside base_game_path
base_mods_path = "mods"

# A folder to backup any game files overwritten
base_backup_path = "backup"

# The function to compute the SHA1 hash of a file
def compute_file_hash(filename):
    sha1 = hashlib.sha1()
    with open(filename, 'rb') as file:
        while True:
            data = file.read(65536)
            if not(data):
                break
            sha1.update(data)
    return sha1.hexdigest()

# The function to load files from base_mods_path to base_game_path
def load_files():
    # Check to see if mods have already been loaded
    if os.path.exists(os.path.join(base_game_path, log_filename)):
        if not(input("Mods detected, continue? (y/n) ") == 'y'):
            return
    with open(os.path.join(base_game_path, log_filename), 'w') as file:
        # Recursively go through each file in base_mods_path
        for dirpath, dirnames, filenames in os.walk(base_mods_path):
            # Set base_mods_path to be the root
            dirpath = dirpath[dirpath.find(base_mods_path) + len(base_mods_path) + 1:]

            # Loop through the files and inject them to base_game_path (respecting their path)
            for filename in filenames:
                # Compute the file path relative to the base_mods_path directory
                relative_filename = os.path.join(dirpath, filename)

                # Compute the target location using the relative path computed above
                absolute_filename = os.path.join(base_game_path, relative_filename)

                # Check to see if the file is overwriting a game file
                if os.path.exists(absolute_filename):
                    # Check to see if the files are the same and don't copy if they are
                    if compute_file_hash(absolute_filename) == compute_file_hash(os.path.join(base_mods_path, relative_filename)):
                        print(f"File {absolute_filename} already exists and matches mod file. Ignoring")
                        file.write(f"File {absolute_filename} already exists and matches mod file. Ignoring\r\n")
                        continue

                    # If so, compute the file's path in base_backup_path
                    backup_filename = os.path.join(base_backup_path, dirpath, filename)

                    print(f"File {absolute_filename} already exists, backing up to {backup_filename}")
                    file.write(f"File {absolute_filename} already exists, backing up to {backup_filename}\r\n")

                    # Compute the tree structure up to the file
                    backup_dirpath = os.path.join(base_backup_path, dirpath)

                    # Check to see if the path needs to be (recursively) created
                    if not(os.path.exists(backup_dirpath)):
                        os.makedirs(backup_dirpath)
                    
                    # Copy the game's file to base_backup_path (respecting the path)
                    shutil.copy(absolute_filename, backup_dirpath)
                print(f"Injecting mod file {relative_filename}")
                file.write(f"Injecting mod file {relative_filename}\r\n")

                # Inject the mod file
                shutil.copy(os.path.join(base_mods_path, dirpath, filename), absolute_filename)
            
            # Loop through the directories to make sure the target file paths can be copied to
            for dirname in dirnames:
                # Compute the directory path relative to base_mods_path
                relative_dirname = os.path.join(dirpath, dirname)

                # Compute the target path in base_game_path
                absolute_dirname = os.path.join(base_game_path, relative_dirname)
                
                # Check to see if the target path exists
                if not(os.path.exists(absolute_dirname)):
                    print(f"Creating mod folder {relative_dirname}")
                    file.write(f"Creating mod folder {relative_dirname}\r\n")

                    # If not, create it
                    os.makedirs(absolute_dirname)
# The function to remove mod files and replace with backup game files if necessary
def remove_files():
    # Check to see if mods have been loaded
    if not(os.path.exists(os.path.join(base_game_path, log_filename))):
        if not(input("Mods not detected, continue? (y/n) ") == 'y'):
            return
    # Loop through the files and directories bottom up so deleting folders works
    for dirpath, dirnames, filenames in os.walk(base_mods_path, topdown=False):
        # Set base_mods_path to be the root
        dirpath = dirpath[dirpath.find(base_mods_path) + len(base_mods_path) + 1:]

        # Loop through each file, delete it, and copy backup if applicable
        for filename in filenames:
            # Compute the file path relative to the base_mods_path directory
            relative_filename = os.path.join(dirpath, filename)

            # Compute the target location using the relative path computed above
            absolute_filename = os.path.join(base_game_path, relative_filename)

            # Compute the backup file path
            backup_filename = os.path.join(base_backup_path, dirpath, filename)

            # Check to see if the file actually exists before deleting then delete
            if os.path.exists(absolute_filename):
                print(f"Removing mod file {relative_filename}")
                os.remove(absolute_filename)
            
            # See if there is a backup game file and copy if it exists
            if os.path.exists(backup_filename):
                print(f"Replacing mod file {relative_filename} with game backup")
                shutil.copy(backup_filename, absolute_filename)
        
        # Loop through the directories, deleting all those that are empty
        for dirname in dirnames:
            # Compute the directory path relative to base_mods_path
            relative_dirname = os.path.join(dirpath, dirname)

            # Compute the target path in base_game_path
            absolute_dirname = os.path.join(base_game_path, relative_dirname)

            # Check to see if the backup folder exists
            if os.path.exists(os.path.join(base_backup_path, relative_dirname)):
                # If so, don't delete, probably contains game files in base_game_path
                continue
            
            # Check to see if the folder exists in base_game_path and delete if it does
            if os.path.exists(absolute_dirname):
                print(f"Removing mod folder {relative_dirname}")
                try:
                    os.rmdir(absolute_dirname)
                except OSError:
                    # Don't delete the folder if it is not empty, i.e. contains vanilla game files
                    print(f"Leaving folder {relative_dirname}")
    # Delete the log file created when the mods were injected if it exists
    if os.path.exists(os.path.join(base_game_path, log_filename)):
        os.remove(os.path.join(base_game_path, log_filename))

if __name__ == '__main__':
    yn = input("Load (l) or remove (r)? ")
    if yn == 'l':
        load_files()
        print("Done injecting files")
    elif yn == 'r':
        remove_files()
        print("Done removing files")