#!/bin/bash

# Define constants

list_all_process() {
    ps -fea | grep gunicorn
}

purge_fragments() {
    echo "Removing all hls fragments.. Are you sure? (y/n)"
    read -r answer
    case $answer in
        y|Y)
            rm -rf /tmp/hls/*
            echo "Done."
            ;;
        n|N)
            echo "Operation cancelled."
            ;;
        *)
            echo "Invalid input. Operation cancelled."
            ;;
    esac
    pause_prompt
}
pause_prompt() {
    echo "Press Enter to continue..."
    read
}
# Define functions
start_app() {
    echo "Starting app..."
    ./start_app.sh
    sleep 3
    echo "Done, current running processes:"
    list_all_process
    echo "Press Enter to continue..."
    read
}

stop_app() {
    echo "Stopping app..."
    pkill -9 gunicorn
    pkill -9 python
    sleep 2
    list_all_process
    echo "Stopped..."
}

restart_app() {
    echo "Restarting app..."
    stop_app
    start_app
}

tail_fragment_dir() {
    echo "Current files:"
    ls -rtl /tmp/hls| tail -10
    pause_prompt
}

watch_process() {
    echo "Current running process"
    list_all_process
    pause_prompt
}

watch_live_logs() {
	tail -f ./logs/flask_app.log
}

toggle_maintenance_file() {
    directory="/usr/share/nginx/html"
    maintenance_file="$directory/maintenance_off.html"
    under_maintenance_file="$directory/under_maintenance.html"

    if [ -f "$maintenance_file" ]; then
        mv "$maintenance_file" "$under_maintenance_file"
        echo "Maintenance mode ON"
	pause_prompt
    elif [ -f "$under_maintenance_file" ]; then
        mv "$under_maintenance_file" "$maintenance_file"
	echo "Maintenance mode OFF"
	pause_prompt
    else
	echo "Problem locating the maintenance file!"
	pause_prompt
    fi
}

# Main loop
while true
do
    clear
    echo "======================"
    echo "== EnfoqueLive v1.0 =="
    echo "======================"
    echo "1. Start Application"
    echo "2. Stop Application"
    echo "3. Restart Application"
    echo "4. Toggle maintenance"
    echo "5. Watch Process"
    echo "6. Watch app logs"
    echo "-----------------"
    echo "7. Purge stream fragments"
    echo "8. Tail fragments dir"
    echo "9. Exit"
    echo -n "Enter your choice: "
    read choice

    case $choice in
        1) start_app ;;
        2) stop_app ; pause_prompt;;
        3) restart_app ;;
	4) toggle_maintenance_file ;;
        5) watch_process ;;
        6) watch_live_logs ;;
        7) purge_fragments ;;
        8) tail_fragment_dir ;;
        9) exit 0 ;;
        *) echo "Invalid choice. Please choose a valid option." ;;
    esac
done
