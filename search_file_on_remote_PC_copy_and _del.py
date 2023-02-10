import os.path
import os
import subprocess
from pathlib import Path
import shutil
import glob
import time
import platform

def folderSize(path):
    fsize = 0
    for file in Path(path).rglob('*'):
        if (os.path.isfile(file)):
            fsize += os.path.getsize(file)
    return fsize

def get_time_now():
    return time.strftime("%d.%m.%Y %H:%M:%S")

def pingPc(ip_host):
    oc = platform.system()
    if (oc == "Windows"):
        ping_com = "ping -n 1 "
    else:
        ping_com = "ping -c 1 "
    comm = ping_com + ip_host
    response = os.popen(comm)
    data_request = response.readlines()
    for line in data_request:
        if 'TTL' in line:
            print(f"Host: {ip_host} - Ping Ok")
            #Пишем в лог
            with open("testlogs.txt", "a") as file_log:
                file_log.write(f"{get_time_now()} Host: {ip_host} - Ping OK\n")
            return True
            break
        else:
            continue                    
        print(f"Host: {ip_host} - Ping False")
        #Пишем в лог
        with open("testlogs.txt", "a") as file_log:
            file_log.write(f"{get_time_now()} Host: {ip_host} - Ping False")
        return False
         
#Шаблон для поиска
search_str = input("Слово для поиска: ")
#Список проверяемых дисков
disk_list = ['c', 'd', 'e', 'f', 'g', 'h', 'k', 'l', 'o', 'p']
#Переменная для сохранения размера найденных файлов
summa = 0
#хранит название найденной папки, для которой был почитан размер
folder = ""

with open("testlogs.txt", "a") as file_log:
    file_log.write(f"{get_time_now()} Поиск начался\n")

#Читаем файл со списком ПК на которых будет поиск по шаблону
with open ('servers.txt', 'r') as file_srv:
    list_srv = file_srv.readlines()
    for pc in list_srv:
        #удаляем лишние пробелы если они есть в строке
        pc = pc.replace(" ","")
        #Если строка не закоменчена, то работаем с ней
        if not pc.startswith('#'):
            pc = pc.rstrip('\n')
            if(pingPc(pc)):
                for disk in disk_list:
                    path_s = f'\\\{pc}\\{disk}$\\**\\*{search_str}*'
                    print(path_s)
                    for path in glob.iglob(path_s, recursive=True):
                        print(path)
                        with open(f'search_list_py_{search_str}.txt','a') as fsearch:
                            fsearch.write(f'{path}\n')
                        with open(f'search_size_py_{search_str}.csv','a') as f2:
                            try:
                                #размер каталога
                                if (os.path.isdir(path)):
                                    size = folderSize(path)
                                    res_f2 = f"{size};{path}\n"
                                    f2.write(res_f2)
                                    print(f'Размер папки вычислен: {size}')
                                    folder = str(path[path.rfind('\\')+1:])
                                    summa+=int(size)
                                #размер файла
                                else:
                                    size = str(os.path.getsize(path))
                                    res_f2 = f"{size};{path}\n"
                                    f2.write(res_f2)
                                    print(f'Размер файла вычислен: {size}')
                                    if not (folder in path and folder != ""):
                                        summa+=int(size)

                                #если путь = директория
                                if (os.path.isdir(path)):
                                    dst = f'D:\\xcopy_{search_str}' + path
                                    if not(os.path.isdir(dst)):
                                        os.makedirs(dst)
                                        print("Папка создана")
                                    else:
                                        print("Папка существует")
                                    dst3 = f'D:\\xcopy_{search_str}' + path
                                    cmd = f"robocopy \"{path}\" \"{dst3}\" /E /Z /R:3 /W:5"
                                    subprocess.call(cmd)
                                    #удаление папки и ее содержимого (Раскомментировать, если требуется удаление на удаленном хосте после копирования)
                                    #shutil.rmtree(path)
                                    #print('Папка удалена!')
                                #если путь = файл
                                else:    
                                    dst2 = f'D:\\xcopy_{search_str}'+str(path[:path.rfind('\\')])
                                    if not(os.path.isdir(dst2)):
                                        os.makedirs(dst2)
                                        print("Папка создана")
                                    else:
                                        print("Папка существует")
                                    shutil.copy2(path, dst2)
                                    #удаление файла (Раскомментировать, если требуется удаление на удаленном хосте после копирования)
                                    #os.remove(path)
                                    #print('Файл удален!')
                            except:
                                print(f'Не доступен сетевой путь: {line}')
                                with open(f'search_not_available_py_{search_str}.csv','a') as f3:
                                    f3.write(f'Не доступен сетевой путь;{path}\n')
    print(f'{summa} Bytes')
    print(f'{summa/1048576} Mb')
    print(f'{summa/1073741824} Gb')
    with open(f'search_size_py_{search_str}.csv','a') as f2:
        f2.write(f'\n{summa} Bytes\n')
        f2.write(f'{summa/1048576} Mb\n')
        f2.write(f'{summa/1073741824} Gb')
with open("testlogs.txt", "a") as file_log:
    file_log.write(f"{get_time_now()} Поиск завершен\n")
