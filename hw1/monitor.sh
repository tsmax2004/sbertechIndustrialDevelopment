#!/bin/bash

# В этом файле хранится PID запущенного процесса
PIDFILE="monitor.pid"
# Директория для логов
LOGSDIR="logs"
# Интервал сбора информации (в секундах)
MONITOR_INTERVAL=30



# Цикл мониторинга
monitor() {
    mkdir -p "$LOGSDIR"

    # Время запуска мониторинга в формате YYYY.mm.dd_HHMMSS
    START_TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    NOW_DATE="0000.00.00" # для создания первого файла

    while true; do
        # Обрабатываем создание первого файла и новые сутки
        if [ "$NOW_DATE" != "$(date +"%Y.%m.%d")" ]; then
            NOW_DATE="$(date +"%Y.%m.%d")"
            LOGSFILE="$LOGSDIR/monitor_${START_TIMESTAMP}_${NOW_DATE}.csv"
            echo "Timestamp,Filesystem,MountOn,Capacity(%),FreeInodes,UsedInodes" >> "$LOGSFILE"
        fi

        df -P -h > /tmp/df_h.out
        df -P -i > /tmp/df_i.out

        NOW_TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

        tail -n +2 /tmp/df_h.out | while read -r line; do
            filesystem=$(echo $line | awk '{print $1}')
            mount_on=$(echo $line | awk '{print $6}')
            capacity=$(echo $line | awk '{print $5}')

            inodeLine=$(grep "^$filesystem " /tmp/df_i.out)
            freeInodes=$(echo $inodeLine | awk '{print $4}')
            usedInodes=$(echo $inodeLine | awk '{print $3}')

            echo "$NOW_TIMESTAMP,$filesystem,$mount_on,$capacity,$freeInodes,$usedInodes" >> "$LOGSFILE"
        done

        rm -f /tmp/df_h.out /tmp/df_i.out

        sleep $MONITOR_INTERVAL
    done
}

if [ -z "$1" ]; then
    echo "Usage: $0 {START|STOP|STATUS}"
    exit 1
fi

case "$1" in
    START)
        if [ -f "$PIDFILE" ]; then
            PID=$(cat "$PIDFILE")
            if ps -p $PID > /dev/null; then
                echo "Monitoring is already running: PID=$PID"
                exit 1
            else
                rm "$PIDFILE"
            fi
        fi


        monitor &

        PID=$!
        echo $PID > "$PIDFILE"
        echo "Monitoring is running: PID=$PID"
        ;;

    STATUS)
        if [ -f "$PIDFILE" ]; then
            PID=$(cat "$PIDFILE")
            if ps -p $PID > /dev/null; then
                echo "Monitoring is running: PID=$PID"
                exit 0
            fi
        fi

        echo "Monitoring is not running"
        ;;

    STOP)
        if [ -f "$PIDFILE" ]; then
            PID=$(cat "$PIDFILE")
            if ps -p $PID > /dev/null; then
                kill $PID
                rm "$PIDFILE"
                echo "Monitoring with PID=$PID has been stopped"
                exit 0
            else
                rm "$PIDFILE"
            fi
        fi

        echo "Monitoring is not running"
        ;;

    *)
        echo "Usage: $0 {START|STOP|STATUS}"
        exit 1
        ;;
esac