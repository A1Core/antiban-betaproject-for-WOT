import time
import configparser
import shutil
import psutil
import threading
from tkinter import filedialog
import pyautogui
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
import requests
import subprocess
import zipfile
from logzero import logger as log
import customtkinter
import os
import win32gui


class App(customtkinter.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("blue")
        self.second = DYandUnzip()
        self.geometry("400x240")
        self.title("Automated CcleanerWOT")
        self.t1 = threading.Thread(target=self.removerandlocker)
        self.t2 = threading.Thread(target=self.mover)
        self.t3 = threading.Thread(target=self.startclass)
        self.button = customtkinter.CTkButton(self, text="Запуск тонков", command=self.t1.start)
        self.button.place(relx=0.5, rely=0.4, anchor="center")
        self.button4 = customtkinter.CTkButton(self, text="Подготовиться к обновлению тонков", command=self.t2.start)
        self.button4.place(relx=0.5, rely=0.6, anchor="center")
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.config_file = 'config.ini'
        self.progress_bar_1 = customtkinter.CTkProgressBar(self)
        self.button5 = customtkinter.CTkButton(self, text="Обновить модпак WotSpeak", command=self.t3.start)
        self.button5.place(relx=0.5, rely=0.8, anchor="center")

    def startclass(self):
        self.progress_bar_1.place(relx=0.5, rely=0.9, anchor="center")
        self.progress_bar_1.configure(mode="indeterminnate")
        self.progress_bar_1.start()
        self.second.downloader()
        self.second.unzip()
        self.progress_bar_1.stop()
        self.progress_bar_1.destroy()
    def removerandlocker(self):
        self.progress_bar_1.place(relx=0.5, rely=0.9, anchor="center")
        self.progress_bar_1.configure(mode="indeterminnate")
        self.progress_bar_1.start()

        if os.path.isfile(self.config_file):
            wgc_path = self.config['DEFAULT']['wgc_path']
            wot_path = self.config['DEFAULT']['wot_path']
        else:
            wot_path = filedialog.askdirectory()
            wgc_path = filedialog.askdirectory()
            self.config['DEFAULT'] = {'wgc_path': wgc_path, 'wot_path': wot_path}

            with open(self.config_file, 'w') as configfile:
                self.config.write(configfile)

        FILES_TO_LOCK = [
            "\screenshots",
            "\\replays",
            '\python.log',
            "\\python.log",
            "\win32\Reports",
            "\win32\Logs",
            "\win64\Reports",
            "\win64\Logs",
            "\win64\cef_browser_process.exe",
            "\win64\cef_subprocess.exe",
            "\win32\cef_browser_process.exe",
            "\win32\cef_subprocess.exe",
            "\win64\monitor_client_impl.dll",
            "\win32\monitor_client_impl.dll"

        ]
        FILES_TO_DELETE = [
            "\lgc_api.exe",
            "\win64\WargamingErrorMonitor.exe",
            "\win32\WargamingErrorMonitor.exe"

        ]
        MAKES_FILES = [
            "\python.log"
        ]
        CATALOGS_TO_DELETE = [
            "\\updates",
            "\\win32"
        ]
        CATALOGS_TO_CHECK = [
            "\win64\Reports",
            "\win64\Logs",
            "\screenshots",
            "\\replays"
        ]
        '''
            Проверка нужных каталогов,если нет-то создает и лочит
        '''
        for makes_files in MAKES_FILES:
            path_to_file1 = wot_path + makes_files
            if not os.path.exists(path_to_file1):
                print(f"Will make files{path_to_file1}")
                open(path_to_file1, "w")

        for catalogs_to_check in CATALOGS_TO_CHECK:
            path_to_file = wot_path + catalogs_to_check
            if not os.path.exists(path_to_file):
                print(f"Will make dirs{path_to_file}")
                os.mkdir(path_to_file)

        '''
            Deletes all files listed in FILES_TO_DELETE from game directory.
        '''
        for file_to_delete in FILES_TO_DELETE:
            path_to_file = wot_path + file_to_delete
            if os.path.isfile(path_to_file):
                for proc in psutil.process_iter():
                    try:
                        if proc.exe() == path_to_file:
                            proc.kill()
                    except:
                        continue
                print(f"Will remove {path_to_file}")
                os.remove(path_to_file)


        for proc in psutil.process_iter():
            if proc.name() in ["lgc_renderer_host.exe", "lgc.exe", "WargamingErrorMonitor.exe"]:
                proc.kill()

        if os.path.exists(wgc_path):
            try:
                subprocess.run(['cmd', '/C', 'rmdir', '/S', '/Q', wgc_path], check=True)
                print("Продолжаю")
            except subprocess.CalledProcessError as e:
                print(f"Произошла ошибка: {e}")
        else:
            print(f"Путь {wgc_path} не существует")


        for catalogs_to_delete in CATALOGS_TO_DELETE:
            path_to_file = wot_path + catalogs_to_delete
            if os.path.exists(path_to_file):
                shutil.rmtree(path_to_file, ignore_errors=True)

        user_sids = [user.name for user in psutil.users()]
        system_sids = ["SY", "BA", "AU", "BU"]
        for file_to_lock in FILES_TO_LOCK:
            path_to_file = wot_path + file_to_lock
            if not os.path.exists(path_to_file):
                continue
            for user_sid in user_sids:
                os.system(f"icacls {path_to_file} /deny {user_sid}:(f)")
            for system_sid in system_sids:
                os.system(f"icacls {path_to_file} /deny *{system_sid}:(f)")
        self.value1 = self.progress_bar_1.set(1)
        stop = self.progress_bar_1.stop()
        print("gotovo")
        if os.path.isfile(wot_path + "\win64\WorldOfTanks.exe"):
            subprocess.Popen(wot_path + "\win64\WorldOfTanks.exe")

        for proc in psutil.process_iter():
            if proc.name() in ["lgc_renderer_host.exe", "lgc.exe", "WargamingErrorMonitor.exe"]:
                proc.kill()

        os._exit(1)
    def mover(self):

        self.progress_bar_1.place(relx=0.5, rely=0.9, anchor="center")
        self.progress_bar_1.configure(mode="indeterminnate")
        self.progress_bar_1.start()

        if os.path.isfile(self.config_file):
            wgc_path = self.config['DEFAULT']['wgc_path']
            wot_path = self.config['DEFAULT']['wot_path']
        else:
            wot_path = filedialog.askdirectory()
            wgc_path = filedialog.askdirectory()
            self.config['DEFAULT'] = {'wgc_path': wgc_path, 'wot_path': wot_path}

            with open(self.config_file, 'w') as configfile:
                self.config.write(configfile)

        CATALOGS_TO_DELETE = [
            "\\res\scripts\client\gui\mods",
            "\mods",
            "\\res_mods"

        ]
        FILES_TO_UNLOCK = [

            "\\python.log",
            "\win64\cef_browser_process.exe",
            "\win64\cef_subprocess.exe",
            "\win64\monitor_client_impl.dll"
        ]
        CATALOGS_TO_UNLOCK = [
            "\screenshots",
            "\win64\Reports",
            "\win64\Logs",
            "\\replays"
        ]

        for proc in psutil.process_iter():
            if proc.name() in ["lgc_renderer_host.exe", "lgc.exe", "WargamingErrorMonitor.exe", "WorldOfTanks.exe"]:
                proc.kill()

        for catalogs_to_delete in CATALOGS_TO_DELETE:
            path_to_file = wot_path + catalogs_to_delete
            print(f"Will remove {path_to_file}")
            shutil.rmtree(path_to_file, ignore_errors=True)


        for catalogs_to_unlock in CATALOGS_TO_UNLOCK:
            path_to_file1 = wot_path + catalogs_to_unlock
            os.system(f"icacls {path_to_file1} /reset ")
            print(f"Unlock catalog {path_to_file1}")


        user_sids = [user.name for user in psutil.users()]
        system_sids = ["SY", "BA", "AU", "BU"]
        for file_to_unlock in FILES_TO_UNLOCK:
            path_to_file = wot_path + file_to_unlock
            if not os.path.exists(path_to_file):
                continue
            for user_sid in user_sids:
                os.system(f"icacls {path_to_file} /grant {user_sid}:(f)")
            for system_sid in system_sids:
                os.system(f"icacls {path_to_file} /grant *{system_sid}:(f)")
                print(f"Unlock {path_to_file}")

        self.value1 = self.progress_bar_1.set(1)
        self.progress_bar_1.stop()
        print(f"Теперь можно обновляться")
        os._exit(1)

class DYandUnzip:
    def __init__(self):
        self.url = "https://wotspeak.org/cheats/915-modpack-wotspeak.html"

    def downloader(self):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.text, 'html.parser')
        buttons = soup.find_all('a', class_='down_new')
        second_button = buttons[1]
        href = second_button['href']
        parsed_url = urlparse(href)
        xf_param = parse_qs(parsed_url.query)['xf'][0]
        result = subprocess.run(['python', 'downloaderyandex.py', f'{xf_param}'], stdout=subprocess.PIPE)
        print(result.stdout.decode())

    def set_foreground_window(self, window_title):
        window_title = "Установка"
        window_handle = win32gui.FindWindow(None, window_title)
        if window_handle != 0:
            win32gui.SetForegroundWindow(window_handle)
        else:
            print(f"Окно с заголовком {window_title} не найдено")

    def unzip(self):
        path = os.path.dirname(os.path.abspath(__file__)) + "\output"
        files = os.listdir(path)
        exe_file = files[0]
        zip_path = os.path.dirname(os.path.abspath(__file__)) + "/output/" + files[0]
        extract_path = os.path.dirname(os.path.abspath(__file__)) + "/output"
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
        log.info(f'Архив {zip_path} успешно разархивирован в папку {extract_path}')
        exe_files = [f.replace('.zip', '.exe') for f in files]
        exe_files1 = exe_files[0]
        subprocess.Popen(path + f"\{exe_files[0]}")
        done = False
        while not done:
            for proc in psutil.process_iter():
                if proc.name() == f"{exe_files1}":
                    log.info(f"Процесс {exe_files1} запущен")
                    time.sleep(5)
                    self.set_foreground_window("Установка")
                    pyautogui.moveTo(981, 572)
                    pyautogui.click(button='left', clicks=1)
                    time.sleep(5)
                    self.set_foreground_window("Установка")
                    pyautogui.moveTo(1008, 594)
                    pyautogui.click(button='left', clicks=1)
                    time.sleep(5)
                    self.set_foreground_window("Установка")
                    pyautogui.moveTo(1335, 792)
                    pyautogui.click(button='left', clicks=13)
                    pyautogui.moveTo(1184, 794)
                    time.sleep(15)
                    self.set_foreground_window("Установка")
                    pyautogui.click(button='left', clicks=1)
                    pyautogui.moveTo(1335, 792)
                    pyautogui.click(button='left', clicks=1)
                    psutil.wait_procs([proc])
                    log.info(f"Процесс {exe_files1} завершен")
                    done = True
                    break
            else:
                time.sleep(0.1)

        subprocess.run(['cmd', '/C', 'rmdir', '/S', '/Q', path], check=True)
        log.info("Обновление модпака завершено")
app = App()
x = (app.winfo_screenwidth() - app.winfo_reqwidth()) / 2 - 200
y = (app.winfo_screenheight() - app.winfo_reqheight()) / 2
app.wm_geometry("+%d+%d" % (x, y))
app.mainloop()
