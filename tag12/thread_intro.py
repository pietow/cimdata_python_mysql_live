import threading
import time

def notice(name:str):
    print("Start:", name)
    time.sleep(0.4)  # Nur der ausführende Thread wartet: 0.4s
    print("Fertig:", name)

def main():
    room = threading.Thread(target=notice, args=("Raumhinweis",))
    materials = threading.Thread(target=notice, args=("Materialhinweis",))


    room.start()
    materials.start()  # starte sein Ausführung
    room.join()
    materials.join()   # Lässt den aufrufenden Thread auf sein Ende warten


if __name__ == "__main__":
    main()